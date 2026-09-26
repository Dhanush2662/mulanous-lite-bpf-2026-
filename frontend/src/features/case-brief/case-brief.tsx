"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  analyzeCase,
  errorMessage,
  getCase,
  isAbortError,
} from "@/api/client";
import { MetaLabel } from "@/components/meta-label";
import { StatusNotice } from "@/components/status-notice";
import { Button } from "@/components/ui/button";
import { AnalysisProgress } from "@/features/case-brief/analysis-progress";
import { EvidenceInspector } from "@/features/case-brief/evidence-inspector";
import { InvestigateDrawer } from "@/features/case-brief/investigate-drawer";
import { TakeActionDrawer } from "@/features/case-brief/take-action-drawer";
import {
  challengeLabel,
  patternLabel,
  queueStatusLabel,
  sourceLabel,
} from "@/lib/labels";
import type { AnalyzeResponse, Case, Disposition, EvidenceRecord } from "@/types/api";

export function CaseBrief({ caseId }: { caseId: string }) {
  const [caseRecord, setCaseRecord] = useState<Case | null>(null);
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [caseError, setCaseError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [loadingCase, setLoadingCase] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [inspectedId, setInspectedId] = useState<string | null>(null);
  const [investigateOpen, setInvestigateOpen] = useState(false);
  const [actionOpen, setActionOpen] = useState(false);

  const refreshCase = useCallback(() => {
    getCase(caseId)
      .then(setCaseRecord)
      .catch((error: unknown) => {
        if (!isAbortError(error)) {
          setCaseError(errorMessage(error));
        }
      });
  }, [caseId]);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    async function load() {
      setLoadingCase(true);
      setAnalyzing(false);
      setCaseError(null);
      setAnalysisError(null);
      setAnalysis(null);
      setCaseRecord(null);

      try {
        const loaded = await getCase(caseId, controller.signal);
        if (!active) {
          return;
        }
        setCaseRecord(loaded);
      } catch (error) {
        if (!active || isAbortError(error)) {
          return;
        }
        setCaseError(errorMessage(error));
        setLoadingCase(false);
        return;
      }

      setLoadingCase(false);
      setAnalyzing(true);

      try {
        const result = await analyzeCase(caseId, controller.signal);
        if (!active) {
          return;
        }
        setAnalysis(result);
      } catch (error) {
        if (!active || isAbortError(error)) {
          return;
        }
        setAnalysisError(errorMessage(error));
        setAnalyzing(false);
        return;
      }

      setAnalyzing(false);

      try {
        const refreshed = await getCase(caseId, controller.signal);
        if (active) {
          setCaseRecord(refreshed);
        }
      } catch (error) {
        if (!active || isAbortError(error)) {
          return;
        }
      }
    }

    void load();
    return () => {
      active = false;
      controller.abort();
    };
  }, [caseId, attempt]);

  const evidence = analysis?.evidence ?? [];
  const inspected =
    evidence.find((record) => record.id === inspectedId) ?? null;

  return (
    <div>
      <Link
        href="/"
        className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]"
      >
        ATTENTION TODAY
      </Link>

      {loadingCase ? (
        <div className="mt-6">
          <StatusNotice title="Loading the case." />
        </div>
      ) : null}

      {caseError ? (
        <div className="mt-6">
          <StatusNotice
            alert
            title="This case could not be opened."
            detail={caseError}
            onRetry={() => setAttempt((current) => current + 1)}
          />
        </div>
      ) : null}

      {caseRecord ? (
        <CaseHeader caseRecord={caseRecord} />
      ) : null}

      <AnalysisProgress active={analyzing} />

      {analysisError ? (
        <div className="mt-6">
          <StatusNotice
            alert
            title="Analysis did not complete."
            detail={analysisError}
            onRetry={() => setAttempt((current) => current + 1)}
          />
        </div>
      ) : null}

      {analysis ? (
        <DecisionBody
          analysis={analysis}
          onInspect={setInspectedId}
          onInvestigate={() => setInvestigateOpen(true)}
          onTakeAction={() => setActionOpen(true)}
          onRunAgain={() => setAttempt((current) => current + 1)}
        />
      ) : null}

      <EvidenceInspector
        evidenceId={inspectedId}
        fallback={inspected}
        onOpenChange={(open) => {
          if (!open) {
            setInspectedId(null);
          }
        }}
      />
      <InvestigateDrawer
        open={investigateOpen}
        caseId={caseId}
        decision={analysis?.decision ?? caseRecord?.disposition ?? null}
        onOpenChange={setInvestigateOpen}
        onInspect={setInspectedId}
        onReanalyzed={() => setAttempt((current) => current + 1)}
      />
      <TakeActionDrawer
        open={actionOpen}
        caseId={caseId}
        analyzed={analysis !== null}
        onOpenChange={setActionOpen}
        onCaseChanged={refreshCase}
      />
    </div>
  );
}

function CaseHeader({ caseRecord }: { caseRecord: Case }) {
  return (
    <header className="mt-6">
      <MetaLabel>{caseRecord.domain.toUpperCase()}</MetaLabel>
      <h1 className="mt-2 text-[28px] leading-tight">{caseRecord.account}</h1>
      <p className="mt-2 text-lg text-[#F7F4EC]">{caseRecord.claim}</p>
      <p className="mt-3 text-sm text-[#A5A198]">{caseRecord.urgency}</p>
      <p className="mt-2 font-mono text-xs text-[#A5A198]">
        {patternLabel(caseRecord.pattern)} · {caseRecord.id}
      </p>
      <p className="mt-2 font-mono text-xs text-[#A5A198]">
        {queueStatusLabel(caseRecord.queue_status)}
        {caseRecord.disposition ? ` · ${caseRecord.disposition}` : ""}
        {caseRecord.last_action_status === "executed" ? " · Action executed" : ""}
        {` · Source count ${caseRecord.source_count}`}
      </p>
    </header>
  );
}

