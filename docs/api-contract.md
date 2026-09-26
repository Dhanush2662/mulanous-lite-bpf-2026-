# API contract — frozen build

This contract supersedes the initial claim-string request (`account_id` + `claim`) for the frozen BPF Day 1 build. The authoritative product surface is [PRODUCT_SPEC.md](PRODUCT_SPEC.md).

Screens that consume this payload:

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

The Evidence Inspector and the P1 Investigate drawer stay on Case Brief. They are not separate pages.

## `POST /api/analyze`

Request body (`application/json`), `AnalyzeRequest`:

```json
{
  "case_id": "acme-sso-rollout"
}
```

`case_id` is a nonempty string that selects one seeded Attention Today case. `acme-sso-rollout` is the canonical id for the Acme SSO demo case. The only request field is `case_id`. Extra fields are ignored. Invalid JSON or a missing or blank `case_id` returns HTTP 400. An unknown case returns HTTP 404.

The service loads that case, assembles relevant fixture evidence, and returns a validated decision from the evidence pipeline in [PRODUCT_SPEC.md](PRODUCT_SPEC.md). The example below shows field shape only. Demo outcomes are computed for the selected case; this document does not define canned decision payloads.

## Types

```ts
interface EvidenceRecord {
  id: string;
  source: "crm" | "jira" | "slack" | "meetings";
  source_record_id: string;
  title: string;
  body: string;
  observed_at: string;
}

interface ChallengeResult {
  hypothesis: string;
  result: "supported" | "not_supported" | "inconclusive";
  evidence_ids: string[];
}
```

`EvidenceRecord.id` is `{source}:{source_record_id}`, for example `jira:JIRA-101`. `observed_at` is UTC ISO 8601. Provenance sits on these fields. Evidence items are flat records.

`contradictions_checked` is `ChallengeResult[]`. Every `evidence_id` must equal an `evidence[].id` in the same response. A response that cites an unknown evidence id is invalid.

## `AnalyzeResponse`

Successful response (`application/json`, HTTP 200):

```json
{
  "case_id": "acme-sso-rollout",
  "account": "Acme",
  "claim": "SSO rollout blocked",
  "decision": "VERIFY",
  "reason": "Open delivery evidence still shows an unresolved SAML mapping blocker.",
  "recommended_action": "Confirm the unresolved SAML mapping blocker with the delivery owner.",
  "suggested_owner": "Delivery owner",
  "due_hint": "Before today's customer checkpoint",
  "evidence": [
    {
      "id": "jira:JIRA-101",
      "source": "jira",
      "source_record_id": "JIRA-101",
      "title": "SSO rollout blocked by SAML mapping",
      "body": "The customer cannot complete SSO rollout until role mapping is corrected.",
      "observed_at": "2026-09-25T10:00:00Z"
    }
  ],
  "contradictions_checked": [
    {
      "hypothesis": "The SSO rollout blocker is already resolved.",
      "result": "not_supported",
      "evidence_ids": ["jira:JIRA-101"]
    }
  ],
  "missing_evidence": []
}
```

`case_id` echoes the selected case. `account` and `claim` are the case fields shown on Attention Today and Case Brief.

`decision` is exactly one of `VERIFY`, `SUPPRESS`, `ABSTAIN` (the Case Brief disposition).

- `reason` is a short human-readable explanation.
- `recommended_action` is the advisory next step for a human. The service does not write back to Jira, CRM, or other systems.
- `suggested_owner` names who should take that step.
- `due_hint` is a short timing hint, or `null` when the analysis has none.
- `evidence` is `EvidenceRecord[]`. It may be empty when the decision is `ABSTAIN`.
- `contradictions_checked` is `ChallengeResult[]`. It may be empty. Each `evidence_ids` entry resolves to `evidence` in this response.
- `missing_evidence` is an array of short statements describing evidence gaps. It may be empty, and it is expected when the decision is `ABSTAIN`.

This response has no confidence field and no risk score.

Error response:

```json
{"error": "Unknown case"}
```

The frontend renders this payload as an advisory Case Brief. Evidence opens in the embedded Evidence Inspector on that same page.
