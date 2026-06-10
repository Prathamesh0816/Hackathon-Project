# TruPulse Chatbot: End-To-End Workflow

This document explains how the TruPulse chatbot works from the frontend input box to backend answer generation.

The chatbot is not only a generic LLM chat box. It is a hybrid system:

```text
User question
-> React ChatPanel
-> POST /query
-> deterministic intent routing
-> analytics/scenario functions when possible
-> uploaded text-note search only for explicit note/file questions
-> RAG context building
-> LLM fallback through Ollama
-> response rendered in chat UI
```

## 1. Frontend Entry Point

File:

```text
frontend/src/components/ChatPanel.jsx
```

The dashboard includes the chatbot panel. It starts with a system message:

```text
Ask me anything about your organization's workforce resilience.
I can run simulations, analyze risks, and recommend actions.
```

Suggested questions are defined in the frontend:

```js
const SUGGESTIONS = [
  'What happens if our top 3 engineers leave?',
  'Who are our biggest single points of failure?',
  'Who is the most valuable employee?',
  'Simulate a 30% workload increase across all teams',
  'What is our overall organizational health?',
  'Who should we cross-train first?',
]
```

When the user sends a question, the frontend calls:

```js
fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query, messages }),
})
```

Important:

- `query` is the current user message.
- `messages` is the recent chat history.
- The backend uses this history to answer follow-up questions like "who are they?" or "how do you know that?"

## 2. API Route

Frontend route:

```text
/api/query
```

Backend route:

```http
POST /query
```

Backend file:

```text
backend/main.py
```

Request model:

```python
class QueryRequest(BaseModel):
    query: str
    messages: list[dict] | None = None
```

Main function:

```python
def natural_language_query(req: QueryRequest):
```

At the start, the backend prepares:

```python
query = req.query.lower()
health = compute_org_health()
conversation_text = _latest_conversation_text(req.messages)
spof_data = compute_spof_ranking()
```

This means almost every chatbot answer has access to:

- Current org health
- Current SPOF ranking
- Recent chat context

## 3. Data Sources Used By The Chatbot

The chatbot uses the same seed data as the dashboard:

```text
backend/data/employees.csv
backend/data/projects.csv
backend/data/dependencies.csv
backend/data/knowledge.csv
backend/data/performance.csv
backend/data/workload.csv
backend/data/review_notes.txt
```

These are loaded by:

```text
backend/scoring.py -> load_all()
```

If an uploaded dataset is activated, the active dataset can override the default CSV data.

Uploaded text notes are stored under:

```text
backend/uploaded_files/text/
```

They are searched only when the query explicitly asks about an uploaded note, text note, file note, assignment, or document.

## 4. High-Level Answer Strategy

The `/query` endpoint answers in this order:

```text
1. Data-source questions
2. Follow-up people questions
3. SPOF evidence questions
4. "Why is X critical?" explanations
5. Best performer / valuable employee questions
6. Important employee questions
7. What-if and scenario questions
8. Team-collapse questions
9. Workload and burnout questions
10. SPOF meaning and SPOF ranking questions
11. Skill-gap questions
12. Org-health questions
13. Cross-training/upskilling questions
14. Uploaded text-note questions
15. RAG + LLM fallback
16. Deterministic pipeline fallback
```

The important design idea:

```text
If the backend can answer from structured analytics, it does that first.
The LLM is used only when the question is not covered by deterministic routing.
```

This keeps the chatbot more reliable for business metrics.

## 5. Deterministic Intent Routing

The chatbot has many direct branches in:

```text
backend/main.py -> natural_language_query()
```

These branches check keywords in the lowercased query.

### Data Source Questions

Examples:

```text
where did this data come from?
what files are used?
what data did you use?
```

The backend returns `_format_data_source_answer()`.

It explains:

- Active data source
- Default seed files
- Whether uploaded dataset is active

### Follow-Up People Questions

Examples:

```text
who are they?
who are those employees?
```

The backend checks recent chat history:

```python
conversation_text = _latest_conversation_text(req.messages)
```

If the previous answer discussed valuable employees, it returns valuable names.

If the previous answer discussed SPOFs or risk, it returns top SPOFs.

### SPOF Meaning Questions

Examples:

```text
what is spof?
meaning of spof
define spof
full form of spof
```

The backend now returns a definition before running SPOF analytics:

```text
SPOF means Single Point of Failure.
In TruPulse, a SPOF is an employee, role, or knowledge area that creates business risk
because there is no reliable backup.
```

This was added because earlier the keyword `spof` immediately triggered the ranking response.

### SPOF Analytics Questions

Examples:

```text
who are our biggest SPOFs?
single points of failure
critical failure risk
```

The backend calls:

```python
compute_spof_ranking()
```

File:

```text
backend/analytics_enhanced.py
```

SPOF logic:

```text
SPOF = employee where BackupAvailable = No
```

The response includes:

- Total SPOFs
- Top SPOFs
- Revenue at risk
- Low documentation areas
- Dependents count
- Severity score

### SPOF Evidence Questions

Examples:

