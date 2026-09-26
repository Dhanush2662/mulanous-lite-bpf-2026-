export type Disposition = "VERIFY" | "SUPPRESS" | "ABSTAIN"

export type Domain = "software" | "manufacturing" | "logistics"

export type ChallengeOutcome = "supported" | "not_supported" | "inconclusive"

export type ActionTool =
  | "create_task"
  | "send_message"
  | "update_account_risk"
  | "expedite_material"
  | "notify_planner"
  | "update_order_risk"
  | "dismiss_resolved"
  | "acknowledge"
  | "request_evidence"

export interface Case {
  id: string
  domain: Domain
  pattern: string
  account: string
  claim: string
  urgency: string
  source_count: number
  disposition: Disposition | null
  queue_status: "open" | "dismissed"
  last_action_status: "none" | "executed"
}

export interface EvidenceRecord {
  id: string
  source: string
  source_record_id: string
  title: string
  body: string
  observed_at: string | null
}

export interface ChallengeResult {
  hypothesis: string
  result: ChallengeOutcome
  evidence_ids: string[]
}

export interface AnalyzeResponse {
  case_id: string
  account: string
  claim: string
  decision: Disposition
  reason: string
  recommended_action: string
  suggested_owner: string
  due_hint: string | null
  evidence: EvidenceRecord[]
  contradictions_checked: ChallengeResult[]
  missing_evidence: string[]
}

export interface ActionStep {
  tool: ActionTool
  summary: string
  args: Record<string, string>
}

export interface SyntheticTask {
  id: string
  title: string
  owner: string
  case_id: string
}

export interface SyntheticMessage {
  id: string
  recipient: string
  body: string
  case_id: string
}

export interface SyntheticAccountRisk {
  account: string
  risk_note: string
  case_id: string
}

export interface MaterialExpedite {
  id: string
  material: string
  detail: string
  case_id: string
}

export interface PlannerNotice {
  id: string
  recipient: string
  body: string
  case_id: string
}

export interface OrderRisk {
  id: string
  order_id: string
  risk_note: string
  case_id: string
}

export interface Acknowledgement {
  id: string
  case_id: string
  note: string
}

export interface EvidenceRequestNote {
  id: string
  case_id: string
  detail: string
}

export interface SyntheticState {
  tasks: SyntheticTask[]
  messages: SyntheticMessage[]
  account_risks: SyntheticAccountRisk[]
  material_expedites: MaterialExpedite[]
  planner_notices: PlannerNotice[]
  order_risks: OrderRisk[]
  acknowledgements: Acknowledgement[]
  evidence_requests: EvidenceRequestNote[]
  dismissed_case_ids: string[]
}

export interface ActionPlan {
  plan_id: string
  case_id: string
  steps: ActionStep[]
  requires_approval: boolean
  before_state: SyntheticState
}

export interface ActionStepResult {
  tool: ActionTool
  summary: string
}

export interface ActionResult {
  plan_id: string
  case_id: string
  status: "executed"
  results: ActionStepResult[]
  before_state: SyntheticState
  after_state: SyntheticState
}

export type DataSource = "api" | "fallback"
