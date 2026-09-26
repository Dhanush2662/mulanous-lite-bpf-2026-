# Mulanous Lite — BPF 2026 prototype

**Authority:** [docs/MULANOUS_LITE_CANON.md](docs/MULANOUS_LITE_CANON.md) is the single source of truth. If this README conflicts with it, the Canon wins.

Mulanous Lite helps an enterprise account team decide whether a reported account signal deserves follow-up. Important claims are scattered across CRM notes, Jira issues, Slack messages, and meeting notes; a single mention can be stale, duplicated, or contradicted.

**User:** Delivery / Operations Manager.

**Product freeze:** [PRODUCT_SPEC](docs/PRODUCT_SPEC.md) is the Day 1 surface note. The Canon wins on conflict.

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

**Solution:** select a case and call `POST /api/analyze` with `{ "case_id": "acme-sso-rollout" }`. The service returns one validated decision: `VERIFY`, `SUPPRESS`, or `ABSTAIN`, with reason, recommended action, suggested owner, due hint, flat evidence records, `contradictions_checked` challenge results, and missing evidence. See [API contract](docs/api-contract.md).

**Architecture:** the frontend calls the decision and action API. The backend reads synthetic JSON fixtures for the selected case and produces an explainable decision. See [architecture](docs/architecture.md), the [Canon](docs/MULANOUS_LITE_CANON.md), and [demo flow](docs/demo-flow.md).

## Run locally

Leave `MONGODB_URI` empty so the API uses in-memory fixtures.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:41731`. The UI reads `NEXT_PUBLIC_API_BASE_URL` (default `http://127.0.0.1:8000`). See [frontend/README.md](frontend/README.md) and [backend/README.md](backend/README.md).

**Challenge disclosure:** this prototype is being built during BPF 2026. All checked-in enterprise inputs are synthetic. AI tools are used to help plan, write, and review the prototype. No private Mulanous source code or customer data belongs in this public repository.

## Layout

```text
backend/   Python FastAPI decision and action API
ingest/    Go fixture ingest into MongoDB Atlas (no connector admin)
frontend/  Attention Today and Case Brief, calling the API
data/      synthetic CRM, Jira, Slack, and meeting records
docs/      product freeze, architecture, demo flow, and API contract
```

## Team boundary

- Backend, AI, and synthetic data: prototype owner.
- Frontend: Syam, using the API contract and mock response.

[PRODUCT_SPEC](docs/PRODUCT_SPEC.md) and the [API contract](docs/api-contract.md) supersede the initial claim-string request for this frozen build. Changes to fields or decision meanings should be coordinated before either side updates code.
