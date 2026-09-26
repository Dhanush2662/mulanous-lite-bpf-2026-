"use client";

import { useEffect, useState } from "react";

import { errorMessage, getEvidence, isAbortError } from "@/api/client";
import { MetaLabel } from "@/components/meta-label";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { formatObservedAt, sourceLabel } from "@/lib/labels";
import type { EvidenceRecord } from "@/types/api";

export function EvidenceInspector({
  evidenceId,
  fallback,
  onOpenChange,
}: {
  evidenceId: string | null;
  fallback: EvidenceRecord | null;
  onOpenChange: (open: boolean) => void;
}) {
  const [record, setRecord] = useState<EvidenceRecord | null>(fallback);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!evidenceId) {
      setRecord(null);
      setError(null);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setError(null);
    setRecord(fallback?.id === evidenceId ? fallback : null);

    getEvidence(evidenceId, controller.signal)
      .then((loaded) => {
        setRecord(loaded);
        setLoading(false);
      })
      .catch((loadError: unknown) => {
        if (isAbortError(loadError)) {
          return;
        }
        setError(errorMessage(loadError));
        setLoading(false);
      });

    return () => controller.abort();
  }, [evidenceId, fallback]);

  return (
    <Sheet open={evidenceId !== null} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-xl">
        <SheetHeader>
          <SheetTitle>Evidence</SheetTitle>
          <SheetDescription>
            One record from the evidence service, with source and timestamp.
          </SheetDescription>
        </SheetHeader>
        <div className="px-4 pb-6">
          {loading ? (
            <p className="text-sm text-[#A5A198]" role="status">
              Loading evidence record.
            </p>
          ) : null}
          {error ? (
            <p className="text-sm text-[#F7F4EC]" role="alert">
              {error}
            </p>
          ) : null}
          {record ? <EvidenceBody record={record} /> : null}
          {!loading && !error && !record ? (
            <p className="text-sm text-[#A5A198]">
              No evidence record is open.
            </p>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function EvidenceBody({ record }: { record: EvidenceRecord }) {
  return (
    <article className="mt-2 border border-[#2F2D28] bg-[#080808] px-4 py-4">
      <MetaLabel>{sourceLabel(record.source).toUpperCase()}</MetaLabel>
      <p className="mt-3 font-mono text-sm text-[#D5A942]">
        {record.source_record_id}
      </p>
      <h3 className="mt-3 text-lg text-[#F7F4EC]">{record.title}</h3>
      <p className="mt-3 text-sm leading-6 text-[#F7F4EC]">{record.body}</p>
      <p className="mt-4 font-mono text-xs text-[#A5A198]">
        {formatObservedAt(record.observed_at)}
      </p>
      {record.observed_at ? (
        <p className="mt-1 font-mono text-xs text-[#A5A198]">{record.observed_at}</p>
      ) : null}
      <p className="mt-3 font-mono text-xs text-[#A5A198]">{record.id}</p>
    </article>
  );
}
