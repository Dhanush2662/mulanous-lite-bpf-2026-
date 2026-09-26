# Mulanous Lite — BPF 2026

## Mission

Build an employee-facing enterprise decision copilot for the Builders' Pitch Fest Enterprise AI challenge.

Primary user:
Delivery / Operations Manager.

Primary question:
"What needs my attention today, and why?"

The system should connect fragmented enterprise evidence, reconstruct relevant operational context, challenge suspected problems, and return an actionable decision brief.

This is NOT:
- a generic enterprise chatbot
- a dashboard full of charts
- a document summarizer
- a Jira analytics tool
- a multi-agent science project

---

## Core Demo

The primary demo scenario is Customer Commitment Risk.

Inputs may include:
- CRM/customer commitments
- Jira/project delivery data
- Slack/communication evidence
- meeting/document evidence

Expected outcome:

CONNECT
→ understand fragmented evidence

CHALLENGE
→ look for contradictions / alternative explanations

DECIDE
→ VERIFY / SUPPRESS / ABSTAIN

ACT
→ present evidence, owner and recommended next action

---

## Decision States

Every analysis MUST terminate in one of:

### VERIFY
Evidence is sufficient and consistent enough to recommend intervention.

### SUPPRESS
The suspected issue was checked and available evidence indicates intervention is not required.

### ABSTAIN
Evidence is missing, contradictory or insufficient.

Never force a finding when evidence is weak.

---

## Architecture

Source adapters
→ normalized evidence
→ context assembler
→ AI reasoning
→ deterministic validation
→ decision object
→ decision brief UI

Keep these concerns separated.

Do not collapse ingestion, reasoning and UI into one LLM call.

---

## AI Responsibilities

AI MAY:
- extract facts
- identify relationships
- interpret unstructured text
- connect evidence across sources
- identify contradictions
- propose explanations
- recommend actions
- produce structured reasoning outputs

AI MUST NOT:
- fabricate source evidence
- invent source IDs
- pretend missing data exists
- bypass validation
- output arbitrary unstructured responses to the frontend

All important model output must conform to a defined schema.

---

## Evidence Rules

Every surfaced claim must reference actual input evidence.

Evidence objects must preserve:
- source
- source record ID
- timestamp where available
- relevant text/value
- provenance

If cited evidence cannot be resolved to an actual input record, reject that evidence.

---

## Challenge Constraints

The prototype must be genuinely dynamic.

Do not hardcode:
- final findings
- canned AI answers
- fake confidence
- responses intended to make the demo appear smarter

Synthetic enterprise data is allowed and expected for the challenge.

Pre-existing connector/adaptor code must remain isolated from challenge-specific reasoning logic.

---

## API Contract

Primary API:

POST /api/analyze

Frontend must consume structured API responses.

Do not make frontend components depend directly on LLM-specific response structures.

Expected conceptual output:

{
  "decision": "VERIFY | SUPPRESS | ABSTAIN",
  "title": "...",
  "summary": "...",
  "priority": "...",
  "evidence": [],
  "contradictions": [],
  "owner": "...",
  "recommended_action": "...",
  "confidence": 0.0
}

The final schema may evolve, but changes must be coordinated between frontend and backend.

---

## Team Ownership

### Sandeep
Owns:
- backend
- AI pipeline
- context assembly
- evidence model
- decision validation
- API
- synthetic enterprise dataset
- integration

### Syam
Owns:
- frontend
- interaction design
- Decision Brief
- evidence presentation
- source-state UI
- responsive layout
- demo polish

Avoid modifying the other owner's area without coordinating first.

---

## Product Rule

Every proposed feature must answer:

"Does this materially improve the 7-minute demo?"

If no:
put it under POST-HACKATHON and do not build it today.

---

## Engineering Rules

Prefer:
- simple modules
- explicit interfaces
- typed schemas
- deterministic validation
- readable code
- small commits
- graceful failure states

Avoid:
- unnecessary abstractions
- microservices
- Kafka/event infrastructure
- vector databases unless demonstrably required
- complex authentication
- elaborate role systems
- premature optimization
- large dependency additions

---

## Demo Reliability

Demo reliability has priority over feature count.

Before adding features:
1. happy path must work
2. VERIFY must work
3. SUPPRESS must work
4. ABSTAIN must work
5. evidence provenance must render
6. clean restart must work

---

## Change Discipline

Do not change:
- primary user
- primary problem
- demo scenario
- decision-state model
- core architecture

without explicit agreement from Sandeep.

Do not redesign the UI style independently of `docs/DESIGN_LANGUAGE.md`.
