import type { SyntheticState } from "../../types/api"

export function SyntheticStateView({ title, state }: { title: string; state: SyntheticState }) {
  return (
    <section className="state-block">
      <h3>{title}</h3>
      <StateGroup label="Tasks" empty={state.tasks.length === 0}>
        {state.tasks.map((item) => (
          <p key={item.id}>
            {item.id} · {item.title}
            <span>{item.owner} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Messages" empty={state.messages.length === 0}>
        {state.messages.map((item) => (
          <p key={item.id}>
            {item.id} · {item.recipient}
            <span>{item.body} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Account risks" empty={state.account_risks.length === 0}>
        {state.account_risks.map((item, index) => (
          <p key={`${item.case_id}-${item.account}-${index}`}>
            {item.account}
            <span>{item.risk_note} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Material expedites" empty={state.material_expedites.length === 0}>
        {state.material_expedites.map((item) => (
          <p key={item.id}>
            {item.id} · {item.material}
            <span>{item.detail} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Planner notices" empty={state.planner_notices.length === 0}>
        {state.planner_notices.map((item) => (
          <p key={item.id}>
            {item.id} · {item.recipient}
            <span>{item.body} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Order risks" empty={state.order_risks.length === 0}>
        {state.order_risks.map((item) => (
          <p key={item.id}>
            {item.id} · {item.order_id}
            <span>{item.risk_note} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Acknowledgements" empty={state.acknowledgements.length === 0}>
        {state.acknowledgements.map((item) => (
          <p key={item.id}>
            {item.id}
            <span>{item.note} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Evidence requests" empty={state.evidence_requests.length === 0}>
        {state.evidence_requests.map((item) => (
          <p key={item.id}>
            {item.id}
            <span>{item.detail} · {item.case_id}</span>
          </p>
        ))}
      </StateGroup>
      <StateGroup label="Dismissed cases" empty={state.dismissed_case_ids.length === 0}>
        {state.dismissed_case_ids.map((caseId) => (
          <p key={caseId} className="mono">
            {caseId}
          </p>
        ))}
      </StateGroup>
    </section>
  )
}

function StateGroup({
  label,
  empty,
  children,
}: {
  label: string
  empty: boolean
  children: React.ReactNode
}) {
  return (
    <div className="state-group">
      <p>{label}</p>
      {empty ? <p className="none">None</p> : <div>{children}</div>}
    </div>
  )
}
