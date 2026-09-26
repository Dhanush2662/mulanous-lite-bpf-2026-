# Mulanous Lite — BPF 2026 prototype

Mulanous Lite helps an enterprise account team decide whether a reported account signal deserves follow-up. Important claims are scattered across CRM notes, Jira issues, Slack messages, and meeting notes; a single mention can be stale, duplicated, or contradicted.

**User:** an account owner or customer success lead reviewing a customer claim before acting on it.

**Solution:** submit a claim and account ID to `POST /api/analyze`. The service gathers related evidence from synthetic source data and returns one decision: `VERIFY` (supported and worth checking with the owner), `SUPPRESS` (already resolved or contradicted), or `ABSTAIN` (insufficient evidence). Each decision includes a short reason and cited source records. The frontend can use the checked-in response example while the backend is built.

**Architecture:** a small frontend calls one backend endpoint. The backend reads four local synthetic JSON datasets, matches records for the account and claim, and produces an explainable decision. See [architecture](docs/architecture.md), [API contract](docs/api-contract.md), and [demo flow](docs/demo-flow.md).

**Challenge disclosure:** this prototype is being built during BPF 2026. All checked-in enterprise inputs are synthetic. AI tools are used to help plan, write, and review the prototype. No private Mulanous source code or customer data belongs in this public repository.

## Layout

```text
backend/   API and decision logic (in progress)
frontend/  UI owned by Syam; can start from frontend/mock-analysis.json
data/      synthetic CRM, Jira, Slack, and meeting records
docs/      architecture, demo flow, and frozen API contract
```

## Team boundary

- Backend, AI, and synthetic data: prototype owner.
- Frontend: Syam, using the API contract and mock response.

The contract is frozen for the first implementation pass. Changes to its fields or decision meanings should be coordinated before either side updates code.
