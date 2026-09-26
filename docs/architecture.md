# Architecture

## Goal

Turn a reported enterprise account claim into a traceable follow-up decision. The prototype uses synthetic local fixtures so the same demo is reproducible and does not require access to private systems.

## Components

1. **Frontend (`frontend/`):** submit a claim and account ID; show the decision, rationale, and cited evidence. Syam can build against `frontend/mock-analysis.json` before the API is available.
2. **Backend (`backend/`):** implement `POST /api/analyze` per [the API contract](api-contract.md). Validate input, retrieve related source records, classify, and return the decision.
3. **Synthetic sources (`data/`):** CRM account context, Jira issues, Slack messages, and meeting notes. Records have stable IDs and account IDs for citation.

```text
Claim + account ID -> POST /api/analyze -> evidence lookup -> decision
                                                  |                |
                                          data/*.json       cited evidence
```

## Decision rules for the first pass

- `VERIFY`: relevant, current evidence supports an unresolved claim that merits human follow-up.
- `SUPPRESS`: relevant evidence shows the claim is resolved, outdated, or contradicted.
- `ABSTAIN`: no reliable decision can be made from the available evidence.

The service should expose its evidence and reasoning. It does not take action in CRM, Jira, or Slack. Source adapters and model-assisted reasoning can evolve behind the same contract.
