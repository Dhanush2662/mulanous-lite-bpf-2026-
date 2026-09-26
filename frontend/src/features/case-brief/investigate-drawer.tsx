"use client";

import { useState } from "react";

import {
  errorMessage,
  investigateCase,
  isAbortError,
} from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import type { Disposition, InvestigateResponse } from "@/types/api";

export function InvestigateDrawer({
  open,
  caseId,
  decision,
  onOpenChange,
  onInspect,
  onReanalyzed,
}: {
  open: boolean;
  caseId: string;
  decision: Disposition | null;
  onOpenChange: (open: boolean) => void;
  onInspect: (evidenceId: string) => void;
  onReanalyzed: () => void;
}) {
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<InvestigateResponse | null>(null);

  const prompts = suggestedPrompts(decision);

  async function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed || pending) {
      return;
    }
    setPending(true);
    setError(null);
    try {
      const result = await investigateCase(caseId, trimmed);
      setResponse(result);
      setMessage(trimmed);
      if (result.tools_used.includes("reanalyze_case")) {
        onReanalyzed();
      }
    } catch (askError) {
      if (!isAbortError(askError)) {
        setError(errorMessage(askError));
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-xl">
        <SheetHeader>
          <SheetTitle>Investigate</SheetTitle>
          <SheetDescription>
            Questions stay on this case. Answers come from the case tools.
          </SheetDescription>
        </SheetHeader>
        <div className="space-y-4 px-4 pb-6">
          <div className="flex flex-col gap-2">
            {prompts.map((prompt) => (
              <Button
                key={prompt}
                variant="outline"
                className="h-auto justify-start px-3 py-2 text-left whitespace-normal"
                disabled={pending}
                onClick={() => void ask(prompt)}
              >
                {prompt}
              </Button>
            ))}
          </div>
          <form
            className="flex flex-col gap-2 sm:flex-row"
            onSubmit={(event) => {
              event.preventDefault();
              void ask(message);
            }}
          >
            <Input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask about this case"
              aria-label="Question about this case"
              disabled={pending}
            />
            <Button type="submit" disabled={pending || message.trim() === ""}>
              Ask about this case
            </Button>
          </form>
          {pending ? (
            <p className="text-sm text-[#A5A198]" role="status">
              Checking this case.
            </p>
          ) : null}
          {error ? (
            <p className="text-sm text-[#F7F4EC]" role="alert">
              {error}
            </p>
          ) : null}
          {response ? (
            <article className="border border-[#2F2D28] bg-[#080808] px-4 py-4">
              <p className="text-sm leading-6 text-[#F7F4EC]">{response.answer}</p>
              <p className="mt-4 font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
                TOOLS
              </p>
              <p className="mt-2 font-mono text-xs text-[#F7F4EC]">
                {response.tools_used.join(" · ")}
              </p>
              <p className="mt-4 font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
                EVIDENCE
              </p>
              {response.evidence_ids.length === 0 ? (
                <p className="mt-2 text-sm text-[#A5A198]">
                  No evidence ids were returned.
                </p>
              ) : (
                <div className="mt-2 flex flex-col items-start gap-1">
                  {response.evidence_ids.map((evidenceId) => (
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
              )}
            </article>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function suggestedPrompts(decision: Disposition | null): string[] {
  const why = decision
    ? `Why is this ${decision}?`
    : "Why was this verified, suppressed, or abstained?";
  return [
    why,
    "What evidence contradicts this?",
    "What would change this decision?",
    "Check whether the blocker is already resolved",
    "What information is missing?",
  ];
}
