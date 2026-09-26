# Mulanous Lite — BPF 2026 prototype

Mulanous Lite helps an enterprise account team decide whether a reported account signal deserves follow-up. Important claims are scattered across CRM notes, Jira issues, Slack messages, and meeting notes; a single mention can be stale, duplicated, or contradicted.

**User:** Delivery / Operations Manager.

**Product freeze:** [PRODUCT_SPEC](docs/PRODUCT_SPEC.md) is the authoritative surface for BPF Day 1.

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

**Solution:** select a case and call `POST /api/analyze` with `{ "case_id": "acme-sso-rollout" }`. The service returns one validated decision: `VERIFY`, `SUPPRESS`, or `ABSTAIN`, with reason, recommended action, suggested owner, due hint, flat evidence records, `contradictions_checked` challenge results, and missing evidence. See [API contract](docs/api-contract.md).

**Architecture:** a small frontend calls one backend endpoint. The backend reads four local synthetic JSON datasets for the selected case and produces an explainable decision. See [architecture](docs/architecture.md), [API contract](docs/api-contract.md), and [demo flow](docs/demo-flow.md).

**Challenge disclosure:** this prototype is being built during BPF 2026. All checked-in enterprise inputs are synthetic. AI tools are used to help plan, write, and review the prototype. No private Mulanous source code or customer data belongs in this public repository.

## Layout

```text
backend/   API and decision logic (in progress)
frontend/  UI owned by Syam; can start from frontend/mock-analysis.json
data/      synthetic CRM, Jira, Slack, and meeting records
docs/      product freeze, architecture, demo flow, and API contract
```

## Team boundary

- Backend, AI, and synthetic data: prototype owner.
- Frontend: Syam, using the API contract and mock response.

[PRODUCT_SPEC](docs/PRODUCT_SPEC.md) and the [API contract](docs/api-contract.md) supersede the initial claim-string request for this frozen build. Changes to fields or decision meanings should be coordinated before either side updates code.