function DecisionBody({
  analysis,
  onInspect,
  onInvestigate,
  onTakeAction,
  onRunAgain,
}: {
  analysis: AnalyzeResponse;
  onInspect: (evidenceId: string) => void;
  onInvestigate: () => void;
  onTakeAction: () => void;
  onRunAgain: () => void;
}) {
  return (
    <div className="mt-8 space-y-8">
      <DispositionHero decision={analysis.decision} reason={analysis.reason} />
      <section>
        <MetaLabel>RECOMMENDED ACTION</MetaLabel>
        <p className="mt-3 max-w-[68ch] text-base leading-6 text-[#F7F4EC]">
          {analysis.recommended_action}
        </p>
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
              OWNER
            </dt>
            <dd className="mt-1 text-sm text-[#F7F4EC]">
              {analysis.suggested_owner}
            </dd>
          </div>
          {analysis.due_hint ? (
            <div>
              <dt className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
                DUE
              </dt>
              <dd className="mt-1 text-sm text-[#F7F4EC]">{analysis.due_hint}</dd>
            </div>
          ) : null}
        </dl>
        <div className="mt-5 flex flex-col gap-2 sm:flex-row">
          <Button onClick={onTakeAction}>Take action</Button>
          <Button variant="outline" onClick={onInvestigate}>
            Investigate
          </Button>
          <Button variant="outline" onClick={onRunAgain}>
            Run analysis again
          </Button>
        </div>
      </section>
      <EvidenceSection evidence={analysis.evidence} onInspect={onInspect} />
      <ChallengeSection
        challenges={analysis.contradictions_checked}
        onInspect={onInspect}
      />
      {analysis.missing_evidence.length > 0 ? (
        <section>
          <MetaLabel>MISSING EVIDENCE</MetaLabel>
          <ul className="mt-3 space-y-2">
            {analysis.missing_evidence.map((item) => (
              <li key={item} className="text-sm leading-6 text-[#F7F4EC]">
                {item}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <p className="max-w-[68ch] border-t border-[#2F2D28] pt-4 text-sm leading-6 text-[#A5A198]">
        Mulanous Lite recommends a decision and a plan. A human must approve
        before any state-changing step runs. Execution stays on synthetic tools
        in this demo process.
      </p>
    </div>
  );
}

function DispositionHero({
  decision,
  reason,
}: {
  decision: Disposition;
  reason: string;
}) {
  const treatment =
    decision === "VERIFY"
      ? "border-l-[#D5A942] text-[#D5A942]"
      : decision === "SUPPRESS"
        ? "border-l-[#2F2D28] text-[#A5A198]"
        : "border-l-[#F7F4EC] text-[#F7F4EC]";

  return (
    <section className={`border border-[#2F2D28] border-l-4 bg-[#0B0B0C] px-5 py-6 ${treatment}`}>
      <h2
        className={`font-mono tracking-[0.12em] ${
          decision === "SUPPRESS" ? "text-2xl" : "text-4xl"
        }`}
      >
        {decision}
      </h2>
      <p className="mt-4 max-w-[68ch] text-base leading-6 text-[#F7F4EC]">
        {reason}
      </p>
    </section>
  );
}

function EvidenceSection({
  evidence,
  onInspect,
}: {
  evidence: EvidenceRecord[];
  onInspect: (evidenceId: string) => void;
}) {
  return (
    <section>
      <MetaLabel>EVIDENCE</MetaLabel>
      {evidence.length === 0 ? (
        <p className="mt-3 text-sm text-[#A5A198]">
          No evidence records were returned with this decision.
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-[#2F2D28] border border-[#2F2D28]">
          {evidence.map((record) => (
            <li key={record.id}>
              <button
                type="button"
                className="w-full px-4 py-3 text-left hover:bg-[#151412]"
                onClick={() => onInspect(record.id)}
              >
                <span className="font-mono text-[11px] tracking-[0.14em] text-[#D5A942]">
                  {sourceLabel(record.source).toUpperCase()} · {record.source_record_id}
                </span>
                <span className="mt-1 block text-sm text-[#F7F4EC]">
                  {record.title}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function ChallengeSection({
  challenges,
  onInspect,
}: {
  challenges: AnalyzeResponse["contradictions_checked"];
  onInspect: (evidenceId: string) => void;
}) {
  return (
    <section>
      <MetaLabel>CONTRADICTIONS CHECKED</MetaLabel>
      {challenges.length === 0 ? (
        <p className="mt-3 text-sm text-[#A5A198]">
          No contradictions were checked for this decision.
        </p>
      ) : (
        <ul className="mt-3 space-y-3">
          {challenges.map((item) => (
            <li
              key={`${item.result}-${item.hypothesis}`}
              className="border border-[#2F2D28] bg-[#0B0B0C] px-4 py-3"
            >
              <p className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
                {challengeLabel(item.result).toUpperCase()}
              </p>
              <p className="mt-2 text-sm leading-6 text-[#F7F4EC]">
                {item.hypothesis}
              </p>
              <div className="mt-2 flex flex-wrap gap-3">
                {item.evidence_ids.map((evidenceId) => (
                  <button
                    key={evidenceId}
                    type="button"
                    className="font-mono text-xs text-[#D5A942]"
                    onClick={() => onInspect(evidenceId)}
                  >
                    {evidenceId}
                  </button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
