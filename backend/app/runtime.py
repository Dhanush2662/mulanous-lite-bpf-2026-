"""One-process orchestration: load, assemble, decide, plan, approve, execute."""

from __future__ import annotations

import threading
from pathlib import Path

from app.actions.executor import SyntheticSession, apply_stored_plan
from app.actions.planner import build_action_plan
from app.adapters.sources import load_workspace
from app.context.assembler import filter_evidence, hybrid_retrieve
from app.errors import AppError
from app.evidence.embeddings import build_embedder
from app.evidence.normalize import build_case_records, normalize_evidence
from app.evidence.store import EvidenceStore, prepare_store
from app.investigate.answer import answer_question
from app.logging_config import get_logger
from app.reasoning.decision_agent import DecisionAgent
from app.reasoning.provider import DecisionProvider
from app.schemas.models import (
    ActionPlan,
    ActionResult,
    AnalyzeResponse,
    AssembledContext,
    Case,
    CaseRecord,
    EvidenceRecord,
    InvestigateResponse,
)

logger = get_logger(__name__)


class Runtime:
    def __init__(
        self,
        data_dir: Path,
        provider: DecisionProvider,
        packs_dir: Path | None = None,
        *,
        use_atlas: bool | None = None,
        force_fake_embeddings: bool = False,
    ) -> None:
        pack_dirs = [packs_dir / "manufacturing"] if packs_dir else []
        loaded = load_workspace(data_dir, pack_dirs)
        evidence = normalize_evidence(loaded)
        self.embedder = build_embedder(force_fake=force_fake_embeddings)
        prepared = prepare_store(
            evidence,
            loaded.cases,
            self.embedder,
            use_atlas=use_atlas,
        )
        self.store: EvidenceStore = prepared.store
        self._cases = {
            case.id: case for case in build_case_records(prepared.cases, prepared.evidence)
        }
        self._order = list(self._cases)
        self._agent = DecisionAgent(provider)
        self._session = SyntheticSession()
        self._analyses: dict[str, AnalyzeResponse] = {}
        self._plans: dict[str, ActionPlan] = {}
        self._executed: set[str] = set()
        self._lock = threading.Lock()
        self.source_status = loaded.statuses
        logger.info(
            "startup cases=%s evidence=%s sources=%s provider=%s store=%s embedder=%s",
            len(self._order),
            len(evidence),
            self.source_status,
            provider.name,
            self.store.name,
            self.embedder.name,
        )

    def list_cases(self) -> list[Case]:
        return [self._public(self._cases[case_id]) for case_id in self._order]

    def get_case(self, case_id: str) -> Case:
        return self._public(self._require_case(case_id))

    def list_case_evidence(
        self,
        case_id: str,
        source: str | None = None,
        query: str | None = None,
    ) -> list[EvidenceRecord]:
        case = self._require_case(case_id)
        assembled = self._assemble(case)
        return filter_evidence(assembled, source, query)

    def get_evidence(self, evidence_id: str) -> EvidenceRecord:
        found = self.store.get(evidence_id)
        if found is None:
            raise AppError(404, "Unknown evidence")
        return found.record

    def analyze(self, case_id: str) -> AnalyzeResponse:
        case = self._require_case(case_id)
        context = self._context(case)
        response = self._agent.decide(context)
        with self._lock:
            case.disposition = response.decision
            self._analyses[case.id] = response
        return response

    def plan(self, case_id: str) -> ActionPlan:
        case = self._require_case(case_id)
        with self._lock:
            analysis = self._analyses.get(case.id)
            if analysis is None:
                raise AppError(400, "Analyze the case before planning an action")
            plan = build_action_plan(analysis, self._public(case), self._session.snapshot())
            self._plans[plan.plan_id] = plan
            self._save_action(plan, status="planned", after_state=None)
            if not plan.requires_approval:
                self._apply_low_risk(plan)
            return plan.model_copy(deep=True)

    def execute(self, plan_id: str, approved: bool | None) -> ActionResult:
        if approved is not True:
            raise AppError(400, "Approval is required before execution")
        with self._lock:
            plan = self._plans.get(plan_id)
            if plan is None:
                raise AppError(404, "Unknown plan")
            if plan_id in self._executed:
                raise AppError(409, "Plan already executed")
            result = apply_stored_plan(plan, self._session)
            self._executed.add(plan_id)
            self._mark_executed(plan)
            self._save_action(plan, status="executed", after_state=result.after_state)
            return result

    def investigate(self, case_id: str, message: str) -> InvestigateResponse:
        case = self._require_case(case_id)
        assembled = self._assemble(case)
        catalog = {
            item.record.id: item.record
            for item in self.store.all_evidence()
            if item.account_id == case.account_id
        }
        with self._lock:
            stored = self._analyses.get(case.id)
            stored_copy = stored.model_copy(deep=True) if stored else None
        return answer_question(
            case=self._public(case),
            assembled=assembled,
            catalog=catalog,
            message=message,
            stored_analysis=stored_copy,
            reanalyze=lambda: self.analyze(case.id),
            refresh_case=lambda: self._public(self._require_case(case.id)),
        )

    def _context(self, case: CaseRecord) -> AssembledContext:
        return AssembledContext(
            case_id=case.id,
            domain=case.domain,
            pattern=case.pattern,
            account=case.account,
            claim=case.claim,
            urgency=case.urgency,
            evidence=self._assemble(case),
        )

    def _assemble(self, case: CaseRecord) -> list[EvidenceRecord]:
        return hybrid_retrieve(
            self.store,
            account_id=case.account_id,
            domain=case.domain,
            claim=case.claim,
            embedder=self.embedder,
        )

    def _apply_low_risk(self, plan: ActionPlan) -> None:
        result = apply_stored_plan(plan, self._session)
        self._executed.add(plan.plan_id)
        for step in plan.steps:
            if step.tool != "dismiss_resolved":
                continue
            stored = self._cases.get(step.args.get("case_id", plan.case_id))
            if stored is not None:
                stored.queue_status = "dismissed"
        self._save_action(plan, status="executed", after_state=result.after_state)

    def _mark_executed(self, plan: ActionPlan) -> None:
        if not plan.steps or not plan.requires_approval:
            return
        stored = self._cases.get(plan.case_id)
        if stored is not None:
            stored.last_action_status = "executed"

    def _save_action(
        self,
        plan: ActionPlan,
        *,
        status: str,
        after_state: object,
    ) -> None:
        document = {
            "plan_id": plan.plan_id,
            "case_id": plan.case_id,
            "status": status,
            "requires_approval": plan.requires_approval,
            "steps": [step.model_dump() for step in plan.steps],
            "before_state": plan.before_state.model_dump(),
            "after_state": after_state.model_dump() if hasattr(after_state, "model_dump") else None,
        }
        try:
            self.store.save_action(document)
        except Exception as exc:
            logger.error("action_save state=skipped error_type=%s", type(exc).__name__)

    def _require_case(self, case_id: str) -> CaseRecord:
        case = self._cases.get(case_id)
        if case is None:
            raise AppError(404, "Unknown case")
        return case

    def _public(self, case: CaseRecord) -> Case:
        return Case(
            id=case.id,
            domain=case.domain,
            pattern=case.pattern,
            account=case.account,
            claim=case.claim,
            urgency=case.urgency,
            source_count=case.source_count,
            disposition=case.disposition,
            queue_status=case.queue_status,
            last_action_status=case.last_action_status,
        )
