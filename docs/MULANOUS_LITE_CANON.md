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

**Problem.** Operational evidence is fragmented. Some of it is exact structured state (ticket status, order quantity, commitment date, inventory quantity, owner). Some of it is unstructured context (Slack, meeting notes, descriptions, escalations, operational comments). Managers reconstruct both by hand before they can decide whether a commitment needs intervention, is already resolved, is insufficiently evidenced, or needs a specific next action.

**Out of scope.** Enterprise search, RAG-only question answering, document summarization, a generic chatbot, and an analytics dashboard. Also out of scope: a connectors admin, a connector settings or OAuth product, a workflow builder, a settings or auth product, and a separate UI per industry. Source adapters and evidence provenance are in scope. An optional one-line sources strip is in scope. Connector management is not.

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

P0 runs attention, context, challenge, decision, action plan, and synthetic execute for two domains on one engine. Challenge in P0 is the contradiction check inside the decision pipeline. The user-driven Investigate drawer is the P1 expression of the INVESTIGATE stage. It is not a third page, and P0 does not wait on it.

Low-risk internal actions may complete under an explicit policy without a second approval click. State-changing and external actions still stop at human approval. The loop above is the state-changing path.

---

## 3. Primary use case and cross-industry proof

**Two P0 demo domains. Same engine, same UI.** A case declares `domain` and `pattern`. Those two fields select the pack. The core does not branch on `case_id` and does not grow an industry-specific screen.

| Priority | Pack | Pattern | Synthetic sources | Gate |
| --- | --- | --- | --- | --- |
| P0-A | `software` | `customer_commitment_intervention` | CRM, Jira, Slack, meetings | Full Decision + Action demo |
| P0-B | `manufacturing` | `production_commitment_intervention` | ERP/order, production schedule, inventory/material, quality/ops notes | Same core, same Attention Today and Case Brief. Compressed cross-industry proof. |
| P1.5 | `logistics` | `delivery_commitment_risk` | TMS, carrier, ETA, SLA | Optional, and only if it fits in the remaining time (about 20 minutes) without risking P0-A or P0-B |

Pack layout:

```text
domain_packs/software/         fixtures + pattern + action tools
domain_packs/manufacturing/
domain_packs/logistics/
```

Core stays assemble, reason, validate, investigate, and actions. Packs supply fixtures, the pattern, and action-tool definitions.

Do not build real SAP, MES, or TMS connectors. Do not build a domain-specific frontend. Do not build a connectors admin.

Checked-in software fixtures may stay in `data/` until a move into `domain_packs/software/` is cheap. That move must not block P0. Manufacturing fixtures belong under `domain_packs/manufacturing/`. Logistics fixtures, if any, belong under their pack directory.

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

No third page. Cut settings, admin, connectors, analytics, a chatbot page, a workflow builder, and auth complexity. No sidebar. No connectors management UI and no OAuth connector product.

An optional one-line sources strip may name the sources already on the case. It is provenance, not a connector admin.

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

Mulanous Lite recommends a decision and a plan. A human must approve before any state-changing or external tool runs. Low-risk internal tools may run under policy. Execution touches synthetic tools only. The product does not write to live CRM, Jira, Slack, SAP, MES, TMS, or any other production system, and it does not contact a real customer.

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

- load the case by id, then retrieve evidence for that case's `domain` and account
- use hybrid retrieval: deterministic structured lookup for exact facts, and vector search only for semantic text
- refuse to decide ticket state, order quantity, commitment date, inventory quantity, ids, owner, or status by vector similarity
- assemble context only from records that retrieval returned for that case
- schema-validate model output
- resolve every evidence reference to a real record for that case
- reject unresolved references
- retry a safe validation failure, or return `ABSTAIN` / a controlled error
- refuse to coerce malformed model output into a decision
- keep state-changing action execution behind the approval gate

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

State-changing and external tools use:

```text
PLAN → SHOW → APPROVE → EXECUTE → RESULT
```

The plan is shown in the Take Action drawer before anything runs. Approval is an explicit human action. Execute applies only that stored plan, and only to synthetic tools. The drawer shows before state and after state in the demo.

Low-risk internal tools may auto-apply when policy allows. They are still planned and still visible. They do not contact a customer and do not write to an external system.

