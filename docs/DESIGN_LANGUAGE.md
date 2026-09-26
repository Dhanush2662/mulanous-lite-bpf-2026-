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

---

# UI Quality Standards

## Quality Bar

The UI must look like a real enterprise product,
not a hackathon mockup.

A screen is not complete because it "works."

It must also be:
- visually coherent
- readable
- responsive
- stable
- understandable without explanation
- presentation-ready

---

## Visual Hierarchy

Every screen must make the user's next question obvious.

Priority order:

1. Decision
2. Why it matters
3. Evidence
4. Recommended action
5. Metadata

Never give all elements equal visual weight.

---

## Spacing

Use a consistent spacing system.

Recommended scale:

4
8
12
16
24
32
48
64

Do not use random spacing values.

Keep:
- section spacing generous
- internal card spacing tighter
- metadata compact

---

## Layout

Use a consistent content grid.

Preferred:
- max-width content area
- strong left alignment
- clear vertical rhythm

Avoid:
- elements floating without alignment
- inconsistent card widths
- arbitrary margins
- dense edge-to-edge content

---

## Cards

Cards must have a purpose.

Use cards for:
- decisions
- evidence
- actions
- source status

Do not put every text block inside a card.

Avoid excessive nesting:

card
  inside card
    inside card

---

## Borders

Use thin, subtle borders.

Default:
#2F2D28

Avoid heavy outlines.

Borders should structure information,
not decorate it.

---

## Typography Quality

Do not use more than:
- 2 font families
- 4 primary text sizes
- 3 font weights

Recommended hierarchy:

Display / Decision:
28–36px

Section title:
16–20px

Body:
14–16px

Metadata:
11–13px

Avoid tiny body text during projector presentation.

---

## Contrast

All important text must remain readable on a projector.

Do not rely on extremely subtle grey-on-black contrast.

Secondary text must still be legible from several meters away.

---

## Decision State Quality

Decision states must be instantly distinguishable.

VERIFY:
high prominence

SUPPRESS:
lower prominence

ABSTAIN:
neutral/incomplete

Do not rely on color alone.

Always include:
- label
- icon or structural distinction
- explanatory text

---

## Loading State

Never show a blank screen while AI runs.

Show meaningful progress:

Collecting evidence
→ Building context
→ Checking contradictions
→ Forming decision

Do not fake detailed internal reasoning.

---

## Empty State

Empty states must explain:
- what is missing
- why nothing is shown
- what the user can do next

Bad:
"No data"

Good:
"No decision could be formed because Jira evidence is unavailable."

---

## Error State

Errors must:
- explain what failed
- avoid technical stack traces
- preserve the rest of the UI
- offer retry where possible

Example:

"Slack evidence could not be loaded.
Analysis continued using CRM and Jira."

---

## Evidence Quality

Evidence must be visually inspectable.

Each evidence item should include:

- source
- source record id
- title
- body
- observed at

Do not hide provenance behind tooltips only.

---

## Interaction Quality

Buttons must have:
- clear labels
- visible hover
- visible focus
- disabled state where needed

Avoid vague labels:

Bad:
"Go"
"Submit"
"Continue"

Good:
"Analyze commitments"
"View evidence"
"Run again"

---

## Animation

Animation must communicate state.

Allowed:
- loading progression
- evidence reveal
- decision arrival
- subtle hover transitions

Avoid:
- decorative floating elements
- excessive fades
- spinning everything
- long transitions

Maximum typical UI transition:
150–250ms

---

## Responsive Behavior

Primary target:
1366×768 and larger laptop screens.

Test at:
- 1366×768
- 1440×900
- 1920×1080

The core decision must remain visible without excessive scrolling.

---

## Projector Test

Before final submission:

Open the UI full-screen.

Stand several meters away.

Check whether you can immediately read:

- decision
- status
- main evidence
- recommended action

If not, increase contrast, size, or spacing.

---

## Demo Safety

Do not put essential demo behavior behind:
- hidden menus
- hover-only interactions
- tiny icons
- complicated navigation

The golden path should be obvious.

---

## UI Completion Gate

A screen is complete only if:

- alignment is consistent
- spacing is consistent
- typography hierarchy is clear
- no overflow
- no clipped text
- no layout shift
- loading state exists
- error state exists
- empty state exists where relevant
- keyboard focus is visible
- no console warnings
- no placeholder lorem ipsum
- no fake production data claims
- no broken buttons
- no unnecessary animations
- tested at presentation resolution
