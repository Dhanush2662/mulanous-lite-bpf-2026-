import { formatObserved, sourceLabel } from "../labels"
import type { EvidenceRecord } from "../../types/api"

export function EvidenceInspector({ record }: { record: EvidenceRecord | null }) {
  return (
    <aside className="inspector" aria-label="Evidence">
      <h2>EVIDENCE</h2>
      {record ? (
        <dl className="evidence-fields">
          <div>
            <dt>SOURCE</dt>
            <dd>{sourceLabel(record.source)}</dd>
          </div>
          <div>
            <dt>RECORD ID</dt>
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
        <p className="status-copy">Select an evidence row.</p>
      )}
    </aside>
  )
}