| Class | Tools | Gate |
| --- | --- | --- |
| Low-risk internal | `dismiss_resolved`, `acknowledge`, `request_evidence` | Policy may auto-apply. |
| State-changing, software | `create_task`, `send_message`, `update_account_risk` | Human approval required. |
| State-changing, manufacturing | `expedite_material`, `notify_planner`, `update_order_risk` | Human approval required. |

P0 software tools:

| Tool | Synthetic effect |
| --- | --- |
| `create_task` | Create a local task (`title`, `owner`, `detail`, `case_id`). |
| `send_message` | Record a local message (`recipient`, `body`, `case_id`). The recipient is a synthetic role, such as "Delivery owner". |
| `update_account_risk` | Record a local account risk note (`account`, `risk_note`, `case_id`). |

P0 manufacturing tools, same gate, synthetic state only:

| Tool | Synthetic effect |
| --- | --- |
| `expedite_material` | Record a local material expedite (`material`, `detail`, `case_id`). |
| `notify_planner` | Record a local notice to the production planner (`recipient`, `body`, `case_id`). |
| `update_order_risk` | Record a local order risk note (`order_id`, `risk_note`, `case_id`). |

Low-risk internal tools:

| Tool | Synthetic effect |
| --- | --- |
| `dismiss_resolved` | Mark the case dismissed on the attention queue. |
| `acknowledge` | Record that the case was seen (`case_id`, `note`). |
| `request_evidence` | Record an internal ask for missing evidence (`case_id`, `detail`). |

Logistics packs may register further tool names later. Those names stay inside the pack. State-changing names still use plan → show → approve → execute. They still hit synthetic state only.

`ActionPlan.requires_approval` is `true` when any step is state-changing or external. It is `false` when every step is low-risk internal. A `false` plan may be applied at plan time under policy. A `true` plan changes nothing until execute with `approved: true`.

Disposition behavior:

- `VERIFY` may plan state-changing tools. Those steps wait for approval.
- `SUPPRESS` plans no state-changing intervention. Policy may dismiss the resolved case from the queue. The honest external result is unchanged enterprise state.
- `ABSTAIN` may request the missing evidence. It must not act as if the commitment were verified, and it must not expedite, message, or update risk as though the commitment were confirmed.

---

## 10. Synthetic environment

MongoDB Atlas is the P0 evidence and context store. It holds normalized enterprise evidence, metadata and provenance, semantic embeddings, and an Atlas Vector Search index. Checked-in fixtures are the seed. The pitch must not describe them as live production connectors, and the product must not grow a connectors admin.

Retrieval is hybrid. See section 14 for the rule and the rationale.

Software evidence sources are `crm`, `jira`, `slack`, and `meetings`. Manufacturing evidence sources are `erp`, `schedule`, `inventory`, and `quality`. Later packs add their own source strings without forking the evidence shape and without a new screen.

Structured sources carry exact facts and are retrieved by metadata filters. Semantic sources (`slack`, `meetings`, descriptions, escalations, quality and operational comments) are retrieved by vector search inside those filters. If Atlas is unreachable, the same hybrid path runs on in-memory fixtures. The process stays up.

---

## 11. Demo cases

Four cases share one pipeline. Three are software. One is manufacturing. Each case declares `domain` and `pattern`.

| Case | `case_id` | Domain | Pattern | Claim | Fixture expectation |
| --- | --- | --- | --- | --- | --- |
| Acme | `acme-sso-rollout` | `software` | `customer_commitment_intervention` | SSO rollout blocked | `VERIFY` |
| Globex | `globex-export-timeout` | `software` | `customer_commitment_intervention` | Export timeout escalation | `SUPPRESS` (already resolved) |
| Initech | `initech-europe-expansion` | `software` | `customer_commitment_intervention` | Europe expansion at risk | `ABSTAIN` (insufficient evidence) |
| Orion Components | `orion-order-5000` | `manufacturing` | `production_commitment_intervention` | 5,000 units due Monday | `VERIFY` |

Orion evidence is a committed order for 5,000 units due Monday, a material shortage, a throughput drop, and a quality hold. That shape is what supports intervention. The case id is not.

`acme-sso-rollout` was already the analyze contract's canonical id. The other ids are assigned here so fixtures and tests stay stable.

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
  queue_status: "open" | "dismissed";
}

