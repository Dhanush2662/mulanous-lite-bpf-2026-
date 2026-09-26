import { challengeLabel, sourceLabel } from "../labels"
import type { AnalyzeResponse, EvidenceRecord } from "../../types/api"

export function CaseBriefView({
  analysis,
  onInspect,
  onPlan,
}: {
  analysis: AnalyzeResponse
  onInspect: (record: EvidenceRecord) => void
  onPlan: () => void
}) {
  const tone = analysis.decision.toLowerCase()

  return (
    <div className="brief">
      <header className="brief-head">
        <h1>{analysis.account}</h1>
        <p>{analysis.claim}</p>
      </header>

      <section className={`hero ${tone}`}>
        <h2>{analysis.decision}</h2>
        <p>{analysis.reason}</p>
      </section>

      <section className="action-block">
        <h3>RECOMMENDED ACTION</h3>
        <p>{analysis.recommended_action}</p>
        <dl>
          <div>
            <dt>OWNER</dt>
            <dd>{analysis.suggested_owner}</dd>
          </div>
          {analysis.due_hint ? (
            <div>
              <dt>DUE</dt>
              <dd>{analysis.due_hint}</dd>
            </div>
          ) : null}
        </dl>
        <button type="button" className="plan-button" onClick={onPlan}>
          PLAN ACTION
        </button>
      </section>

      <section className="evidence-block">
        <h3>EVIDENCE</h3>
        {analysis.evidence.length === 0 ? (
          <p className="status-copy">No evidence records were returned with this decision.</p>
        ) : (
          <table className="evidence-table">
            <thead>
              <tr>
                <th>SOURCE</th>
                <th>RECORD ID</th>
                <th>TITLE</th>
              </tr>
            </thead>
            <tbody>
              {analysis.evidence.map((record) => (
                <tr
                  key={record.id}
                  tabIndex={0}
                  onClick={() => onInspect(record)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault()
                      onInspect(record)
                    }
                  }}
                >
                  <td>{sourceLabel(record.source)}</td>
                  <td className="mono">{record.source_record_id}</td>
                  <td>{record.title}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="challenge-block">
        <h3>CONTRADICTIONS CHECKED</h3>
        {analysis.contradictions_checked.length === 0 ? (
          <p className="status-copy">No contradictions were checked for this decision.</p>
        ) : (
          <ul>
            {analysis.contradictions_checked.map((item) => (
              <li key={`${item.result}-${item.hypothesis}`}>
                <p className="mono">{challengeLabel(item.result)}</p>
                <p>{item.hypothesis}</p>
                <p className="mono evidence-ids">{item.evidence_ids.join(" · ")}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {analysis.missing_evidence.length > 0 ? (
        <section className="missing-block">
          <h3>MISSING EVIDENCE</h3>
          <ul>
            {analysis.missing_evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  )
}
