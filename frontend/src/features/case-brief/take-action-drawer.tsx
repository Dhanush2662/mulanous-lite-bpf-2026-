"use client";

import { useState } from "react";

import {
  errorMessage,
  executeAction,
  isAbortError,
  planAction,
} from "@/api/client";
import { MetaLabel } from "@/components/meta-label";
import { SyntheticStateView } from "@/components/synthetic-state";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { ActionPlan, ActionResult } from "@/types/api";

export function TakeActionDrawer({
  open,
  caseId,
  analyzed,
  onOpenChange,
  onCaseChanged,
}: {
  open: boolean;
  caseId: string;
  analyzed: boolean;
  onOpenChange: (open: boolean) => void;
  onCaseChanged: () => void;
}) {
  const [plan, setPlan] = useState<ActionPlan | null>(null);
  const [result, setResult] = useState<ActionResult | null>(null);
  const [pending, setPending] = useState<"plan" | "execute" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function planCase() {
    setPending("plan");
    setError(null);
    setResult(null);
    try {
      const next = await planAction(caseId);
      setPlan(next);
      if (!next.requires_approval) {
        onCaseChanged();
      }
    } catch (planError) {
      if (!isAbortError(planError)) {
        setError(errorMessage(planError));
      }
    } finally {
      setPending(null);
    }
  }

  async function approve() {
    if (!plan || !plan.requires_approval) {
      return;
    }
    setPending("execute");
    setError(null);
    try {
      const executed = await executeAction(plan.plan_id);
      setResult(executed);
      onCaseChanged();
    } catch (executeError) {
      if (!isAbortError(executeError)) {
        setError(errorMessage(executeError));
      }
    } finally {
      setPending(null);
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-2xl">
        <SheetHeader>
          <SheetTitle>Take action</SheetTitle>
          <SheetDescription>
            The plan is shown before anything state-changing runs. Approval
            applies only the stored plan.
          </SheetDescription>
        </SheetHeader>
        <div className="space-y-4 px-4 pb-8">
          {!analyzed ? (
            <p className="text-sm text-[#A5A198]">
              Analyze the case before planning an action.
            </p>
          ) : (
            <Button onClick={() => void planCase()} disabled={pending !== null}>
              {pending === "plan" ? "Planning" : "Plan action"}
            </Button>
          )}
          {error ? (
            <p className="text-sm text-[#F7F4EC]" role="alert">
              {error}
            </p>
          ) : null}
          {plan ? <PlanBody plan={plan} /> : null}
          {plan?.requires_approval && !result ? (
            <Button onClick={() => void approve()} disabled={pending !== null}>
              {pending === "execute" ? "Executing" : "Approve and execute"}
            </Button>
          ) : null}
          {plan && !plan.requires_approval ? (
            <p className="text-sm leading-6 text-[#A5A198]">
              Applied under policy. This plan did not require approval, so the
              service applied it when the plan was created. An after-state is
              returned only by execution, and executing this plan again is
              rejected. The attention queue shows the updated case.
            </p>
          ) : null}
          {result ? <ResultBody result={result} /> : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function PlanBody({ plan }: { plan: ActionPlan }) {
  return (
    <div className="space-y-4">
      <div>
        <MetaLabel>PLAN</MetaLabel>
        <p className="mt-2 font-mono text-xs text-[#F7F4EC]">{plan.plan_id}</p>
        <p className="mt-2 text-sm text-[#A5A198]">
          {plan.requires_approval
            ? "Approval required. Nothing in this plan has run."
            : "Approval not required."}
        </p>
      </div>
      <ol className="space-y-3">
        {plan.steps.map((step) => (
          <li key={`${step.tool}-${step.summary}`} className="border border-[#2F2D28] px-3 py-3">
            <p className="font-mono text-xs text-[#D5A942]">{step.tool}</p>
            <p className="mt-2 text-sm text-[#F7F4EC]">{step.summary}</p>
            <dl className="mt-3 space-y-1">
              {Object.entries(step.args).map(([key, value]) => (
                <div key={key}>
                  <dt className="font-mono text-[11px] text-[#A5A198]">{key}</dt>
                  <dd className="text-sm text-[#F7F4EC]">{value}</dd>
                </div>
              ))}
            </dl>
          </li>
        ))}
      </ol>
      <SyntheticStateView title="BEFORE" state={plan.before_state} />
    </div>
  );
}

function ResultBody({ result }: { result: ActionResult }) {
  return (
    <div className="space-y-4">
      <div>
        <MetaLabel>RESULT</MetaLabel>
        <p className="mt-2 font-mono text-xs text-[#D5A942]">{result.status}</p>
        <ul className="mt-3 space-y-2">
          {result.results.map((step) => (
            <li key={`${step.tool}-${step.summary}`} className="text-sm text-[#F7F4EC]">
              <span className="font-mono text-xs text-[#D5A942]">{step.tool}</span>
              <span className="mt-1 block">{step.summary}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <SyntheticStateView title="BEFORE" state={result.before_state} />
        <SyntheticStateView title="AFTER" state={result.after_state} />
      </div>
    </div>
  );
}
