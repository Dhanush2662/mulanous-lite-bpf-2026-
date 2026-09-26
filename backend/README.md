# Backend

P0 decision and action API for Mulanous Lite. The product rules are in [the Canon](../docs/MULANOUS_LITE_CANON.md). This process implements:

```text
case → evidence → hybrid context → challenge → decide → validate → plan → policy or human approval → synthetic execute
```

One FastAPI process. Software fixtures live in `../data/`. The manufacturing pack lives in `../domain_packs/manufacturing/`. Nothing writes to a live customer system. There is no connectors admin.

## Run locally without Atlas

From the repository root, leave `MONGODB_URI` empty:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API is `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`. CORS is open so a local frontend on another port can call it.

The process loads the checked-in fixtures into an in-memory store and still runs hybrid retrieval: structured metadata filters for exact facts, and local vectors for Slack, meetings, and quality notes.

```bash
curl -s http://127.0.0.1:8000/api/cases
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"acme-sso-rollout"}'
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"orion-order-5000"}'
```

A clean restart clears synthetic tasks, messages, manufacturing expedites, and queue dismissals. Case dispositions also reset because they live in process memory.

## Run locally with MongoDB Atlas

Copy [`.env.example`](../.env.example) to `.env` in the repo root or `backend/.env`. Set `MONGODB_URI`. Do not commit the URI. Optional: `MONGODB_DB` (default `mulanous_lite`) and `ATLAS_VECTOR_INDEX` (default `evidence_vector`).

On startup the process pings Atlas and upserts cases, evidence, and later action records into the `cases`, `evidence`, and `actions` collections. If the ping fails, it logs the error type and keeps serving from the in-memory fixtures. The URI is never logged.

Create a vector search index named `evidence_vector` on `evidence.embedding` before the demo if you want Atlas Vector Search itself. Dimensions are 64 and similarity is cosine. Filter fields are `account_id`, `domain`, and `retrieval_class`. If that index is missing, semantic retrieval falls back to the same cosine ranking inside the account and domain filter. Exact facts never use that ranking.

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 64,
      "similarity": "cosine"
    },
    { "type": "filter", "path": "account_id" },
    { "type": "filter", "path": "domain" },
    { "type": "filter", "path": "retrieval_class" }
  ]
}
```

Structured sources (`crm`, `jira`, `erp`, `schedule`, `inventory`) are stored without an embedding. Semantic sources (`slack`, `meetings`, `quality`) are embedded. With `OPENAI_API_KEY` set, embeddings use `text-embedding-3-small` at `EMBEDDING_DIMENSIONS` (default 64). Without that key, embeddings are a deterministic local hash so the demo still runs.

## LLM provider

| `OPENAI_API_KEY` | Behavior |
| --- | --- |
| unset or empty | Deterministic evidence reader and local embeddings. No network call. This is what the tests use. |
| set | OpenAI structured outputs (`response_format: json_schema`) and OpenAI embeddings. Default decision model `gpt-4o-mini` (override with `OPENAI_MODEL`). The model must support structured outputs. |

The reader and the live model share one validator. The decision is not a `case_id` lookup. If model output does not match the schema, cites an unknown evidence id, or otherwise fails grounding, the service makes one repair call and then returns a safe `ABSTAIN`.

## Endpoints

Error body: `{"error": "..."}`.

| Method and path | Success |
| --- | --- |
| `GET /api/cases` | `Case[]` |
| `GET /api/cases/{id}` | `Case` |
| `GET /api/cases/{id}/evidence?source=&q=` | assembled `EvidenceRecord[]` |
| `GET /api/evidence/{id}` | one `EvidenceRecord` (`jira:JIRA-101`) |
| `POST /api/analyze` | `{ "case_id": "..." }` → `AnalyzeResponse` |
| `POST /api/actions/plan` | `{ "case_id": "..." }` → `ActionPlan` |
| `POST /api/actions/execute` | `{ "plan_id": "...", "approved": true }` → `ActionResult` with before and after |
| `POST /api/investigate` | grounded read-only answer using `get_case`, `get_evidence`, `inspect_evidence`, `reanalyze_case` |

`POST /api/analyze` ignores extra fields. A missing or blank `case_id` is HTTP 400. An unknown case or evidence id or plan id is HTTP 404. Execute without `approved: true` is HTTP 400 and does not change state.

There is no confidence field and no risk score. Embeddings are not API fields.

### Action behavior

Low-risk internal tools may auto-apply at plan time: `dismiss_resolved`, `acknowledge`, `request_evidence`. `ActionPlan.requires_approval` is false for those plans. A later execute of the same plan is HTTP 409.

State-changing tools still wait for approval. Plan does not execute them.

- `VERIFY` on software plans `create_task`, `send_message`, and `update_account_risk`.
- `VERIFY` on manufacturing plans `expedite_material`, `notify_planner`, and `update_order_risk`.
- `SUPPRESS` plans `dismiss_resolved` only. It does not create tasks, messages, or risk notes.
- `ABSTAIN` plans `request_evidence` only. It does not treat the commitment as verified.

Execute applies the stored plan only. The client cannot swap tools or arguments at execute time. A plan runs once.

## Layout

```text
app/adapters/     load data/*.json and domain_packs/*; a bad file drops that source only
app/evidence/     normalize, hybrid store, embeddings, optional Atlas client
app/context/      structured filters plus semantic rank, dedupe, cap of 12
app/reasoning/    prompt decision-v2, deterministic reader, optional OpenAI call
app/validation/   schema and grounding checks
app/actions/      plan, low-risk policy, and synthetic execute
app/investigate/  P1 read tools and a deterministic grounded answer
app/api/          HTTP routes
app/schemas/      Pydantic models
```

`AssembledContext` is the only evidence pack the decision call sees. `ActionStep` is a planned action. The wire names match the Canon (`ActionPlan`, `ActionResult`).

## Tests

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check app tests
```

Tests force the in-memory store and the deterministic embedder. They do not call OpenAI and they do not require Atlas. An `MONGODB_URI` or `OPENAI_API_KEY` in the environment does not change that.

## Not in this process

A connectors admin, OAuth connector product, logistics pack, multi-agent framework, and a frontend. The investigate route is a grounded extension point for the P1 drawer, not a second model.
