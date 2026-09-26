import type {
  ActionPlan,
  ActionResult,
  ActionStep,
  Case,
  SyntheticState,
} from "../types/api"
import { FALLBACK_ANALYSES } from "./fallback-analyses"

export { FALLBACK_ANALYSES }

export const FALLBACK_CASES: Case[] = [
  {
    id: "acme-sso-rollout",
    domain: "software",
    pattern: "customer_commitment_intervention",
    account: "Acme",
    claim: "SSO rollout blocked",
    urgency: "Customer checkpoint today",
    source_count: 8,
    disposition: null,
    queue_status: "open",
    last_action_status: "none",
  },
  {
    id: "globex-export-timeout",
    domain: "software",
    pattern: "customer_commitment_intervention",
    account: "Globex",
    claim: "Export timeout escalation",
    urgency: "Escalation thread is already in close-out",
    source_count: 8,
    disposition: null,
    queue_status: "open",
    last_action_status: "none",
  },
  {
    id: "initech-europe-expansion",
    domain: "software",
    pattern: "customer_commitment_intervention",
    account: "Initech",
    claim: "Europe expansion at risk",
    urgency: "No dated milestone",
    source_count: 7,
    disposition: null,
    queue_status: "open",
    last_action_status: "none",
  },
  {
    id: "orion-order-5000",
    domain: "manufacturing",
    pattern: "production_commitment_intervention",
    account: "Orion Components",
    claim: "5,000 units due Monday",
    urgency: "Due Monday",
    source_count: 5,
    disposition: null,
    queue_status: "open",
    last_action_status: "none",
  },
]

export function emptyState(): SyntheticState {
  return {
    tasks: [],
    messages: [],
    account_risks: [],
    material_expedites: [],
    planner_notices: [],
    order_risks: [],
    acknowledgements: [],
    evidence_requests: [],
    dismissed_case_ids: [],
  }
}

/** Take Action reference copy. Used only when POST /api/actions/plan cannot be reached for Acme. */
export function fallbackAcmePlan(): ActionPlan {
  return {
    plan_id: "fallback-acme-plan",
    case_id: "acme-sso-rollout",
    requires_approval: true,
    before_state: emptyState(),
    steps: [
      {
        tool: "create_task",
        summary: "Create a task for the delivery owner.",
        args: {
          title: "Confirm the unresolved SAML mapping blocker with the delivery owner.",
          owner: "Delivery owner",
          case_id: "acme-sso-rollout",
        },
      },
      {
        tool: "send_message",
        summary: "Message the delivery owner about the intervention.",
        args: {
          recipient: "Delivery owner",
          body: "Confirm the unresolved SAML mapping blocker before the customer checkpoint.",
          case_id: "acme-sso-rollout",
        },
      },
      {
        tool: "update_account_risk",
        summary: "Record an account risk note for Acme.",
        args: {
          account: "Acme",
          risk_note: "SSO rollout is blocked by unresolved SAML mapping.",
          case_id: "acme-sso-rollout",
        },
      },
    ],
  }
}

export function localExecute(plan: ActionPlan): ActionResult {
  const after = structuredClone(plan.before_state)
  let sequence = 1
  for (const step of plan.steps) {
    applyLocal(step, after, sequence)
    sequence += 1
  }
  return {
    plan_id: plan.plan_id,
    case_id: plan.case_id,
    status: "executed",
    results: plan.steps.map((step) => ({ tool: step.tool, summary: step.summary })),
    before_state: plan.before_state,
    after_state: after,
  }
}

function applyLocal(step: ActionStep, state: SyntheticState, sequence: number): void {
  const caseId = step.args.case_id ?? ""
  if (step.tool === "create_task") {
    state.tasks.push({
      id: `task-${sequence}`,
      title: step.args.title ?? "",
      owner: step.args.owner ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "send_message") {
    state.messages.push({
      id: `message-${sequence}`,
      recipient: step.args.recipient ?? "",
      body: step.args.body ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "update_account_risk") {
    state.account_risks.push({
      account: step.args.account ?? "",
      risk_note: step.args.risk_note ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "expedite_material") {
    state.material_expedites.push({
      id: `expedite-${sequence}`,
      material: step.args.material ?? "",
      detail: step.args.detail ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "notify_planner") {
    state.planner_notices.push({
      id: `notice-${sequence}`,
      recipient: step.args.recipient ?? "",
      body: step.args.body ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "update_order_risk") {
    state.order_risks.push({
      id: `order-${sequence}`,
      order_id: step.args.order_id ?? "",
      risk_note: step.args.risk_note ?? "",
      case_id: caseId,
    })
  } else if (step.tool === "acknowledge") {
    state.acknowledgements.push({
      id: `ack-${sequence}`,
      case_id: caseId,
      note: step.args.note ?? "",
    })
  } else if (step.tool === "request_evidence") {
    state.evidence_requests.push({
      id: `request-${sequence}`,
      case_id: caseId,
      detail: step.args.detail ?? "",
    })
  } else if (step.tool === "dismiss_resolved" && caseId && !state.dismissed_case_ids.includes(caseId)) {
    state.dismissed_case_ids.push(caseId)
  }
}
