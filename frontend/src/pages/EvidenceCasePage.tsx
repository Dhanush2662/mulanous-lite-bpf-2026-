import { useState } from "react"
import { Link, useLocation, useParams } from "react-router-dom"

import { FallbackNote } from "../components/FallbackNote"
import { DecisionProgress } from "../features/case-brief/DecisionProgress"
import { challengeLabel, formatObserved, sourceLabel } from "../features/labels"
import { useAttentionQueue } from "../hooks/useAttentionQueue"
import { useCaseAnalysis } from "../hooks/useCaseAnalysis"
import type { AnalyzeResponse, Case, EvidenceRecord } from "../types/api"

export function EvidenceCasePage() {
  const { caseId = "" } = useParams()
  const location = useLocation()
  const preview = readPreview(location.state)
  const analysisState = useCaseAnalysis(caseId, preview)
  const queue = useAttentionQueue()
  const [pickedId, setPickedId] = useState<string | null>(null)
  const [closed, setClosed] = useState(false)

  const analysis = analysisState.analysis
  const evidence = analysis?.evidence ?? []
  const selected = closed
    ? null
    : (evidence.find((record) => record.id === pickedId) ?? evidence[0] ?? null)
  const caseRecord = queue.cases.find((item) => item.id === caseId) ?? preview
  const account = analysis?.account ?? preview?.account ?? ""
  const claim = analysis?.claim ?? preview?.claim ?? ""

  return (
    <>
      <header className="evidence-top">
        <p className="brand">MULANOUS LITE</p>
        <Link to={`/cases/${caseId}`} state={preview ? { preview } : undefined}>
          Case Brief
        </Link>
      </header>
      <main className="page evidence-page">
        <p className="crumbs">
          <Link to="/">Cases</Link>
          <span> / {caseId}</span>
        </p>

        {analysisState.phase === "progress" ? (
          <DecisionProgress
            account={account}
            claim={claim}
            steps={analysisState.steps}
            step={analysisState.step}
          />
        ) : null}

        {analysisState.phase === "error" ? (
          <div className="status-panel" role="alert">
            <p>Analysis did not complete.</p>
            <p>{analysisState.error}</p>
            <button type="button" className="open-button" onClick={analysisState.retry}>
              Try again
            </button>
          </div>
        ) : null}

        {analysisState.phase === "ready" && analysis ? (
          <>
            <FallbackNote
              source={analysisState.source}
              text="Local fallback. The decision service did not return this analysis."
            />
            <div className="evidence-case">
              <article>
                <header className="evidence-title">
                  <h1>
                    {analysis.case_id}: {analysis.claim}
                  </h1>
                  <p className={`disposition ${analysis.decision.toLowerCase()}`}>{analysis.decision}</p>
                </header>
                <MetaRow analysis={analysis} caseRecord={caseRecord} />
                <section>
                  <h2>OVERVIEW</h2>
                  <p>{analysis.reason || analysis.claim}</p>
                </section>
                <section>
                  <h2>INVESTIGATION NOTES</h2>
                  <p className="note-source">
                    Composed from the analyze evidence records and contradictions checked. The
                    service does not return a separate notes field.
                  </p>
                  <ul className="note-list">
                    {analysis.evidence.map((record) => (
                      <li key={record.id}>
                        <button
                          type="button"
                          className={record.id === selected?.id ? "is-selected" : ""}
                          onClick={() => {
                            setClosed(false)
                            setPickedId(record.id)
                          }}
                        >
                          <span className="mono">
                            {sourceLabel(record.source)} · {record.source_record_id}
                          </span>
                          <span>{record.title}</span>
                        </button>
                        <p>{record.body}</p>
                      </li>
                    ))}
                    {analysis.contradictions_checked.map((item) => (
                      <li key={`${item.result}-${item.hypothesis}`}>
                        <p className="mono">{challengeLabel(item.result)}</p>
                        <p>{item.hypothesis}</p>
                      </li>
                    ))}
                  </ul>
                </section>
              </article>
              <Inspector record={selected} onClose={() => setClosed(true)} />
            </div>
          </>
        ) : null}
      </main>
    </>
  )
}

function MetaRow({
  analysis,
  caseRecord,
}: {
  analysis: AnalyzeResponse
  caseRecord: Case | null
}) {
  const updated = latestObserved(analysis.evidence)
  return (
    <dl className="meta-row">
      {caseRecord ? (
        <div>
          <dt>STATUS</dt>
          <dd>{caseRecord.queue_status === "dismissed" ? "Dismissed" : "Open"}</dd>
        </div>
      ) : null}
      <div>
        <dt>ASSIGNEE</dt>
        <dd>{analysis.suggested_owner}</dd>
      </div>
      {updated ? (
        <div>
          <dt>UPDATED</dt>
          <dd className="mono">{formatObserved(updated)}</dd>
        </div>
      ) : null}
    </dl>
  )
}

function Inspector({
  record,
  onClose,
}: {
  record: EvidenceRecord | null
  onClose: () => void
}) {
  return (
    <aside className="inspector" aria-label="Evidence inspector">
      <div className="inspector-head">
        <h2>EVIDENCE INSPECTOR</h2>
        {record ? (
          <button type="button" className="text-button" onClick={onClose}>
            CLOSE INSPECTOR
          </button>
        ) : null}
      </div>
      {record ? (
        <dl className="evidence-fields">
          <div>
            <dt>SOURCE</dt>
            <dd>{sourceLabel(record.source)}</dd>
          </div>
          <div>
            <dt>SOURCE RECORD ID</dt>
            <dd className="mono">{record.source_record_id}</dd>
          </div>
          <div>
            <dt>TITLE</dt>
            <dd>{record.title}</dd>
          </div>
          <div>
            <dt>BODY</dt>
            <dd>{record.body}</dd>
          </div>
          <div>
            <dt>OBSERVED AT</dt>
            <dd className="mono">{formatObserved(record.observed_at)}</dd>
          </div>
        </dl>
      ) : (
        <p className="status-copy">Select an evidence record.</p>
      )}
    </aside>
  )
}

function latestObserved(records: EvidenceRecord[]): string | null {
  const stamps = records
    .map((record) => record.observed_at)
    .filter((value): value is string => Boolean(value))
    .sort()
  return stamps.at(-1) ?? null
}

function readPreview(state: unknown): Case | null {
  if (!state || typeof state !== "object" || !("preview" in state)) {
    return null
  }
  const preview = (state as { preview?: Case }).preview
  if (!preview || typeof preview.id !== "string") {
    return null
  }
  return preview
}