interface EvidenceRecord {
  id: string; // "{source}:{source_record_id}"
  source: string; // software: "crm" | "jira" | "slack" | "meetings"; manufacturing: "erp" | "schedule" | "inventory" | "quality"
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

Embeddings and `retrieval_class` (`structured` or `semantic`) live in the Atlas evidence store. They are not API fields. Similarity is not a confidence score and is not shown.

`domain` and `pattern` are required on every case. They select the pack and the action tools. They are engine fields, not extra screens. Attention Today reads `account`, `claim`, `urgency`, `source_count`, `disposition`, and `queue_status`.

`Case.disposition` is `null` until a validated analysis exists. `queue_status` is `open` until a low-risk `dismiss_resolved` runs.

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
  material_expedites: Array<{ id: string; material: string; detail: string; case_id: string }>;
  planner_notices: Array<{ id: string; recipient: string; body: string; case_id: string }>;
  order_risks: Array<{ id: string; order_id: string; risk_note: string; case_id: string }>;
  acknowledgements: Array<{ id: string; case_id: string; note: string }>;
  evidence_requests: Array<{ id: string; case_id: string; detail: string }>;
  dismissed_case_ids: string[];
}

interface ActionPlan {
  plan_id: string;
  case_id: string;
  steps: ActionStep[];
  requires_approval: boolean;
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
Cases → Atlas evidence store → Hybrid retrieval → Assembler → Decision Agent → Validator → Action Planner → Policy or Approval → Executor
```

One process. No microservices, Kafka, or multi-agent framework.

MongoDB Atlas is the evidence and context store: normalized evidence, metadata and provenance, semantic embeddings, and Atlas Vector Search. That store is required for the P0 architecture, not as a sponsor decoration.

**Why hybrid retrieval.** Enterprise evidence has two shapes. Exact structured state answers "what is the ticket status, the order quantity, the commitment date, the inventory quantity, the id, the owner?" Semantic unstructured context answers "what did people say, what was escalated, what did the meeting or the quality note imply?" A pure structured query misses the note. Pure RAG can misread a quantity or a status because a nearby sentence looks similar. Hybrid retrieval uses each path for the shape it is good at.

| Path | Used for | Must not be used for |
| --- | --- | --- |
| Deterministic structured retrieval | Ticket state, order quantity, commitment date, inventory quantity, ids, owner, status. Metadata filters on account, domain, time, and source. | Ranking Slack or meeting prose by token overlap alone when a vector index is available. |
| Vector / semantic retrieval | Slack, meeting notes, descriptions, escalations, operational and quality comments. | Deciding an exact fact listed above. |

Filters (account, domain, and optionally time and source) bound both paths. Vector search runs inside those filters, on semantic records only.

If Atlas is unreachable, or the vector index is missing, the process falls back to the same hybrid code path over in-memory fixtures and local vectors. One store failure must not crash the demo.

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
11. State-changing and external tools require PLAN → SHOW → APPROVE → EXECUTE → RESULT. Low-risk internal tools may auto-apply under policy. Neither class calls a live enterprise system.
12. Execute applies the stored synthetic plan only. It does not call live enterprise systems. The client cannot swap tools at execute time.
13. A source or Atlas outage degrades that store. The demo process stays up, hybrid retrieval falls back to fixtures, and the decision can still be `ABSTAIN` or a partial grounded result. One store failure must not crash the demo.
14. Vector similarity must not establish ticket state, order quantity, commitment date, inventory quantity, ids, owner, or status. Those values come from structured retrieval.

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

**P0 (must work before anything else).** Attention Today and Case Brief for software and manufacturing. Dynamic analyze, all three dispositions, hybrid retrieval from the Atlas evidence store, evidence with provenance, contradictions, recommended action, action plan, human approval for state-changing tools, synthetic execute with before/after on the VERIFY path. `SUPPRESS` shows that no state-changing intervention runs. `ABSTAIN` shows what is missing. P0-A is the full software loop. P0-B is the Orion manufacturing case on those same two screens.

**P1 (only after P0 is stable).** Investigate drawer with the four grounded tools. The queue reflects the latest disposition and, after execute, that a synthetic action was applied.

**P1.5 (optional).** One logistics pack case, only if it fits in the remaining time without putting P0 at risk.

**P2 (cut for the hackathon).** Everything else: live connectors, a connectors admin, OAuth connector product, real SAP/MES/TMS, extra pages, auth complexity, analytics, confidence scores, multi-agent frameworks, workflow builders, and a domain-specific UI. Atlas Vector Search remains the semantic half of P0 retrieval.

Internal freeze: **4:30 PM IST.**

---

## 18. Demo story

Pitch line: **Mulanous Lite is an operational decision and action agent.**

About seven minutes. Software is the full loop. Manufacturing is a compressed cross-industry proof on the same screens. Names and records are synthetic.

1. **Attention.** Open Attention Today. The queue includes software and manufacturing cases. Each row shows account, claim, urgency, source count, and disposition when already analyzed.
2. **Select the wedge.** Open Acme, Customer Commitment Intervention: SSO rollout blocked. Call `POST /api/analyze` with `{ "case_id": "acme-sso-rollout" }`.
3. **Context.** Case Brief shows flat evidence from CRM, Jira, Slack, and meetings, including provenance.
4. **Challenge.** Show contradictions checked. The "already resolved" hypothesis is tested against evidence. No confidence score.
5. **Decide.** `VERIFY`. Show reason, recommended action, owner, due hint, and the advisory boundary.
6. **When not to act.** Open Globex (`globex-export-timeout`). The same pipeline returns `SUPPRESS` because the export timeout is already resolved. Do not launch an intervention.
7. **When evidence is not enough.** Open Initech (`initech-europe-expansion`). The same pipeline returns `ABSTAIN` and names the missing evidence.
8. **Plan.** Return to Acme. The Take Action drawer shows a synthetic plan (`create_task`, `send_message`, and/or `update_account_risk`) and the before state. Nothing has run yet.
9. **Approve.** The manager explicitly approves. There is no autonomous write-back.
10. **Execute.** Synthetic tools run. Before and after are both visible.
11. **Cross-industry.** Open Orion Components (`orion-order-5000`) on the same Attention Today and the same Case Brief. `domain` is `manufacturing` and `pattern` is `production_commitment_intervention`. Call the same `POST /api/analyze`. Evidence from ERP, the production schedule, inventory, and quality notes supports `VERIFY`: a committed order of 5,000 units due Monday, a material shortage, a throughput drop, and a quality hold. The Take Action drawer shows manufacturing tools (`expedite_material`, `notify_planner`, `update_order_risk`). State-changing steps still wait for approval. There is no manufacturing-specific page.

Close on the pitch line: when to act, when not to act, when to ask for more evidence, and the same engine on a second domain.

If P1 is up, one grounded Investigate question on Case Brief can sit between beats 5 and 6. It does not add a page. Do not skip the Orion beat. Do not add a third page to make room for it.

These beats freeze the seven-minute demo. Software stays the full loop. Manufacturing stays compressed.

---

## 19. Merge-back into Mulanous

Lite stays a thin slice. Do not implement full Mulanous in the hackathon. Keep these module boundaries so a later merge is mechanical.

| Lite module | Mulanous concept |
| --- | --- |
| Source adapters and domain packs | Adapters and context pack |
| Atlas evidence store and hybrid retrieval | Structured state plus semantic context |
| Challenge results / contradictions | Pattern intelligence and counter-interrogation |
| Flat evidence id, source, `observed_at` | Provenance |
| `VERIFY` / `SUPPRESS` / `ABSTAIN` validator | Tri-state gate |
| Investigate drawer and its four tools | Investigation |
| Plan → show → approve → execute | Human-approved action |
| Attention Today | Attention delivery |

Core assemble / reason / validate / investigate / actions stays industry-agnostic. Packs carry fixtures, pattern ids, and tool variants.

---

## 20. Change control

Product and architecture stay frozen until P0 works. This revision freezes the Atlas evidence store, hybrid retrieval, P0-A software, P0-B manufacturing, and the split between low-risk internal actions and state-changing approval.

A new idea that does not materially improve the 7-minute demo goes to **POST-HACKATHON / FUTURE** and is not built in this hackathon.

A real scope or architecture change updates this Canon first. Then sync the README, product spec, API contract, architecture note, demo flow, frontend handoff, and agent instructions.

Unchanged without a Canon edit:

- primary user
- primary question
- the two-screen surface
- the three dispositions
- the decision pipeline and the state-changing approval gate
- synthetic-only execution
- the rule that dispositions are computed, not hardcoded

---

## 21. Success

Success is a working dynamic prototype: grounded evidence, all three decision states, investigation, human-approved synthetic execution, a 7-minute demo, and enough credibility to support incubation.

P0 is the qualification gate: software and manufacturing on one API and the same two screens, hybrid retrieval, all three decision states, and human-approved state-changing execution. The Investigate drawer and queue refresh stay P1 once that path is stable. A hardcoded demo result does not count.

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
