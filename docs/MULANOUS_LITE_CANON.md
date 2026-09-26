# Mulanous Lite Canon

**Status:** AUTHORITATIVE SINGLE SOURCE OF TRUTH for the Mulanous Lite BPF 2026 build.  
**Product and architecture:** FROZEN until P0 works.  
**Internal freeze:** 4:30 PM IST.

This document is authoritative. If the README, `PRODUCT_SPEC.md`, architecture notes, API docs, frontend docs, agent instructions, or implementation notes conflict with this file, `docs/MULANOUS_LITE_CANON.md` wins. Any material product or architecture change updates this document first, then the other docs.

Mulanous Lite is a challenge-built abstraction. It is not intended to become a separate long-term product. Keep the boundaries clean enough to merge into Mulanous later. The short-term goal is the strongest working Enterprise AI prototype for Builders' Pitch Fest: qualify for the next round and for incubation. Do not broaden the product beyond what this Canon freezes.

---

## 1. Product definition

| | |
| --- | --- |
| Product | Mulanous Lite |
| Category | Operational Decision + Action Agent |
| Primary user | Delivery / Operations Manager |
| Primary question | "What needs my attention today, why, and what should I do about it?" |

**Problem.** Operational evidence is fragmented across CRM, delivery systems, communication, and meetings. Managers reconstruct that context by hand before they can decide whether a commitment needs intervention, is already resolved, is insufficiently evidenced, or needs a specific next action.

**Out of scope.** Enterprise search, RAG-only question answering, document summarization, a generic chatbot, and an analytics dashboard. Also out of scope: a connectors admin, a workflow builder, a settings or auth product, and a separate UI per industry.

---

## 2. Core product loop

```text
ATTENTION → INVESTIGATE → CONTEXT → CHALLENGE → DECIDE → PLAN ACTION → HUMAN APPROVAL → EXECUTE
```

The demo must prove three behaviors with the same engine:

| Disposition | Meaning | What it proves |
| --- | --- | --- |
| `VERIFY` | Evidence is sufficient and consistent enough to support intervention. | When to act. |
| `SUPPRESS` | The suspected issue was checked. Available evidence shows it is already resolved, contradicted, or does not require intervention. | When not to act. |
| `ABSTAIN` | Evidence is missing, internally conflicting, or otherwise insufficient. The system must not force a finding. | When to ask for more evidence. |

`VERIFY`, `SUPPRESS`, and `ABSTAIN` are the only terminal analysis states. There is no confidence percentage and no risk score.

P0 runs attention, context, challenge, decision, action plan, human approval, and synthetic execute. Challenge in P0 is the contradiction check inside the decision pipeline. The user-driven Investigate drawer is the P1 expression of the INVESTIGATE stage. It is not a third page, and P0 does not wait on it.

---

## 3. Primary use case and cross-industry proof

**P0 judged wedge.** Enterprise Delivery / Operations → Customer Commitment Intervention.

Software / SaaS fixtures only: CRM, Jira, Slack, and meetings. All of them are synthetic.

**Same engine, same UI.** Industry proof is a domain pack, not a new product and not a new frontend.

| Priority | Pack | Pattern | Synthetic sources | Gate |
| --- | --- | --- | --- | --- |
| P0 | `software` | `customer_commitment_intervention` | CRM, Jira, Slack, meetings | Required demo |
| P1 | `manufacturing` | `production_commitment_risk` | ERP/order, production schedule, inventory/material, quality notes | Required only after P0 is stable |
| P1.5 | `logistics` | `delivery_commitment_risk` | TMS, carrier, ETA, SLA | Optional, and only if it fits in the remaining time (about 20 minutes) without risking P0 |

Pack layout:

```text
domain_packs/software/         fixtures + pattern + action tools
domain_packs/manufacturing/
domain_packs/logistics/
```

Core stays assemble, reason, validate, investigate, and actions. A case declares `domain` and `pattern`. The core does not grow industry-specific screens.

Do not delay P0 for industry packs. Do not build real SAP, MES, or TMS connectors. Do not build a domain-specific frontend.

Checked-in software fixtures may stay in `data/` until a move into `domain_packs/software/` is cheap. That move must not block P0. New manufacturing and logistics fixtures belong under their pack directories.

---

## 4. Product surface (locked)

Two screens only.

```text
Attention Today
      ↓
Case Brief
      ├── Evidence Inspector   (embedded)
      ├── Investigate drawer   (embedded, P1)
      └── Take Action drawer   (embedded)
```

