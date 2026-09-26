import { MetaLabel } from "@/components/meta-label";
import type { SyntheticState } from "@/types/api";

export function SyntheticStateView({
  title,
  state,
}: {
  title: string;
  state: SyntheticState;
}) {
  return (
    <section className="border border-[#2F2D28] bg-[#0B0B0C] px-4 py-4">
      <MetaLabel>{title}</MetaLabel>
      <StateGroup label="Tasks" empty={state.tasks.length === 0}>
        {state.tasks.map((item) => (
          <RecordLine
            key={item.id}
            primary={`${item.id} · ${item.title}`}
            secondary={`${item.owner} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup label="Messages" empty={state.messages.length === 0}>
        {state.messages.map((item) => (
          <RecordLine
            key={item.id}
            primary={`${item.id} · ${item.recipient}`}
            secondary={`${item.body} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup label="Account risks" empty={state.account_risks.length === 0}>
        {state.account_risks.map((item) => (
          <RecordLine
            key={`${item.case_id}-${item.account}-${item.risk_note}`}
            primary={item.account}
            secondary={`${item.risk_note} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup
        label="Material expedites"
        empty={state.material_expedites.length === 0}
      >
        {state.material_expedites.map((item) => (
          <RecordLine
            key={item.id}
            primary={`${item.id} · ${item.material}`}
            secondary={`${item.detail} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup label="Planner notices" empty={state.planner_notices.length === 0}>
        {state.planner_notices.map((item) => (
          <RecordLine
            key={item.id}
            primary={`${item.id} · ${item.recipient}`}
            secondary={`${item.body} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup label="Order risks" empty={state.order_risks.length === 0}>
        {state.order_risks.map((item) => (
          <RecordLine
            key={item.id}
            primary={`${item.id} · ${item.order_id}`}
            secondary={`${item.risk_note} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup
        label="Acknowledgements"
        empty={state.acknowledgements.length === 0}
      >
        {state.acknowledgements.map((item) => (
          <RecordLine
            key={item.id}
            primary={item.id}
            secondary={`${item.note} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup
        label="Evidence requests"
        empty={state.evidence_requests.length === 0}
      >
        {state.evidence_requests.map((item) => (
          <RecordLine
            key={item.id}
            primary={item.id}
            secondary={`${item.detail} · ${item.case_id}`}
          />
        ))}
      </StateGroup>
      <StateGroup
        label="Dismissed cases"
        empty={state.dismissed_case_ids.length === 0}
      >
        {state.dismissed_case_ids.map((caseId) => (
          <p key={caseId} className="font-mono text-sm text-[#F7F4EC]">
            {caseId}
          </p>
        ))}
      </StateGroup>
    </section>
  );
}

function StateGroup({
  label,
  empty,
  children,
}: {
  label: string;
  empty: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="mt-4 border-t border-[#2F2D28] pt-3">
      <p className="font-mono text-[11px] tracking-[0.14em] text-[#A5A198]">
        {label}
      </p>
      <div className="mt-2 space-y-2">
        {empty ? <p className="text-sm text-[#A5A198]">None</p> : children}
      </div>
    </div>
  );
}

function RecordLine({
  primary,
  secondary,
}: {
  primary: string;
  secondary: string;
}) {
  return (
    <div>
      <p className="text-sm text-[#F7F4EC]">{primary}</p>
      <p className="text-sm text-[#A5A198]">{secondary}</p>
    </div>
  );
}
