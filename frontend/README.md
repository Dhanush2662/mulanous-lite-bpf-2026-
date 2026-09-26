# Frontend

Vite, React, and TypeScript. Two routes:

```text
Attention Today
→ Case Brief
    ├── Evidence Inspector drawer
    └── Take Action drawer
```

`VITE_API_BASE` defaults to `http://127.0.0.1:8000`. Copy [`.env.example`](.env.example) if the API is elsewhere. If the service is down or the queue is empty, the UI uses a typed fallback captured from the fixture API.

```bash
cd frontend
npm install
npm run dev
```

The dev server listens on `http://127.0.0.1:41731`. Start the API first. See [backend/README.md](../backend/README.md). With `MONGODB_URI` empty, the API serves the checked-in synthetic fixtures.

# Frontend handoff

Syam owns the UI. Build the locked path:

```text
Attention Today
→ Case Brief
→ embedded Evidence Inspector
→ optional P1 Investigate drawer
```

The Evidence Inspector and the optional P1 Investigate drawer stay on Case Brief. Do not add a sidebar, settings, connectors, analytics, or a standalone chat page.

The analyze request is:

```http
POST /api/analyze
```

```json
{
  "case_id": "acme-sso-rollout"
}
```

Use [the API contract](../docs/api-contract.md) as the source of truth. Render `decision`, `reason`, `recommended_action`, `suggested_owner`, `due_hint`, `evidence`, `contradictions_checked`, and `missing_evidence`.

Each evidence item is a flat record: `id`, `source`, `source_record_id`, `title`, `body`, `observed_at`. `contradictions_checked` is an array of `{ hypothesis, result, evidence_ids }`. Every `evidence_id` matches an `evidence[].id` in that response. Do not render a confidence or risk score.

[`mock-analysis.json`](mock-analysis.json) matches that response shape so layout can start before the API is ready. The running demo still calls `POST /api/analyze` for the selected case.