No third page. Cut settings, admin, connectors, analytics, a chatbot page, a workflow builder, and auth complexity. No sidebar.

### Attention Today

A short queue of operational cases. Each row shows:

- account
- claim
- urgency / time context
- source count
- current disposition, if the case has been analyzed

Opening a row navigates to Case Brief.

### Case Brief

One page for the open case. It shows:

- account
- claim
- decision (disposition)
- reason
- recommended action
- owner
- due hint, when present
- evidence, with provenance
- contradictions checked
- missing evidence, where relevant
- advisory boundary

Evidence opens in the Evidence Inspector on this page. Investigation opens in a drawer on this page. Action planning, approval, and the execution result open in the Take Action drawer on this page.

### Advisory boundary

Mulanous Lite recommends a decision and a plan. A human must approve before any state-changing tool runs. Execution touches synthetic tools only. The product does not write to live CRM, Jira, Slack, SAP, MES, TMS, or any other production system, and it does not contact a real customer.

---

## 5. Screens in one sentence each

**Attention Today** answers "what needs me today?"  
**Case Brief** answers "why, what did we challenge, what is the decision, and what action is waiting for my approval?"

---

## 6. What is embedded, not a page

| Surface | Where it lives | Job |
| --- | --- | --- |
| Evidence Inspector | Case Brief | Show one flat evidence record: source, record id, title, body, `observed_at`. |
| Investigate drawer | Case Brief, P1 | Case-scoped questions. Grounded tool use. Not a blank chat. |
| Take Action drawer | Case Brief | Show the plan, take explicit approval, run synthetic tools, show before and after. |

---

## 7. Decision Agent

Pipeline:

```text
case → retrieve → assemble → model → contradictions → structured output → validator → disposition
```

### AI responsibilities

The model may:

- extract facts from supplied evidence
- identify relationships
- interpret unstructured text
- connect evidence across sources
- identify contradictions and state challenge hypotheses
- propose explanations
- recommend an action, owner, and due hint
- return structured output that matches the schema

The model must not:

- fabricate source evidence
- invent source ids
- pretend missing data exists
- bypass the validator
- send unstructured prose to the frontend
- choose a disposition by looking up `case_id` or the claim string

### Deterministic responsibilities

Code, not the model, must:

- load the case and the pack fixtures
- assemble context only from those records
- schema-validate model output
- resolve every evidence reference to a real record for that case
- reject unresolved references
- retry a safe validation failure, or return `ABSTAIN` / a controlled error
- refuse to coerce malformed model output into a decision
- keep action execution behind the approval gate

Prompts are versioned, explicit, grounded in the supplied evidence, and constrained to schema output.

---

## 8. Investigation Agent

Drawer only. Not a chatbot page. Not an open-ended assistant.

Allowed tools:

| Tool | Effect |
| --- | --- |
| `get_case` | Read the open case. |
| `get_evidence` | Read evidence assembled for that case. |
| `inspect_evidence` | Read one evidence record by id. |
| `reanalyze_case` | Run the Decision Agent pipeline again for that case. |

Every answer must be grounded in tool results. Suggested prompts stay on the open case, for example: why this disposition, what contradicts it, what would change it, whether the blocker is already resolved, and what information is missing.

The Investigation Agent has no write tools and no path to live systems.

---

## 9. Action Agent

Sequence for every state-changing tool:

```text
PLAN → SHOW → APPROVE → EXECUTE → RESULT
```

The plan is shown in the Take Action drawer before anything runs. Approval is an explicit human action. Execute applies only that stored plan, and only to synthetic tools. The drawer shows before state and after state in the demo.

P0 software tools:

| Tool | Synthetic effect |
| --- | --- |
| `create_task` | Create a local task (`title`, `owner`, `detail`, `case_id`). |
| `send_message` | Record a local message (`recipient`, `body`, `case_id`). The recipient is a synthetic role, such as "Delivery owner". |
| `update_account_risk` | Record a local account risk note (`account`, `risk_note`, `case_id`). |

Manufacturing and logistics packs may register domain-appropriate tool variants later. Those names stay inside the pack. They use the same plan → show → approve → execute gate. They still hit synthetic state only.

Disposition behavior:

- `VERIFY` may plan state-changing tools.
- `SUPPRESS` plans no intervention. The honest result is unchanged state.
- `ABSTAIN` may plan a request to collect the missing evidence. It must not act as if the commitment were verified.

---

## 10. Synthetic environment

Synthetic CRM, Jira, Slack, and meeting records are the P0 enterprise environment. The UI and the pitch must not describe them as live production connectors.

