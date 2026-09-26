# Backend

P0 decision and action API for Mulanous Lite. The product rules are in [the Canon](../docs/MULANOUS_LITE_CANON.md). This process implements:

```text
case → evidence → context → challenge → decide → validate → plan → human approval → synthetic execute
```

One FastAPI process. Synthetic CRM, Jira, Slack, and meeting fixtures live in `../data/`. Nothing writes to a live customer system.

## Run locally

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API is `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`. CORS is open so a local frontend on another port can call it.

Check the three cases:

```bash
curl -s http://127.0.0.1:8000/api/cases
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H 'content-type: application/json' \
  -d '{"case_id":"acme-sso-rollout"}'
```

A clean restart clears synthetic tasks, messages, and account risk notes. Case dispositions also reset because they live in process memory.

## LLM provider

| `OPENAI_API_KEY` | Behavior |
| --- | --- |
| unset or empty | Deterministic evidence reader. No network call. This is what the tests use. |
| set | OpenAI structured outputs (`response_format: json_schema`). Default model `gpt-4o-mini` (override with `OPENAI_MODEL`). The model must support structured outputs. |

Copy [`.env.example`](../.env.example) to `.env` in the repo root or `backend/.env`. Do not commit keys. The process reads the key from the environment and never logs it.

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
| `POST /api/actions/plan` | `{ "case_id": "..." }` → `ActionPlan` (`requires_approval: true`, nothing runs) |
| `POST /api/actions/execute` | `{ "plan_id": "...", "approved": true }` → `ActionResult` with before and after |
| `POST /api/investigate` | grounded read-only answer using `get_case`, `get_evidence`, `inspect_evidence`, `reanalyze_case` |

`POST /api/analyze` ignores extra fields. A missing or blank `case_id` is HTTP 400. An unknown case or evidence id or plan id is HTTP 404. Execute without `approved: true` is HTTP 400 and does not change state.

There is no confidence field and no risk score.

### Action behavior

Tools are only `create_task`, `send_message`, and `update_account_risk`.

- `VERIFY` plans an intervention.
- `SUPPRESS` plans no steps. Approved execute leaves synthetic state unchanged.
- `ABSTAIN` plans a request to gather or clarify. It does not record the commitment as verified.

Execute applies the stored plan only. The client cannot swap tools or arguments at execute time. A plan runs once.

## Layout

```text
app/adapters/     load data/*.json; a bad file drops that source only
app/evidence/     flat EvidenceRecord ids ({source}:{source_record_id})
app/context/      account filter, lexical relevance, recency, dedupe, cap of 12
app/reasoning/    prompt decision-v1, deterministic reader, optional OpenAI call
app/validation/   schema and grounding checks
app/actions/      plan and synthetic execute
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

Tests inject the deterministic reader or a scripted fake. They do not call OpenAI.

## Not in this process

Manufacturing and logistics packs, vector search, multi-agent frameworks, live OAuth, and a frontend. The investigate route is a grounded extension point for the P1 drawer, not a second model.
