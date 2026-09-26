"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { errorMessage, getCaseEvidence, getCases, isAbortError } from "@/api/client";
import { MetaLabel } from "@/components/meta-label";
import { StatusNotice } from "@/components/status-notice";
import {
  patternLabel,
  queueStatusLabel,
  sourceLabel,
  uniqueSources,
} from "@/lib/labels";
import type { Case, Disposition } from "@/types/api";

interface QueueRow {
  item: Case;
  sources: string[];
  sourcesError: string | null;
}

export function AttentionToday() {
  const [rows, setRows] = useState<QueueRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);

  const reload = useCallback(() => {
    setAttempt((current) => current + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    getCases(controller.signal)
      .then(async (cases) => {
        const loaded = await Promise.all(
          cases.map((item) => loadRow(item, controller.signal)),
        );
        if (!controller.signal.aborted) {
          setRows(loaded);
          setLoading(false);
        }
      })
      .catch((loadError: unknown) => {
        if (isAbortError(loadError)) {
          return;
        }
        setRows(null);
        setError(errorMessage(loadError));
        setLoading(false);
      });

    return () => controller.abort();
  }, [attempt]);

  return (
    <div>
      <h1 className="max-w-[18ch] text-[32px] leading-tight tracking-tight sm:text-4xl">
        What needs my attention today?
      </h1>
      <p className="mt-4 max-w-[62ch] text-sm leading-6 text-[#A5A198]">
        Operational cases from the decision service. Opening a case runs
        analysis and opens the brief.
      </p>

      {loading ? (
        <div className="mt-8">
          <StatusNotice title="Loading the attention queue." />
        </div>
      ) : null}

      {error ? (
        <div className="mt-8">
          <StatusNotice
            alert
            title="The attention queue could not be loaded."
            detail={error}
            onRetry={reload}
          />
        </div>
      ) : null}

      {rows && rows.length === 0 ? (
        <div className="mt-8">
          <StatusNotice
            title="The attention queue is empty."
            detail="The decision service returned no cases."
          />
        </div>
      ) : null}

      {rows && rows.length > 0 ? (
        <div className="mt-8 space-y-8">
          <SourceStrip rows={rows} />
          {groupRows(rows).map((group) => (
            <section key={group.domain}>
              <h2 className="font-mono text-[11px] tracking-[0.18em] text-[#A5A198]">
                {group.domain.toUpperCase()}
              </h2>
              <div className="mt-3 divide-y divide-[#2F2D28] border border-[#2F2D28] bg-[#0B0B0C]">
                {group.items.map((row) => (
                  <CaseRow key={row.item.id} row={row} />
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : null}
    </div>
  );
}

async function loadRow(item: Case, signal: AbortSignal): Promise<QueueRow> {
  try {
    const evidence = await getCaseEvidence(item.id, signal);
    return {
      item,
      sources: uniqueSources(evidence.map((record) => record.source)),
      sourcesError: null,
    };
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }
    return { item, sources: [], sourcesError: errorMessage(error) };
  }
}

function groupRows(rows: QueueRow[]): { domain: string; items: QueueRow[] }[] {
  const groups: { domain: string; items: QueueRow[] }[] = [];
  for (const row of rows) {
    const last = groups[groups.length - 1];
    if (!last || last.domain !== row.item.domain) {
      groups.push({ domain: row.item.domain, items: [row] });
    } else {
      last.items.push(row);
    }
  }
  return groups;
}

function SourceStrip({ rows }: { rows: QueueRow[] }) {
  const byDomain = new Map<string, Set<string>>();
  for (const row of rows) {
    const set = byDomain.get(row.item.domain) ?? new Set<string>();
    for (const source of row.sources) {
      set.add(source);
    }
    byDomain.set(row.item.domain, set);
  }

  const lines = [...byDomain.entries()]
    .map(([domain, sources]) => ({
      domain,
      sources: uniqueSources([...sources]),
    }))
    .filter((line) => line.sources.length > 0);

  if (lines.length === 0) {
    return null;
  }

  return (
    <section className="border border-[#2F2D28] bg-[#151412] px-4 py-4">
      <MetaLabel>SOURCES</MetaLabel>
      <div className="mt-3 space-y-2">
        {lines.map((line) => (
          <p key={line.domain} className="text-sm">
            <span className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
              {line.domain.toUpperCase()}
            </span>
            <span className="mx-3 text-[#2F2D28]">|</span>
            <span className="text-[#F7F4EC]">
              {line.sources.map(sourceLabel).join(" · ")}
            </span>
          </p>
        ))}
      </div>
    </section>
  );
}

function CaseRow({ row }: { row: QueueRow }) {
  const { item } = row;
  const quiet = item.queue_status === "dismissed";

  return (
    <Link
      href={`/cases/${item.id}`}
      className={`block px-4 py-4 transition-colors duration-150 hover:bg-[#151412] focus-visible:bg-[#151412] sm:px-5 ${
        quiet ? "opacity-70" : ""
      }`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-lg text-[#F7F4EC]">{item.account}</p>
          <p className="mt-1 text-base text-[#F7F4EC]">{item.claim}</p>
          <p className="mt-2 text-sm text-[#A5A198]">{item.urgency}</p>
          <p className="mt-2 font-mono text-xs text-[#A5A198]">
            {patternLabel(item.pattern)}
          </p>
          {row.sources.length > 0 ? (
            <p className="mt-3 font-mono text-xs text-[#D5A942]">
              {row.sources.map(sourceLabel).join(" · ")}
            </p>
          ) : null}
          {row.sourcesError ? (
            <p className="mt-3 text-sm text-[#A5A198]">
              Evidence sources could not be loaded. {row.sourcesError}
            </p>
          ) : null}
        </div>
        <div className="flex shrink-0 flex-row gap-6 sm:flex-col sm:items-end sm:gap-2 sm:text-right">
          <p className="font-mono text-xs tracking-[0.14em] text-[#F7F4EC]">
            {queueStatusLabel(item.queue_status)}
          </p>
          <DispositionMark disposition={item.disposition} />
          <p className="font-mono text-xs text-[#A5A198]">
            Source count {item.source_count}
          </p>
          {item.last_action_status === "executed" ? (
            <p className="font-mono text-xs text-[#D5A942]">Action executed</p>
          ) : null}
        </div>
      </div>
    </Link>
  );
}

function DispositionMark({ disposition }: { disposition: Disposition | null }) {
  if (!disposition) {
    return (
      <p className="font-mono text-xs tracking-[0.14em] text-[#A5A198]">
        NOT ANALYZED
      </p>
    );
  }

  const tone =
    disposition === "VERIFY"
      ? "text-[#D5A942]"
      : disposition === "SUPPRESS"
        ? "text-[#A5A198]"
        : "text-[#F7F4EC]";

  return (
    <p className={`font-mono text-xs tracking-[0.14em] ${tone}`}>{disposition}</p>
  );
}
