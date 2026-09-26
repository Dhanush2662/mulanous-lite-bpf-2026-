import { Drawer } from "../../components/Drawer"
import { sourceLabel } from "../labels"
import type { EvidenceRecord } from "../../types/api"

export function EvidenceInspector({
  record,
  onClose,
}: {
  record: EvidenceRecord | null
  onClose: () => void
}) {
  if (!record) {
    return null
  }

  return (
    <Drawer title="EVIDENCE" onClose={onClose}>
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
          <dd className="mono">{record.observed_at ?? "No timestamp"}</dd>
        </div>
      </dl>
    </Drawer>
  )
}
