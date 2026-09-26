import { SourceChips } from "../../components/SourceChips"
import { challengeLabel, domainSources, formatObserved, sourceLabel } from "../labels"
import type { AnalyzeResponse, Domain, EvidenceRecord } from "../../types/api"

export function CaseBriefView({
  analysis,
  domain,
  selectedId,
  onInspect,
  onPlan,
}: {
  analysis: AnalyzeResponse
  domain: Domain
  selectedId: string | null
  onInspect: (record: EvidenceRecord) => void
  onPlan: () => void
}) {
  const tone = analysis.decision.toLowerCase()
  const contradiction = contradictionLine(analysis)

  return (
    <div className="brief">
      <p className="case-kicker">Case Brief</p>
      <header className="case-identity">
        <p>
          {analysis.account}
          {" · "}
          {analysis.claim}
          {" · "}
          <span className="mono">{analysis.case_id}</span>
        </p>
        <div className="case-identity-side">
          <SourceChips names={domainSources(domain)} />
          <p className="demo-mark">SYNTHETIC DEMO</p>
        </div>
      </header>

      <section className={`hero ${tone}`}>
        <h2>{analysis.decision}</h2>
        <p className="decision-title">{analysis.recommended_action}</p>
        <p>{analysis.reason}</p>
      </section>

      <section className="challenge-block">
        <h3>CONTRADICTIONS CHECKED</h3>
        <p className="contradiction-line">{contradiction}</p>
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
                <th>TITLE</th>
                <th>SUMMARY</th>
                <th>OBSERVED AT</th>
              </tr>
            </thead>
            <tbody>
              {analysis.evidence.map((record) => (
                <tr
                  key={record.id}
                  tabIndex={0}
                  className={record.id === selectedId ? "is-selected" : ""}
                  onClick={() => onInspect(record)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault()
                      onInspect(record)
                    }
                  }}
                >
                  <td>{sourceLabel(record.source)}</td>
                  <td>{record.title}</td>
                  <td className="summary">{record.body}</td>
                  <td className="mono">{formatObserved(record.observed_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
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

function contradictionLine(analysis: AnalyzeResponse): string {
  if (analysis.contradictions_checked.length === 0) {
    return "No contradictions were checked for this decision."
  }
  return analysis.contradictions_checked
    .map((item) => `${item.hypothesis} ${challengeLabel(item.result)}`)
    .join(" · ")
}
