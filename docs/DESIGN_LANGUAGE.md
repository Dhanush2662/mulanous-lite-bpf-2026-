# Mulanous Lite — Design Language

## Product Feeling

Mulanous Lite should feel like:

- serious enterprise software
- evidence-driven
- calm under pressure
- precise
- operational
- trustworthy

It must NOT look like:
- a generic AI chatbot
- a colorful SaaS dashboard
- a crypto product
- a neon AI demo
- glassmorphism
- a consumer productivity app

---

## Visual Principle

Information hierarchy > decoration.

The interface should visually distinguish:

1. Decision
2. Evidence
3. Explanation
4. Action
5. Metadata

The decision is always the hero.

---

## Color System

Background:
#080808

Primary surface:
#0B0B0C

Secondary surface:
#151412

Border / divider:
#2F2D28

Primary text:
#F7F4EC

Secondary text:
#A5A198

Signal / accent:
#D5A942

Gold is sparse.

Use gold for:
- verified signal
- active evidence connection
- important metadata
- selected state

Do not cover large surfaces in gold.

---

## Typography

Primary:
Inter or equivalent clean grotesk sans-serif.

Metadata / source labels:
IBM Plex Mono or equivalent monospace.

Hierarchy:

H1:
large, compact, high confidence

H2:
section-level

Body:
high readability

Mono:
source systems
timestamps
IDs
decision state
technical metadata

Avoid overly large marketing typography inside application screens.

---

## Geometry

Prefer:
- sharp or minimally rounded rectangles
- thin borders
- generous spacing
- strong alignment
- disciplined grids

Avoid:
- huge border radius
- floating pill overload
- soft gradient cards
- heavy shadows

---

## Main Screen

Primary question:

"What needs my attention today?"

Below it:

Decision Feed / Decision Brief.

Do not build a generic chat interface as the primary product.

---

## Decision Brief Structure

Top area:

[ VERIFIED ]

Customer commitment requires intervention

Associated commitment:
₹22L

Then:

WHY THIS MATTERS

Short explanation.

EVIDENCE

CRM
Customer rollout committed for Friday

JIRA
Critical blocker unresolved for 9 days

SLACK
Customer escalation yesterday

CONTRADICTIONS CHECKED

Show what the system checked before verifying.

OWNER

Delivery Manager

RECOMMENDED ACTION

Review recovery plan with account and delivery owners today.

---

## Decision State Treatment

VERIFY
Strong visual prominence.
Gold may be used.

SUPPRESS
Visually quiet.
Do not treat as an alert.

ABSTAIN
Neutral / incomplete state.
Explain exactly what evidence is missing.

Do not use aggressive red/green traffic-light styling as the main visual language.

---

## Evidence UI

Evidence should look inspectable.

Each item should show:

SOURCE
record / entity
relevant evidence
timestamp

Example:

JIRA
DEL-442
Critical blocker unresolved
9 days

Source evidence should be expandable where useful.

---

## Interaction Principles

User should be able to:

- inspect why a decision was made
- inspect source evidence
- understand contradictions
- understand what action is recommended

Every important output should answer:

"What made the system say this?"

---

## Demo Principle

The interface should make the AI reasoning visible without showing raw chain-of-thought.

Show:

Evidence found
→ Context connected
→ Contradictions checked
→ Decision

Do NOT expose internal hidden reasoning text.

---

## Motion

Minimal.

Allowed:
- analysis progress
- evidence entering
- decision transition
- source connection lines

Avoid decorative animation.

---

## Responsive Priority

Primary target:
laptop presentation screen.

Secondary:
tablet.

Mobile optimization is not important for today's challenge.

---

## Final Quality Test

Before accepting a screen ask:

"Could this screenshot plausibly belong to serious enterprise decision software?"

If no, simplify it.