Software evidence sources are `crm`, `jira`, `slack`, and `meetings`. Later packs add their own source strings without forking the evidence shape and without a new screen.

---

## 11. Demo cases

Three software cases are the fixture and test expectations. They share one pipeline.

| Case | `case_id` | Claim | Fixture expectation |
| --- | --- | --- | --- |
| Acme | `acme-sso-rollout` | SSO rollout blocked | `VERIFY` |
| Globex | `globex-export-timeout` | Export timeout escalation | `SUPPRESS` (already resolved) |
| Initech | `initech-europe-expansion` | Europe expansion at risk | `ABSTAIN` (insufficient evidence) |

`acme-sso-rollout` was already the analyze contract's canonical id. `globex-export-timeout` and `initech-europe-expansion` are assigned here so fixtures and tests have stable ids.

Tests may expect those dispositions from the seeded evidence. Implementation must not hardcode `case_id` or claim text to a decision. If the fixtures change, the label is recomputed. A response that can only be produced by a lookup table is not a valid demo.

---

## 12. Data model

No confidence field. No risk score. Evidence is flat. `observed_at` is `string | null` (UTC ISO 8601, or `null` when the source record has no timestamp). Do not invent timestamps. Do not nest a provenance object.

```ts
type Disposition = "VERIFY" | "SUPPRESS" | "ABSTAIN";

interface Case {
  id: string;
  domain: "software" | "manufacturing" | "logistics";
  pattern: string;
  account: string;
  claim: string;
  urgency: string;
  source_count: number;
  disposition: Disposition | null;
}

interface EvidenceRecord {
  id: string; // "{source}:{source_record_id}"
  source: string; // P0: "crm" | "jira" | "slack" | "meetings"
  source_record_id: string;
  title: string;
  body: string;
  observed_at: string | null;
}

interface ChallengeResult {
  hypothesis: string;
  result: "supported" | "not_supported" | "inconclusive";
  evidence_ids: string[];
}

interface AnalyzeResponse {
  case_id: string;
  account: string;
  claim: string;
  decision: Disposition;
  reason: string;
  recommended_action: string;
  suggested_owner: string;
  due_hint: string | null;
  evidence: EvidenceRecord[];
  contradictions_checked: ChallengeResult[];
  missing_evidence: string[];
}
```

`EvidenceRecord.id` example: `jira:JIRA-101`.

`Case.disposition` is `null` until a validated analysis exists. Attention Today reads `account`, `claim`, `urgency`, `source_count`, and `disposition`. `id`, `domain`, and `pattern` are engine fields, not extra screens.

P1 queue state: after analyze, the queue returns the stored disposition. After an approved execute, the case may include `last_action_status` of `"none"` or `"executed"` so the same row can show that a synthetic action was applied. That is not a new column family and not a new page.

Action objects:

```ts
interface ActionStep {
  tool: string;
  summary: string;
  args: Record<string, string>;
}

interface SyntheticState {
  tasks: Array<{ id: string; title: string; owner: string; case_id: string }>;
  messages: Array<{ id: string; recipient: string; body: string; case_id: string }>;
  account_risks: Array<{ account: string; risk_note: string; case_id: string }>;
}

interface ActionPlan {
  plan_id: string;
  case_id: string;
  steps: ActionStep[];
  requires_approval: true;
  before_state: SyntheticState;
}

interface ActionResult {
  plan_id: string;
  case_id: string;
  status: "executed";
  results: Array<{ tool: string; summary: string }>;
  before_state: SyntheticState;
  after_state: SyntheticState;
}
```

Synthetic state lives in the one demo process. A clean restart may clear it. Within a session, before and after must both be visible.

---

## 13. HTTP endpoints

One process. JSON in, JSON out. Error body: `{ "error": string }`.

| Method and path | Request | Success |
| --- | --- | --- |
| `GET /api/cases` | — | `Case[]` |
| `GET /api/cases/:id` | — | `Case` |
| `GET /api/cases/:id/evidence` | — | `EvidenceRecord[]` assembled for that case |
| `GET /api/evidence/:id` | — | one `EvidenceRecord` |
| `POST /api/analyze` | `{ "case_id": string }` | `AnalyzeResponse` |
| `POST /api/investigate` | `{ "case_id": string, "message": string }` | grounded answer, see below |
| `POST /api/actions/plan` | `{ "case_id": string }` | `ActionPlan` |
| `POST /api/actions/execute` | `{ "plan_id": string, "approved": true }` | `ActionResult` |