```text
how can you say they have undocumented knowledge?
what is the evidence?
how do you know they have no backup?
```

The backend now returns `_format_spof_evidence_answer()`.

It explains the source:

```text
employees.csv -> BackupAvailable = No
knowledge.csv -> DocumentationLevel = Low
```

This fix prevents the chatbot from accidentally searching unrelated uploaded notes like `assignment_ntier_text.txt`.

### Important Employee Questions

Examples:

```text
who is the most important employee?
who is the most critical resource?
important employee
```

The backend maps these to SPOF criticality and returns top SPOF context.

### Best Performer / Valuable Employee Questions

Examples:

```text
who is the best performer?
who is the most valuable employee?
top performers
```

The backend uses performance, workload, revenue/team context, and documentation quality to rank valuable employees.

Helpers include:

```text
_format_best_performers_answer()
_format_valuable_answer()
_valuable_employees()
```

## 6. Scenario And What-If Questions

The chatbot supports scenario questions like:

```text
What happens if our top 3 engineers leave?
What if Vikram leaves?
Simulate a 30% workload increase.
What if the sales team leaves?
```

Backend functions used:

```text
simulate_scenario()
compare_scenarios()
_run_llm_pipeline()
```

Files:

```text
backend/scoring.py
backend/main.py
```

### Employee Departure Scenario

For attrition:

```python
simulate_scenario("attrition", removed_employees=[...])
```

The simulation:

1. Removes selected employees from employee data.
2. Removes their knowledge, workload, and performance rows.
3. Removes dependencies where they are owners.
4. Calculates revenue at risk.
5. Recomputes resilience, trust, burnout, and retention.
6. Recomputes composite score.

Revenue at risk:

```text
team revenue * 35%
```

It counts each affected team only once to avoid double-counting.

### Workload Increase Scenario

For workload:

```python
simulate_scenario("workload_increase", workload_increase_pct=30)
```

The simulation increases:

- Weekly hours
- Overdue tasks

Then it recomputes burnout and health scores.

### Team Restructuring Scenario

For restructure:

```python
simulate_scenario("team_restructuring", restructure_team="Engineering")
```

It removes a sampled percentage of the team and calculates attrition impact.

## 7. Agentic AI Pipeline In Chat

For many scenario answers, the backend also runs:

```python
_run_llm_pipeline(health, scenario)
```

This tries:

```text
1. LangChain/LangGraph pipeline
2. Raw agents pipeline
3. Deterministic fallback templates
```

The fallback chain lives in:

```text
backend/main.py -> _run_llm_pipeline()
```

The five agents are:

```text
1. Insight Agent
2. Risk Agent
3. Simulation Agent
4. Coaching Agent
5. Governance Agent
```

Primary implementation:

```text
backend/agents_langchain.py
```

Raw fallback:

```text
backend/agents.py
```

Deterministic fallback:

```text
backend/agents.py -> run_pipeline_fallback()
```

### Agent Responsibilities

Insight Agent:

```text
Finds top organizational patterns from org health data.
```

Risk Agent:

```text
Identifies SPOFs, cascade risk, and blast radius.
```

Simulation Agent:

```text
Explains before/after scenario impact.
```

Coaching Agent:

```text
Creates mitigation actions such as cross-training, documentation, hiring, or upskilling.
```

Governance Agent:

```text
Checks confidence, reasoning, bias, counter-arguments, and whether human review is needed.
```

## 8. RAG / Company-Aware Retrieval

If no deterministic branch answers the query, the backend calls:

```python
_llm_chat(query, health, messages)
```

File:

```text
backend/main.py
```

This uses:

```python
build_company_rag_context(query, health)
```

File:

```text
backend/rag.py
```

RAG means Retrieval-Augmented Generation.

In this project, RAG gathers relevant company context before asking the LLM.

### RAG Context Includes

Data source context:

```text
Whether active source is CSV, SQLite, or uploaded dataset.
```

Analytics context:

```text
Org health, SPOF summary, skill gaps, knowledge concentration,
succession planning, workforce readiness.
```

Structured records:

```text
Matching employees, teams, performance rows, workload rows,
knowledge rows, projects, dependencies.
```

Document snippets:

```text
README.md
ARCHITECTURE.md
docs/TECHNICAL_EXPLANATION.md
docs/SPECIFICATIONS.md
docs/PROJECT_OVERVIEW.md
backend/data/review_notes.txt
```

Vector retrieval:

```text
Optional ChromaDB retrieval if ENABLE_VECTOR_RAG=1.
Disabled by default.
```

## 9. LLM Fallback

If deterministic routing does not handle the question, `_llm_chat()` builds a prompt with:

- Current org health summary
- Recent conversation history
- RAG context
- User question

It calls:

```python
agents._llm_call()
```

The configured local LLM backend is Ollama.

Default model:

```text
qwen2.5:3b
```

Configuration:

```text
OLLAMA_URL
OLLAMA_MODEL
```

If Ollama is unavailable, the app still has deterministic fallbacks for core demo flows.

## 10. Uploaded Text Notes

