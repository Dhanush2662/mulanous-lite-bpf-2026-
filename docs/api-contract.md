# API contract — frozen build

This contract supersedes the initial claim-string request (`account_id` + `claim`) for the frozen BPF Day 1 build. The authoritative product surface is [PRODUCT_SPEC.md](PRODUCT_SPEC.md).

## `POST /api/analyze`

Request body (`application/json`), `AnalyzeRequest`:

```json
{
  "case_id": "acme-sso-rollout"
}
```

`case_id` is a nonempty string that selects one seeded Attention Today case. The example id above illustrates the request shape for the Acme SSO demo case. The only request field is `case_id`. Extra fields are ignored. Invalid JSON or a missing or blank `case_id` returns HTTP 400. An unknown case returns HTTP 404.

The service loads that case, assembles relevant fixture evidence, and returns a validated decision from the evidence pipeline in [PRODUCT_SPEC.md](PRODUCT_SPEC.md). Expected demo outcomes are listed there.

Successful response (`application/json`, HTTP 200), `AnalyzeResponse`:

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
      "body": "SSO rollout remains at risk while SAML role mapping is unresolved.",
      "provenance": {
        "source": "crm",
        "record_id": "CRM-001",
        "title": "Q3 account risk note",
        "observed_at": "2026-09-24T09:00:00Z",
        "url": null
      }
    }
  ],
  "contradictions_checked": [
    "Checked whether a later record already closed the SAML mapping blocker."
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
- `evidence` cites records the decision relies on. Each item has `body` (the relevant text) and `provenance`. Provenance includes `source` (`crm`, `jira`, `slack`, or `meetings`), `record_id` (a checked-in source record), `title`, `observed_at` (UTC ISO 8601, or `null` when the source has no timestamp), and `url` (a string or `null`; synthetic fixtures do not use real enterprise links). The array may be empty when the decision is `ABSTAIN`.
- `contradictions_checked` is an array of short statements describing contradictions or resolutions that were checked. It may be empty.
- `missing_evidence` is an array of short statements describing evidence gaps. It may be empty, and it is expected when the decision is `ABSTAIN`.

Confidence is omitted. The product spec lists it under P2.

Error response:

```json
{"error": "Unknown case"}
```

The frontend renders this payload as an advisory Case Brief. It does not infer certainty beyond the decision and the cited evidence.
