# Ingest

Go worker that reads the checked-in synthetic fixtures and upserts them into the MongoDB Atlas collections the Python decision API reads.

This is fresh Lite code. It does not vendor or copy another repository. It does not open a connectors admin and it does not perform OAuth.

## What it writes

| Collection | Document |
| --- | --- |
| `cases` | `id`, `domain`, `pattern`, `account`, `account_id`, `claim`, `urgency`, `ingest_order` |
| `evidence` | `id` (`source:source_record_id`), `source`, `source_record_id`, `account_id`, `domain`, `title`, `body`, `observed_at`, `retrieval_class`, `facts`, `embedding` |

`embedding` is null. Slack, meetings, and quality are `retrieval_class: semantic`. CRM, Jira, ERP, schedule, and inventory are `structured`. The Python process fills semantic vectors when it reads the collection.

Sources:

- `data/`: CRM, Jira, Slack, meetings, and the three software cases
- `domain_packs/manufacturing/`: ERP, production schedule, inventory, quality notes, and `orion-order-5000`

## Run

From the repository root, with `MONGODB_URI` set in the environment or in `.env`:

```bash
make ingest
```

The same command from `ingest/`:

```bash
go run ./cmd/ingest
```

Optional: `MONGODB_DB` (default `mulanous_lite`).

If `MONGODB_URI` is missing, the command exits 1 and prints `MONGODB_URI is required`. It does not start an in-memory store. If Atlas cannot be reached, it exits 1 with `atlas unavailable` and does not print the URI.

Then start the Python API. When the `evidence` collection already has rows, the API reads those documents instead of overwriting them from the fixture files. If the collection is empty, the API seeds it from the files. If `MONGODB_URI` is unset, the API keeps using the in-memory fixtures.

Restart the API after a later ingest so it can fill any semantic embeddings the worker left null.