Uploaded text notes are searched through:

```text
backend/storage.py -> search_text_notes()
```

The query handler uses:

```text
_format_text_note_answer()
```

This is now guarded by:

```text
_is_uploaded_note_query()
```

Meaning:

```text
The bot only searches uploaded text notes when the user clearly asks about notes,
uploaded text, assignment, file note, or document search.
```

This prevents unrelated uploaded files from being used for workforce analytics answers.

## 11. Response Shape

Most chatbot responses look like:

```json
{
  "answer": "Plain English answer shown in chat",
  "spofs": [...],
  "scenario": {...},
  "summary": {...},
  "actions": [...]
}
```

The frontend always displays:

```js
data.answer
```

If extra structured data exists, `ChatPanel.jsx` renders small helper sections:

```text
Recommended Actions
Top Valuable Employees
Top SPOFs
```

## 12. Frontend Rendering Logic

After the backend returns JSON, `ChatPanel.jsx` appends:

```js
{
  role: 'assistant',
  text: data.answer || data.summary?.insight?.headline || 'Analysis complete...',
  data,
}
```

Then it optionally renders:

- `data.summary.coaching.actions`
- `data.actions`
- `data.valuable_employees`
- `data.spofs`

This is why SPOF answers can show a short list below the chatbot answer.

## 13. Example Flows

### Example 1: "What is SPOF?"

```text
User asks: what is spof?
Frontend sends POST /query
Backend detects definition intent
Backend returns SPOF definition
Frontend displays answer
```

No LLM is needed.

### Example 2: "Who are our biggest SPOFs?"

```text
User asks SPOF ranking question
Backend calls compute_spof_ranking()
Backend returns total SPOFs, top names, revenue at risk
Frontend displays answer and top SPOF list
```

No LLM is needed.

### Example 3: "How can you say they have undocumented knowledge?"

```text
User asks follow-up evidence question
Backend checks recent conversation for SPOF context
Backend returns CSV evidence:
  employees.csv -> BackupAvailable = No
  knowledge.csv -> DocumentationLevel = Low
```

No uploaded note search is used.

### Example 4: "What happens if our top 3 engineers leave?"

```text
User asks scenario question
Backend finds top engineering SPOFs
Backend runs simulate_scenario("attrition", removed_employees=[...])
Backend runs agent pipeline/fallback for interpretation
Backend returns projected score, revenue at risk, and recommendations
Frontend displays answer and actions
```

### Example 5: "Explain something not covered by rules"

```text
User asks open-ended question
No deterministic branch matches
Backend builds RAG context
Backend sends prompt to local LLM
Backend returns generated answer grounded in company context
```

## 14. Important Backend Functions

| Function | File | Purpose |
|---|---|---|
| `natural_language_query()` | `backend/main.py` | Main chatbot route |
| `_latest_conversation_text()` | `backend/main.py` | Builds recent-history text for follow-ups |
| `_mentioned_employees()` | `backend/main.py` | Finds employee names in a query |
| `_format_top_spof_answer()` | `backend/main.py` | Formats critical employee/SPOF answer |
| `_format_spof_reason()` | `backend/main.py` | Explains why an employee is critical |
| `_format_spof_evidence_answer()` | `backend/main.py` | Explains CSV evidence for undocumented knowledge |
| `_format_text_note_answer()` | `backend/main.py` | Answers explicit uploaded-note questions |
| `_llm_chat()` | `backend/main.py` | RAG + LLM fallback |
| `_run_llm_pipeline()` | `backend/main.py` | Agent pipeline with fallback chain |
| `build_company_rag_context()` | `backend/rag.py` | Builds retrieval context for LLM |
| `compute_org_health()` | `backend/scoring.py` | Org health scores |
| `simulate_scenario()` | `backend/scoring.py` | What-if simulations |
| `compute_spof_ranking()` | `backend/analytics_enhanced.py` | SPOF ranking and revenue risk |
| `compute_skill_gaps()` | `backend/analytics_enhanced.py` | Skill gap analysis |

## 15. How To Test

Start backend:

```powershell
cd "E:\Prathamesh Hackathon\Hackathon-Project\backend"
uvicorn main:app --reload --port 8000
```

Test query API directly:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"what is spof?","messages":[]}'
```

Test SPOF ranking:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"who are our biggest single points of failure?","messages":[]}'
```

Test SPOF evidence follow-up:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"how can you say they have undocumented knowledge?","messages":[{"role":"assistant","text":"We have 56 single points of failure. The highest risk: Farhan, Lalit, Tanvi."}]}'
```

Test scenario:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:8000/query" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"what happens if our top 3 engineers leave?","messages":[]}'
```

## 16. Key Design Notes

- The chatbot is analytics-first, LLM-second.
- Structured backend calculations are preferred over free-form generation.
- RAG context grounds open-ended LLM answers in company data.
- Uploaded notes are intentionally restricted to explicit note/file questions.
- Agentic AI is used for scenario interpretation, coaching actions, and governance.
- Deterministic fallback keeps the demo working even if the local LLM is unavailable.

