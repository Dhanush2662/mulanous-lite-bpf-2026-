import type { AnalyzeResponse } from "../types/api"

/** Fixture analyses captured from the local API. Used only when that API is down. */
export const FALLBACK_ANALYSES: Record<string, AnalyzeResponse> = {
  "acme-sso-rollout": {
    "case_id": "acme-sso-rollout",
    "account": "Acme",
    "claim": "SSO rollout blocked",
    "decision": "VERIFY",
    "reason": "Open evidence still shows an unresolved blocker (SSO group-to-role mapping has not shipped; SSO rollout blocked by SAML mapping; Customer checkpoint still expects SSO). The hypothesis that this is already resolved is not supported.",
    "recommended_action": "Confirm the unresolved blocker with the delivery owner and track it before the customer checkpoint.",
    "suggested_owner": "Delivery owner",
    "due_hint": "Before today's customer checkpoint",
    "evidence": [
      {
        "id": "jira:JIRA-103",
        "source": "jira",
        "source_record_id": "JIRA-103",
        "title": "SSO group-to-role mapping has not shipped",
        "body": "Status is open. The SSO group-to-role mapping fix has not shipped. The blocker remains open and there is no resolution.",
        "observed_at": "2026-09-25T11:15:00Z"
      },
      {
        "id": "jira:JIRA-101",
        "source": "jira",
        "source_record_id": "JIRA-101",
        "title": "SSO rollout blocked by SAML mapping",
        "body": "Status is open. The customer cannot complete the SSO rollout until role mapping is corrected. This blocker stops the committed rollout.",
        "observed_at": "2026-09-25T10:00:00Z"
      },
      {
        "id": "crm:CRM-002",
        "source": "crm",
        "source_record_id": "CRM-002",
        "title": "Customer checkpoint still expects SSO",
        "body": "Customer success confirmed the SSO rollout commitment is still due for today's customer checkpoint. The SAML mapping blocker is unresolved.",
        "observed_at": "2026-09-25T08:00:00Z"
      },
      {
        "id": "crm:CRM-001",
        "source": "crm",
        "source_record_id": "CRM-001",
        "title": "Q3 SSO commitment at risk",
        "body": "Acme committed to complete the SSO rollout before the September security review. The commitment is at risk while SAML role mapping is unresolved. No waiver has been recorded.",
        "observed_at": "2026-09-24T09:00:00Z"
      },
      {
        "id": "slack:SLACK-202",
        "source": "slack",
        "source_record_id": "SLACK-202",
        "title": "Escalation from customer success",
        "body": "The Acme champion asked for a same-day update on the SSO rollout. The SSO blocker is still blocked and unresolved ahead of the checkpoint.",
        "observed_at": "2026-09-25T14:05:00Z"
      },
      {
        "id": "slack:SLACK-201",
        "source": "slack",
        "source_record_id": "SLACK-201",
        "title": "Acme rollout update",
        "body": "Acme SSO is still blocked on SAML mapping. The platform team is investigating. The customer checkpoint is today.",
        "observed_at": "2026-09-25T13:30:00Z"
      },
      {
        "id": "meetings:MEETING-301",
        "source": "meetings",
        "source_record_id": "MEETING-301",
        "title": "Acme weekly check-in",
        "body": "A separate export question was closed last week. The SSO role-mapping blocker remains open and unresolved. The customer still expects the committed rollout.",
        "observed_at": "2026-09-25T16:00:00Z"
      },
      {
        "id": "meetings:MEETING-302",
        "source": "meetings",
        "source_record_id": "MEETING-302",
        "title": "Delivery standup",
        "body": "The delivery owner raised the Acme SSO blocker in standup. There is no resolution. The team will confirm the unresolved SAML mapping before today's customer checkpoint.",
        "observed_at": "2026-09-25T17:00:00Z"
      }
    ],
    "contradictions_checked": [
      {
        "hypothesis": "The reported issue is already resolved.",
        "result": "not_supported",
        "evidence_ids": [
          "jira:JIRA-103",
          "jira:JIRA-101",
          "crm:CRM-002",
          "crm:CRM-001"
        ]
      }
    ],
    "missing_evidence": []
  },
  "globex-export-timeout": {
    "case_id": "globex-export-timeout",
    "account": "Globex",
    "claim": "Export timeout escalation",
    "decision": "SUPPRESS",
    "reason": "Available evidence shows the issue is already resolved (Account health after the export fix; Export timeout follow-up closed; Customer sign-off on the export window). Intervention is not required.",
    "recommended_action": "Do not escalate. Leave the resolved issue closed unless new evidence appears.",
    "suggested_owner": "Delivery owner",
    "due_hint": null,
    "evidence": [
      {
        "id": "crm:CRM-111",
        "source": "crm",
        "source_record_id": "CRM-111",
        "title": "Account health after the export fix",
        "body": "Nightly exports are completing for Globex. The timeout incident is resolved. No further action was requested by the customer.",
        "observed_at": "2026-09-24T12:00:00Z"
      },
      {
        "id": "crm:CRM-110",
        "source": "crm",
        "source_record_id": "CRM-110",
        "title": "Export timeout follow-up closed",
        "body": "Globex raised an export timeout last week. The customer confirmed exports now complete within the agreed window. The issue is resolved and the escalation is closed.",
        "observed_at": "2026-09-24T09:30:00Z"
      },
      {
        "id": "jira:JIRA-211",
        "source": "jira",
        "source_record_id": "JIRA-211",
        "title": "Customer sign-off on the export window",
        "body": "Status is done. The customer signed off that the nightly export completes. The timeout incident is resolved.",
        "observed_at": "2026-09-23T18:00:00Z"
      },
      {
        "id": "jira:JIRA-210",
        "source": "jira",
        "source_record_id": "JIRA-210",
        "title": "Export timeout on large CSV",
        "body": "Status is resolved. The export timeout was corrected in release 4.2 and verified with the customer on 23 September 2026.",
        "observed_at": "2026-09-23T15:00:00Z"
      },
      {
        "id": "slack:SLACK-311",
        "source": "slack",
        "source_record_id": "SLACK-311",
        "title": "Closing the export escalation",
        "body": "No further action on the Globex export timeout. Do not reopen the incident. The customer is satisfied and the escalation is closed.",
        "observed_at": "2026-09-24T08:40:00Z"
      },
      {
        "id": "slack:SLACK-310",
        "source": "slack",
        "source_record_id": "SLACK-310",
        "title": "Globex export thread",
        "body": "The Globex export timeout is resolved. The customer confirmed the 23 September export succeeded. This thread can stay closed.",
        "observed_at": "2026-09-23T16:10:00Z"
      },
      {
        "id": "meetings:MEETING-410",
        "source": "meetings",
        "source_record_id": "MEETING-410",
        "title": "Globex export review",
        "body": "The customer said the export timeout is resolved and they do not need an escalation. Verification with the customer is complete.",
        "observed_at": "2026-09-24T10:00:00Z"
      },
      {
        "id": "meetings:MEETING-411",
        "source": "meetings",
        "source_record_id": "MEETING-411",
        "title": "Internal close-out",
        "body": "Delivery agreed the export timeout is already resolved. Do not reopen it and do not start a new intervention.",
        "observed_at": "2026-09-24T13:20:00Z"
      }
    ],
    "contradictions_checked": [
      {
        "hypothesis": "The issue still requires intervention.",
        "result": "not_supported",
        "evidence_ids": [
          "crm:CRM-111",
          "crm:CRM-110",
          "jira:JIRA-211",
          "jira:JIRA-210"
        ]
      }
    ],
    "missing_evidence": []
  },
  "initech-europe-expansion": {
    "case_id": "initech-europe-expansion",
    "account": "Initech",
    "claim": "Europe expansion at risk",
    "decision": "ABSTAIN",
    "reason": "The supplied evidence is insufficient to support or dismiss intervention (EU workspace note; Europe expansion idea; Renewal conversation mentioned Europe).",
    "recommended_action": "Gather a dated milestone, an accountable owner, and whether any delivery blocker exists before intervening.",
    "suggested_owner": "Account owner",
    "due_hint": null,
    "evidence": [
      {
        "id": "crm:CRM-211",
        "source": "crm",
        "source_record_id": "CRM-211",
        "title": "EU workspace note",
        "body": "The account team is exploring options for a Europe workspace. There is no scope and no milestone. Nothing is scheduled.",
        "observed_at": "2026-09-23T11:00:00Z"
      },
      {
        "id": "jira:JIRA-310",
        "source": "jira",
        "source_record_id": "JIRA-310",
        "title": "Europe expansion idea",
        "body": "Captured from a sales conversation about Europe expansion. The item is unscheduled. There are no acceptance criteria and no customer commitment date.",
        "observed_at": "2026-09-22T16:30:00Z"
      },
      {
        "id": "crm:CRM-210",
        "source": "crm",
        "source_record_id": "CRM-210",
        "title": "Renewal conversation mentioned Europe",
        "body": "Initech mentioned a possible Europe expansion during renewal. There is no signed commitment, no target date, and no owner for the idea.",
        "observed_at": "2026-09-22T15:00:00Z"
      },
      {
        "id": "meetings:MEETING-510",
        "source": "meetings",
        "source_record_id": "MEETING-510",
        "title": "Initech renewal chat",
        "body": "Europe expansion came up as a possibility. There was no decision, no date, and no delivery obstacle was identified. A follow-up was not scheduled.",
        "observed_at": "2026-09-23T14:00:00Z"
      },
      {
        "id": "slack:SLACK-411",
        "source": "slack",
        "source_record_id": "SLACK-411",
        "title": "Unclear Europe ask",
        "body": "The Europe expansion comment was a possibility only. No decision was made and no owner was named.",
        "observed_at": null
      },
      {
        "id": "meetings:MEETING-511",
        "source": "meetings",
        "source_record_id": "MEETING-511",
        "title": "Internal recap",
        "body": "The notes do not show whether Europe expansion is a real delivery commitment. They lack a milestone, an owner, and a target date. The claim is insufficient until those exist.",
        "observed_at": "2026-09-23T15:10:00Z"
      },
      {
        "id": "slack:SLACK-410",
        "source": "slack",
        "source_record_id": "SLACK-410",
        "title": "Europe aside",
        "body": "Someone said Initech might expand in Europe next year. No details were shared and no follow-up was booked.",
        "observed_at": "2026-09-22T17:45:00Z"
      }
    ],
    "contradictions_checked": [
      {
        "hypothesis": "A dated commitment, owner, and unresolved blocker support intervention.",
        "result": "inconclusive",
        "evidence_ids": [
          "crm:CRM-211",
          "jira:JIRA-310",
          "crm:CRM-210",
          "meetings:MEETING-510"
        ]
      }
    ],
    "missing_evidence": [
      "No evidence describes an unresolved delivery blocker.",
      "No evidence shows the issue was resolved and verified.",
      "No dated milestone or target date is established.",
      "No accountable owner is named."
    ]
  },
  "orion-order-5000": {
    "case_id": "orion-order-5000",
    "account": "Orion Components",
    "claim": "5,000 units due Monday",
    "decision": "VERIFY",
    "reason": "Open evidence still shows an unresolved blocker (Housing alloy shortage; Line 3 throughput drop; Committed order ORION-PO-5000). The hypothesis that this is already resolved is not supported.",
    "recommended_action": "Confirm the material shortage and quality hold with the production planner before Monday.",
    "suggested_owner": "Production planner",
    "due_hint": "Before Monday",
    "evidence": [
      {
        "id": "inventory:ORION-MAT-441",
        "source": "inventory",
        "source_record_id": "ORION-MAT-441",
        "title": "Housing alloy shortage",
        "body": "Inventory for the Monday commitment of 5,000 units. On-hand quantity is 1200. Required quantity is 5000. Status is short. Housing alloy material shortage is unresolved. The production planner cannot complete the order.",
        "observed_at": "2026-09-25T11:30:00Z"
      },
      {
        "id": "schedule:ORION-LINE-3",
        "source": "schedule",
        "source_record_id": "ORION-LINE-3",
        "title": "Line 3 throughput drop",
        "body": "Line 3 throughput drop. The line is behind the committed 5,000 units due Monday. Status is behind. This blocker is unresolved and the line cannot complete the order.",
        "observed_at": "2026-09-25T11:00:00Z"
      },
      {
        "id": "erp:ORION-PO-5000",
        "source": "erp",
        "source_record_id": "ORION-PO-5000",
        "title": "Committed order ORION-PO-5000",
        "body": "Committed order for Orion Components: 5,000 units due Monday. Order quantity is 5000. Commitment date is Monday. Status is open. Production planner owns the order. The commitment is unresolved.",
        "observed_at": "2026-09-25T09:00:00Z"
      },
      {
        "id": "quality:ORION-QA-17",
        "source": "quality",
        "source_record_id": "ORION-QA-17",
        "title": "Quality hold on the Orion run",
        "body": "Quality hold remains open on the Orion run. The hold is a blocker. The line cannot complete the 5,000 units due Monday.",
        "observed_at": "2026-09-25T13:00:00Z"
      },
      {
        "id": "quality:ORION-QA-18",
        "source": "quality",
        "source_record_id": "ORION-QA-18",
        "title": "Ops escalation before Monday",
        "body": "Ops escalation comment: the quality hold and material shortage are still open ahead of Monday. Production planner was told the units cannot complete.",
        "observed_at": "2026-09-25T15:10:00Z"
      }
    ],
    "contradictions_checked": [
      {
        "hypothesis": "The reported issue is already resolved.",
        "result": "not_supported",
        "evidence_ids": [
          "inventory:ORION-MAT-441",
          "schedule:ORION-LINE-3",
          "erp:ORION-PO-5000",
          "quality:ORION-QA-17"
        ]
      }
    ],
    "missing_evidence": []
  }
}
