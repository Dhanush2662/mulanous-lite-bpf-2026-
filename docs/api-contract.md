# API contract — frozen for initial build

## `POST /api/analyze`

Request body (`application/json`):

```json
{
  "account_id": "acme-001",
  "claim": "The SSO rollout is blocked for Acme."
}
```

`account_id` is a nonempty string matching a synthetic CRM account. `claim` is a nonempty plain-language string, at most 1000 characters. Extra fields are ignored. Invalid JSON or missing/invalid fields return HTTP 400. An unknown account returns HTTP 404.

Successful response (`application/json`, HTTP 200):

```json
{
  "account_id": "acme-001",
  "claim": "The SSO rollout is blocked for Acme.",
  "decision": "VERIFY",
  "reason": "Recent source records show an unresolved SSO rollout blocker.",
  "evidence": [
    {
      "source": "jira",
      "id": "JIRA-101",
      "title": "SSO rollout blocked by SAML mapping",
      "url": null,
      "observed_at": "2026-09-25T10:00:00Z"
    }
  ]
}
```

`decision` is exactly one of `VERIFY`, `SUPPRESS`, `ABSTAIN`. `reason` is a short human-readable explanation. `evidence` is an array and may be empty for `ABSTAIN`. `source` is one of `crm`, `jira`, `slack`, `meetings`; `id` refers to a checked-in source record. `url` is a string or `null`; no real enterprise links are used in the synthetic fixtures. All timestamps use UTC ISO 8601.

Error response:

```json
{"error": "Invalid claim"}
```

The frontend should render the decision as advisory and display the cited records. It should not infer certainty from the decision label alone.