`POST /api/analyze` accepts only `case_id` as meaningful input. Extra fields are ignored. A missing or blank `case_id` is HTTP 400. An unknown case is HTTP 404. The example payloads in older docs illustrate field shape. They are not canned decision payloads.

`POST /api/investigate` response:

```ts
interface InvestigateResponse {
  case_id: string;
  answer: string;
  tools_used: Array<"get_case" | "get_evidence" | "inspect_evidence" | "reanalyze_case">;
  evidence_ids: string[];
}
```

`evidence_ids` must resolve to records for that case. An answer with no successful tool use is invalid.

`POST /api/actions/execute` runs the stored plan for `plan_id` only when `approved` is exactly `true`. The client cannot swap tools or arguments at execute time. Unknown `plan_id` is HTTP 404. Missing approval is HTTP 400 and changes nothing.

Unknown evidence id is HTTP 404.

---

## 14. Architecture

```text
Cases → Sources → Assembler → Decision Agent → Validator → Action Planner → Approval → Executor
```

One process. No microservices, Kafka, vector database, or multi-agent framework unless this Canon is updated first because P0 cannot ship without it. The default is that none of those are required.

Preferred backend boundaries: `adapters/`, `evidence/`, `context/`, `reasoning/`, `validation/`, `actions/`, `api/`, `schemas/`.

Preferred frontend boundaries: `components/`, `features/`, `api/`, `types/`, `hooks/`, `pages/`. Two pages.

Domain packs supply fixtures, the pattern, and action-tool definitions. Core reads `domain` and `pattern` from the case.

---

## 15. Validation and action safety

1. Do not trust model output, source payloads, or frontend input. Validate important inputs and outputs.
2. Model output must match the schema before it is shown or stored. On failure, retry safely or return `ABSTAIN` / a controlled error. Never silently coerce malformed output.
3. Every model-produced evidence reference must resolve to a real evidence record loaded for that case. Unknown ids invalidate the output.
4. Every `ChallengeResult.evidence_ids` entry equals an `evidence[].id` in the same `AnalyzeResponse`.
5. `EvidenceRecord.id` is `{source}:{source_record_id}`.
6. `observed_at` is UTC ISO 8601 or `null`.
7. `decision` is exactly `VERIFY`, `SUPPRESS`, or `ABSTAIN`. No confidence percentage and no risk score on any endpoint.
8. Disposition is computed from assembled evidence. It is not a map from `case_id` or claim text.
9. `VERIFY` only when evidence is sufficient and consistent enough to support intervention. `SUPPRESS` only when evidence supports not intervening. `ABSTAIN` when evidence is missing, conflicting, or insufficient, including when validation cannot recover a grounded decision.
10. Investigation answers cite tool results from the four allowed tools. Investigation cannot call action tools.
11. State-changing tools require PLAN → SHOW → APPROVE → EXECUTE → RESULT.
12. Execute applies the stored synthetic plan only. It does not call live enterprise systems.
13. A source that fails to load degrades that source. The demo process stays up and the decision can still be `ABSTAIN` or a partial grounded result. One source failure must not crash the demo.

---

## 16. Frontend principles

Palette, used as in `docs/DESIGN_LANGUAGE.md`:

| Role | Hex |
| --- | --- |
| Background | `#080808` |
| Primary surface | `#0B0B0C` |
| Secondary surface | `#151412` |
| Border / divider | `#2F2D28` |
| Primary text | `#F7F4EC` |
| Secondary text | `#A5A198` |
| Signal / accent | `#D5A942` |

Gold stays sparse. No purple AI gradients, glassmorphism, or neon.

The Case Brief makes this chain legible:

```text
Evidence → Challenge → Decision → Action
```

The disposition remains the visual hero: a viewer several meters from a projector can read the decision, the main evidence, and the recommended action. `VERIFY` is prominent. `SUPPRESS` is quiet. `ABSTAIN` is neutral and names the missing evidence. Do not rely on red/green traffic lights as the main language.

Show analysis progress: collecting evidence, building context, checking contradictions, forming the decision. Do not show raw chain-of-thought. Do not render a confidence score.

---

## 17. Build priorities

**P0 (must work before anything else).** Attention Today, Case Brief, dynamic analyze, all three dispositions, evidence with provenance, contradictions, recommended action, action plan, explicit approval, synthetic execute with before/after on the VERIFY path. `SUPPRESS` shows that no intervention runs. `ABSTAIN` shows what is missing.

**P1 (only after P0 is stable).** Investigate drawer with the four grounded tools. One manufacturing pack case in the same queue and the same Case Brief. The queue reflects the latest disposition and, after execute, that a synthetic action was applied.

