# Change Log And Rationale

This document summarizes the changes made during the TruPulse AI review and cleanup, and explains why each change was made.

## 1. Dashboard Project Label

File changed:

```text
frontend/src/pages/Dashboard.jsx
```

Change:

```text
Changed "active projects" to "projects"
```

Why:

The dashboard showed:

```text
115 employees · 14 teams · 34 active projects
```

But the backend value comes from the total project count in `projects.csv`, not a filtered active-project count.

So the label was misleading.

Result:

```text
115 employees · 14 teams · 34 projects
```

This is more accurate and easier to defend during explanation.

## 2. Workforce Readiness Risk Label

File changed:

```text
frontend/src/pages/Dashboard.jsx
```

Change:

Added frontend mapping:

```text
High readiness -> LOW risk
Medium readiness -> MEDIUM risk
Low readiness -> HIGH risk
```

Why:

The dashboard showed:

```text
Workforce Readiness
93.3
High
High Risk
```

That was contradictory. A high readiness score should not be shown as high risk.

Result:

A high workforce readiness score now maps to:

```text
LOW Risk
```

## 3. Org Pulse Ticker Made Dynamic

File changed:

```text
frontend/src/components/OrgPulseTicker.jsx
```

Change:

The carousel/ticker was changed from hardcoded event text to live API-driven text.

It now calls:

```text
GET /org-health
GET /spof-ranking
GET /employee/Vikram
GET /succession-planning
GET /
```

Why:

The ticker previously had hardcoded values like:

```text
Composite health score: 27.5/100
56 single points of failure
$5.6M revenue at risk
Vikram no backup
211 of 468 knowledge areas
```

The user asked where those values came from and requested that all of them become dynamic.

Result:

The ticker now calculates live text from backend data:

```text
Composite health score
SPOF count
Top-3 SPOF revenue risk
Vikram profile and revenue risk
Burnout count
Low documentation count
AI pipeline status
Succession coverage
```

It refreshes every 30 seconds.

## 4. Chatbot SPOF Definition Fix

File changed:

```text
backend/main.py
```

Change:

Added explicit handling for questions like:

```text
what is spof
meaning of spof
define spof
full form of spof
what does spof mean
single point of failure meaning
```

Why:

The chatbot was answering analytical SPOF ranking questions instead of explaining the meaning of SPOF.

For example, when asked:

```text
what is spof?
```

it could respond with the ranking:

```text
We have 56 single points of failure...
```

That did not answer the definition question.

Result:

The chatbot now explains:

```text
SPOF means Single Point of Failure.
```

Then it explains the concept in the TruPulse context.

## 5. Uploaded Notes Query Guard

File changed:

```text
backend/main.py
```

Change:

Added `_is_uploaded_note_query()` and restricted uploaded text note search to explicit note/file/document questions.

Why:

The chatbot sometimes answered unrelated questions from an uploaded note, such as `assignment_ntier_text.txt`.

That caused confusing responses like:

```text
I found this in the uploaded text note assignment_ntier_text.txt...
```

when the user was asking about SPOF evidence.

Result:

Uploaded notes are now searched only when the user asks about:

```text
uploaded note
text note
uploaded text
assignment
file note
document search
```

This prevents irrelevant note answers from overriding analytics answers.

## 6. SPOF Evidence Follow-Up

File changed:

```text
backend/main.py
```

Change:

Added `_format_spof_evidence_answer()` and a follow-up branch for questions like:

```text
How can you say they have undocumented knowledge?
Where is the evidence?
Why are they SPOFs?
```

Why:

After the chatbot said employees had no backup and undocumented knowledge, the user asked where that claim came from.

The system needed to answer from the actual dataset, not from uploaded notes or vague language.

Result:

The chatbot can now explain evidence using:

```text
employees.csv -> BackupAvailable = No
knowledge.csv -> DocumentationLevel = Low
```

It gives an evidence-based explanation for the top SPOFs.

## 7. What-If Default Employee

File changed:

```text
frontend/src/pages/WhatIf.jsx
```

Change:

The default selected attrition employee now prefers:

```text
Vikram
```

Fallback:

```text
First employee in the employee list
```

Why:

The What-If page previously selected the first employee from `/employees`, which was often `Sunita`.

For demo purposes, Vikram is a better default because his attrition scenario clearly shows:

```text
Composite score drop
Revenue at risk
SPOF shock
No backup risk
```

Result:

Opening the What-If page now starts with Vikram selected for the attrition scenario.

## 8. What-If Stale Output Fix

File changed:

```text
frontend/src/pages/WhatIf.jsx
```

Change:

Removed restored simulation and pipeline output from `localStorage`.

Added a `clearAnalysis()` function that clears:

```text
simulation result
pipeline result
pipeline visibility
errors
```

It runs when the user changes:

```text
selected employee
scenario type
workload percentage
restructure team
```

Why:

The What-If page was showing old AI Pipeline output immediately on first open.

Also, when the user selected a different employee, the old output stayed visible, making it look like the new employee produced the same result.

Result:

The What-If page now behaves like a fresh simulator:

```text
Open page -> no old output
Change inputs -> previous output clears
Run Simulation -> new Time Machine output appears
Run AI Pipeline Analysis -> new pipeline output appears
```

## 9. AI Pipeline Reliability Fix

File changed:

```text
frontend/src/pages/WhatIf.jsx
```

Change:

The What-If pipeline button now sends:

```json
{
  "use_fallback": true,
  "use_langchain": false
}
```

Why:

`Run AI Pipeline Analysis` was hanging because the backend tried the LLM/LangChain pipeline first.

For a demo, waiting indefinitely looks like nothing happened.

Result:

The button now uses the deterministic fallback pipeline.

It returns immediately with:

```text
Insight Agent
Risk Agent
Simulation Agent
Coaching Agent
Governance Agent
Agent Execution Trace
```

This makes the demo reliable even when local LLM or LangChain execution is unavailable.

## 10. Paste Employee Data Hidden From What-If

File changed:

```text
frontend/src/pages/WhatIf.jsx
```

Change:

Removed `TextInput` from the What-If page render and removed its import.

Important:

The `TextInput` component and `/text-input` API were not deleted. They are still available for use elsewhere.

Why:

The `Paste Employee Data` section was confusing on the What-If page.

A user would expect:

```text
Parse & Add -> employee is added -> simulation changes
```

But the parsed text records are stored separately and do not currently affect:

```text
What-If simulation
Org Health
SPOF Ranking
Skill Gaps
Revenue Risk
```

Result:

The What-If page is now focused:

```text
Scenario controls
Run Simulation
Time Machine
Run AI Pipeline Analysis
Pipeline output
Feedback
```

This avoids showing a feature that does not affect the simulation.

## 11. Calculation Documentation Added

Files added:

```text
docs/ORG_PULSE_TICKER_CALCULATIONS.md
docs/ORG_HEALTH_SCORE_CALCULATIONS.md
docs/CHATBOT_WORKFLOW.md
docs/WHAT_IF_TIME_MACHINE_CALCULATIONS.md
docs/SPOF_RANKING_CALCULATIONS.md
```

Why:

The user repeatedly asked:

```text
Where are these values coming from?
How are these calculated?
Which API routes are used?
What is the formula?
```

Result:

The project now has dedicated explanation documents for:

```text
Org Pulse ticker
Org health score
Chatbot workflow
What-If Time Machine
SPOF ranking
```

These documents make the app easier to explain during review or demo.

## 12. Specific Calculation Explanations Documented

The new documents explain:

```text
Composite Health
Resilience
Trust
Burnout
Retention
Annual Revenue at Risk
Workforce Readiness
Skill Gaps
SPOF Ranking
Time Machine Before/After values
AI Pipeline vs Simulation
Chatbot routing
RAG usage
```

Why:

Several values looked suspicious or unclear without explanation, such as:

```text
115 employees
14 teams
34 projects
56 SPOFs
211 of 468 low-documentation areas
$13.4M revenue at risk
Vikram's $2.7M revenue at risk
```

Result:

Each value now has a documented source, route, and formula.

## 13. Build Verification

After frontend changes, the build was run multiple times:

```text
npm.cmd run build
```

Result:

The frontend build passed.

Only the existing Vite chunk-size warning appeared:

```text
Some chunks are larger than 500 kB after minification
```

No build-breaking errors were introduced.

## 14. API Verification

The following backend routes were tested during the review:

```text
GET /org-health
GET /spof-ranking
GET /employees
POST /whatif
POST /pipeline
```

Key verified results:

```text
Composite score = 47.5
Overall risk = HIGH
SPOF count = 56
Critical SPOFs = 34
Total annual revenue at risk = 13,447,897
Vikram attrition projected composite = 41.7
Vikram revenue at risk = 2,721,856
Deterministic pipeline returns summary and trace immediately
```

## 15. What Improved Overall

These changes improved:

```text
Accuracy
Demo reliability
Explainability
Trust in dashboard numbers
Chatbot answer quality
What-If page clarity
Metric traceability
```

Before, several parts of the app looked like static or unexplained demo data.

After the changes, key values are either:

```text
calculated dynamically from APIs
explained in documentation
or hidden if they do not affect the current workflow
```

## 16. Remaining Recommendations

Recommended next improvements:

```text
Move Paste Employee Data to Upload Data page
Connect parsed text employees to the active scoring dataset if live ingestion is required
Move AI Pipeline output directly above FeedbackPanel for better visibility
Add UI validation when attrition has zero selected employees
Consider tie-breakers in SPOF ranking for employees with severity score = 100
Fix mojibake characters in some UI text if they appear in browser
```

The highest-value next change would be:

```text
Add a tie-breaker to SPOF ranking
```

Current ranking sorts by severity score only. Many employees hit score 100, so their order follows dataset order. A clearer ranking could sort by:

```text
severity_score
revenue_at_risk_usd
dependents_count
low_doc_areas
weekly_hours
```

That would make the ranking feel more intentional when several employees have the same severity score.

