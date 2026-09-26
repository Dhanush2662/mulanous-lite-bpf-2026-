# Architecture

## Goal

Help a Delivery / Operations Manager see what needs attention today and why. The prototype uses synthetic local fixtures so the same demo is reproducible and does not require access to private systems. The locked product surface is [PRODUCT_SPEC.md](PRODUCT_SPEC.md).

## Screens

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

Attention Today is a short queue of operational cases. Opening a case navigates to Case Brief. The Evidence Inspector and the optional P1 Investigate drawer stay on Case Brief. There is no sidebar, settings, connectors page, analytics page, or standalone chat page.

## Components

1. **Frontend (`frontend/`):** render Attention Today, then Case Brief. Call `POST /api/analyze` with the selected `case_id`. Show disposition, reason, recommended action, suggested owner, due hint, evidence, contradictions checked, and missing evidence. Open evidence in the embedded inspector. The P1 Investigate drawer, when present, stays on the same page.
2. **Backend (`backend/`):** implement `POST /api/analyze` per [the API contract](api-contract.md). Load the selected case, assemble fixture evidence, run analysis, validate the structured result, and return `AnalyzeResponse`.
3. **Synthetic sources (`data/`):** CRM account context, Jira issues, Slack messages, and meeting notes. Records have stable IDs used as `source_record_id` on each flat `EvidenceRecord`.

```text
Attention Today
  → case_id
  → POST /api/analyze
  → load fixtures (data/*.json)
  → assemble context
  → analyze evidence
  → validate
  → AnalyzeResponse on Case Brief
```

Canonical request:

```json
{
  "case_id": "acme-sso-rollout"
}
```

Evidence is a flat record (`id`, `source`, `source_record_id`, `title`, `body`, `observed_at`). `contradictions_checked` is an array of challenge results. Each `evidence_id` resolves to an evidence id in that same response. The response includes no confidence field and no risk score.

The three demo cases in the product spec share this pipeline. The service returns the validated model result for the selected case. It does not ship canned decision payloads, and it does not take action in CRM, Jira, or Slack.

## Decision states

- `VERIFY`: available evidence supports intervention.
- `SUPPRESS`: the suspected problem is contradicted or already resolved.
- `ABSTAIN`: available evidence is insufficient or conflicting.