**P1.5 (optional).** One logistics pack case, only if it fits in the remaining time without putting P0 at risk.

**P2 (cut for the hackathon).** Everything else: live connectors, real SAP/MES/TMS, extra pages, auth complexity, analytics, confidence scores, vector search, multi-agent frameworks, workflow builders, and a domain-specific UI.

Internal freeze: **4:30 PM IST.**

---

## 18. Demo story

Pitch line: **Mulanous Lite is an operational decision and action agent.**

Ten beats, about seven minutes. Names and records are synthetic.

1. **Attention.** Open Attention Today. The queue shows account, claim, urgency, source count, and disposition when already analyzed.
2. **Select the wedge.** Open Acme, Customer Commitment Intervention: SSO rollout blocked. Call `POST /api/analyze` with `{ "case_id": "acme-sso-rollout" }`.
3. **Context.** Case Brief shows flat evidence from CRM, Jira, Slack, and meetings, including provenance.
4. **Challenge.** Show contradictions checked. The "already resolved" hypothesis is tested against evidence. No confidence score.
5. **Decide.** `VERIFY`. Show reason, recommended action, owner, due hint, and the advisory boundary.
6. **When not to act.** Open Globex (`globex-export-timeout`). The same pipeline returns `SUPPRESS` because the export timeout is already resolved. Do not launch an intervention.
7. **When evidence is not enough.** Open Initech (`initech-europe-expansion`). The same pipeline returns `ABSTAIN` and names the missing evidence.
8. **Plan.** Return to Acme. The Take Action drawer shows a synthetic plan (`create_task`, `send_message`, and/or `update_account_risk`) and the before state. Nothing has run yet.
9. **Approve.** The manager explicitly approves. There is no autonomous write-back.
10. **Execute.** Synthetic tools run. Before and after are both visible. Close on the pitch line: when to act, when not to act, and when to ask for more evidence.

If P1 is up, one grounded Investigate question on Case Brief can sit between beats 5 and 6. It does not add a page. If P1 manufacturing is up, one production-commitment case in the same queue can replace a long explanation of cross-industry scope. Skip both rather than risk the P0 path.

These ten beats were not written down in the Day 1 spec. This section freezes them.

---

## 19. Merge-back into Mulanous

Lite stays a thin slice. Do not implement full Mulanous in the hackathon. Keep these module boundaries so a later merge is mechanical.

| Lite module | Mulanous concept |
| --- | --- |
| Source adapters and domain packs | Adapters and context pack |
| Challenge results / contradictions | Pattern intelligence and counter-interrogation |
| Flat evidence id, source, `observed_at` | Provenance |
| `VERIFY` / `SUPPRESS` / `ABSTAIN` validator | Tri-state gate |
| Investigate drawer and its four tools | Investigation |
| Plan → show → approve → execute | Human-approved action |
| Attention Today | Attention delivery |

Core assemble / reason / validate / investigate / actions stays industry-agnostic. Packs carry fixtures, pattern ids, and tool variants.

---

## 20. Change control

Product and architecture stay frozen until P0 works.

A new idea that does not materially improve the 7-minute demo goes to **POST-HACKATHON / FUTURE** and is not built in this hackathon.

A real scope or architecture change updates this Canon first. Then sync the README, product spec, API contract, architecture note, demo flow, frontend handoff, and agent instructions.

Unchanged without a Canon edit:

- primary user
- primary question
- the two-screen surface
- the three dispositions
- the decision pipeline and the approval gate
- synthetic-only execution
- the rule that dispositions are computed, not hardcoded

---

## 21. Success

Success is a working dynamic prototype: grounded evidence, all three decision states, investigation, human-approved synthetic execution, a 7-minute demo, and enough credibility to support incubation.

P0 is the qualification gate. The Investigate drawer, the manufacturing case, and queue refresh are P1 once P0 is stable. A hardcoded demo result does not count.

---

## Authority over other documents

These files remain useful and are subordinate to this Canon until they are synced:

- `README.md`
- `docs/PRODUCT_SPEC.md`
- `docs/api-contract.md`
- `docs/architecture.md`
- `docs/demo-flow.md`
- `docs/DESIGN_LANGUAGE.md`
- `frontend/README.md`
- `backend/README.md`
- `agent.md`
- `AGENTS.md`

Visual details that this Canon does not restate (type scale, spacing, motion, projector checks) still come from `docs/DESIGN_LANGUAGE.md`, except where that file conflicts with this Canon.
