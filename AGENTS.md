# Agent Instructions

Before writing or reviewing code, read [`agent.md`](agent.md) and [`docs/DESIGN_LANGUAGE.md`](docs/DESIGN_LANGUAGE.md). The mission, ownership, architecture, and visual rules in those files apply to every change.

Human teammates and other agents will review code and UI strictly on every change. Treat rejection risk as high (over 80% as stated by the project owner) and make work easy to inspect. Design for scrutiny across 10,000+ potential test cases; this is a quality expectation, not a claim that such tests have been run. Do not claim a gate passed without running and checking it. These standards and the Definition of Done are hard gates.

# Code Quality Standards

## General Rule

Challenge speed does not justify unreadable or fragile code.

Optimize for:
- correctness
- readability
- debuggability
- demo reliability
- small surface area

Do not optimize for:
- cleverness
- abstraction depth
- architectural novelty

---

## Code Structure

Keep modules focused.

Each file should ideally have one clear responsibility.

Preferred boundaries:

backend/
- adapters/
- evidence/
- context/
- reasoning/
- validation/
- api/
- schemas/

frontend/
- components/
- features/
- api/
- types/
- hooks/
- pages/

Avoid giant files that mix:
- fetching
- business logic
- model calls
- validation
- UI rendering

---

## Naming

Names must explain intent.

Good:
- assembleContext()
- validateEvidenceReferences()
- analyzeCommitmentRisk()
- DecisionBrief
- EvidenceCard

Bad:
- processData()
- helper()
- handleThing()
- temp()
- finalFinal()

No unexplained abbreviations.

---

## Functions

Prefer small functions with one responsibility.

Target:
- < 40 lines when practical
- explicit inputs
- explicit outputs
- minimal hidden state

Avoid deeply nested conditionals.

Prefer early returns.

---

## Types and Schemas

All important boundaries must be typed.

Define schemas for:
- source evidence
- normalized evidence
- context
- model output
- decision output
- API request
- API response

Never rely on loosely shaped objects for critical logic.

---

## Validation

Never trust:
- LLM output
- external source payloads
- frontend input

Validate all important inputs and outputs.

LLM responses must pass schema validation before being used.

If validation fails:
- retry safely, or
- return ABSTAIN / controlled error

Never silently coerce malformed AI output.

---

## LLM Calls

LLM prompts must be:
- versioned
- explicit
- structured
- grounded in supplied evidence
- constrained to schema output

Do not:
- ask for unrestricted prose and parse it later
- send unnecessary data
- expose secrets
- trust fabricated IDs
- let the model invent source facts

Every model-produced evidence reference must resolve to real evidence.

---

## Error Handling

Every external operation must fail gracefully.

Handle:
- model timeout
- malformed output
- missing evidence
- source unavailable
- network failure
- API error

Never crash the demo because one source fails.

Return useful states such as:
- source unavailable
- incomplete evidence
- analysis failed safely
- ABSTAIN

---

## Logging

Log:
- request ID
- analysis start/end
- source load state
- context size
- model call success/failure
- validation result
- final decision state

Do not log:
- secrets
- API keys
- confidential data
- full raw prompts unnecessarily

---

## Secrets

Use environment variables.

Never commit:
- API keys
- tokens
- passwords
- OAuth secrets

Provide `.env.example`.

---

## Tests

Minimum test coverage must include:

1. VERIFY scenario
2. SUPPRESS scenario
3. ABSTAIN scenario
4. invalid model response
5. missing evidence reference
6. source failure
7. API response schema

Prioritize high-value tests over broad coverage.

---

## Git Discipline

Commits should be small and descriptive.

Examples:

feat: add normalized evidence schema
feat: implement decision validation
feat: add decision brief UI
fix: reject unresolved evidence references
test: add abstain decision scenario

Avoid:
- "update"
- "changes"
- "final"
- "working"

---

## Dependency Discipline

Before adding a dependency ask:

"Can this be done clearly with what we already have?"

Avoid large libraries for trivial functionality.

Lock dependency versions where practical.

---

## Performance

For the challenge:

Target:
- initial UI load < 2s where possible
- analysis response ideally < 10–15s
- no unnecessary repeated model calls
- no blocking UI

Show progress while analysis runs.

---

## Reliability Gate

Before calling a feature complete:

- builds successfully
- typecheck passes
- lint passes
- critical tests pass
- no console errors
- no uncaught promise rejections
- no hardcoded demo result
- clean restart works

# Definition of Done

A feature is DONE only when:

1. Functionally works
2. Types pass
3. Lint passes
4. Critical path tested
5. Error state handled
6. UI matches design language
7. No console errors
8. Demo path works from clean start
9. Another teammate can understand the code
10. It materially improves the final 7-minute demonstration
