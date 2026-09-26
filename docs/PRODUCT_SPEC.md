# Mulanous Lite — Product Spec

**Authority:** If this spec conflicts with [MULANOUS_LITE_CANON.md](MULANOUS_LITE_CANON.md), the Canon wins. Material product or architecture changes update the Canon first.

**Status:** FROZEN for BPF 2026 Day 1 (Builders' Pitch Fest)  
**Freeze target:** working demo by 4:30 PM IST; portal cutoff follows event schedule.

## User

Delivery / Operations Manager

## Job To Be Done

Tell me what needs my attention today — and prove why.

## Problem

Operational evidence required for intervention decisions is fragmented across
CRM, delivery systems, communication channels, and meetings.

Managers manually reconstruct this context before deciding whether something
actually needs intervention.

## Product Loop

ATTENTION
→ CONTEXT
→ CHALLENGE
→ DISPOSITION
→ ACTION

Optional P1 (same Case Brief, not a new page): INVESTIGATE (tool-using agent drawer)

## Screens (LOCKED)

```text
Attention Today
      ↓
Case Brief
      ↓
Evidence inspector (drawer/expand, NOT another page)
      +
Investigate with Mulanous (drawer, P1 — not a third page)
```

No sidebar. No settings. No connectors page. No analytics. No standalone chat product.

### 1. Attention Today

Shows a small queue of operational cases.

Each case contains:

- account
- claim
- urgency/time context
- source count
- current disposition if analyzed

Opening a case navigates to Case Brief.

### 2. Case Brief

Shows:

- account
- claim
- disposition
- reason
- recommended action
- suggested owner
- due hint (when present)
- evidence (with provenance)
- contradictions checked
- missing evidence where relevant

Evidence can be inspected without leaving the page.

### P1 — Investigation agent (embedded)

A **drawer inside Case Brief**, not an agent page and not a general chatbot.

Suggested prompts (examples):

- Why was this verified / suppressed / abstained?
- What evidence contradicts this?
- What would change this decision?
- Check whether the blocker is already resolved
- What information is missing?

Agent may use only case-scoped tools (`get_case`, `get_evidence`, `inspect_evidence`, `reanalyze_case`). Responses must be grounded in tool results. No write-back to enterprise systems.

## Decision States

**VERIFY**  
The available evidence supports intervention.

**SUPPRESS**  
The suspected problem is contradicted or already resolved.

**ABSTAIN**  
Available evidence is insufficient or conflicting.

## Advisory Boundary

Mulanous Lite recommends decisions.

It does not:

- modify Jira
- contact customers
- assign work
- close cases
- perform autonomous write-back

Human decides what happens next.

## Dynamic AI requirement (non-negotiable)

- Synthetic **fixtures may be seeded**.
- Disposition **must not** be keyed solely off claim string literals.
- Pipeline: selected case → load relevant fixtures → assemble context → AI analyzes evidence → structured output → **validator** → VERIFY / SUPPRESS / ABSTAIN.
- Challenge results and recommended action come from structured model output (then validated), not decorative UI copy or disposition templates alone.

## Demo cases (same engine, different outcomes)

1. **Acme — SSO rollout blocked** → expected **VERIFY**
2. **Globex — Export timeout escalation** → expected **SUPPRESS** (already resolved)
3. **Initech — Europe expansion at risk** → expected **ABSTAIN** (insufficient evidence)

## Build priority

**P0 (must ship):** Attention Today → Case Brief → dynamic VERIFY/SUPPRESS/ABSTAIN → evidence + provenance → recommended action + owner → contradictions / missing evidence.

**P1 (if P0 green):** Investigate drawer with ≥3 grounded tools.

**P2 (cut):** write-back, multi-agent frameworks, vector DB unless proven necessary, confidence %, analytics, extra pages.
