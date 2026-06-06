# TruPulse AI — Q&A Prep for Judges

> Print this. Prathamesh holds it during Q&A. Varad knows every answer.

---

## Technical Questions

### Q: "Where's the ML model? This looks like heuristics."
> *"It's a deterministic scoring function with documented weights. We chose interpretability over opacity — HR leaders need to explain why an employee is flagged, not trust a black box. The architecture is XGBoost-ready: swap one import in `scoring.py`, the API contract doesn't change."*

### Q: "Are the AI agents real or just prompts?"
> *"Five sequential LLM calls with role-specific prompts. Each call has a different system prompt — Insight, Risk, Simulation, Coaching, Governance. The execution trace in the UI shows every agent's input, output, and latency. It's not autonomous agentic orchestration, but it follows the same architectural pattern."*

### Q: "How does the Governance Agent work?"
> *"It receives the outputs of all 4 other agents, then generates a confidence score, reasoning trace, bias checks, and a counter-argument. If confidence is below 60% or the scenario involves compensation/personnel decisions, it flags for human review."*

### Q: "What happens when Ollama is down?"
> *"The pipeline auto-falls back to deterministic templates. The UI doesn't change — same 5 agent boxes, same recommendations — just with a 'fallback mode' indicator in the trace. Demo never breaks."*

### Q: "How do you handle data privacy?"
> *"Everything runs locally. Ollama is on localhost. No data ever leaves your infrastructure. No API keys, no cloud dependency. For multi-tenant production, we'd add encryption at rest and row-level security in PostgreSQL."*

### Q: "Can I see the XGBoost model?"
> *"The XGBoost scaffold is in `scoring.py` lines 6-7 — it says 'Production architecture is XGBoost-ready: swap compute_resilience_score() with a trained model.' Today we use a heuristic because we don't have years of HRIS training data. The architecture is designed so you drop in a model later."*

### Q: "What's the tech stack?"
> *"FastAPI backend, React + Tailwind frontend, Ollama for LLM, CSV/SQLite for data. Docker Compose to run everything. PostgreSQL-ready via SQLAlchemy."*

---

## Business Questions

### Q: "Why would I buy this instead of Workday/BambooHR?"
> *"Those report what happened. We simulate what will happen. Workday tells you someone quit. We tell you who's going to quit, what it costs, and how to prevent it — before they update their LinkedIn. We sit on top of your existing HRIS, not replace it."*

### Q: "What's the ROI?"
> *"For a 200-person company: $400K–$1.2M in annual workforce risk identified. The first prevented key-employee departure pays for the platform for 10 years. Our demo data shows 56 SPOFs putting $54.6M at risk — de-risking all of them costs $840K. That's 65:1 ROI."*

### Q: "Is this for HR or for leadership?"
> *"Both. HR uses it for succession planning and upskilling. Leadership uses it for scenario planning — 'what if our top engineer leaves?' The report is executive-ready in one click."*

### Q: "How long to set up?"
> *"Upload three CSVs — employees, projects, dependencies — and see your org health in 30 seconds. Most HR systems export these natively."*

### Q: "What's the pricing model?"
> *"For the hackathon: open-source. For production: per-seat SaaS with a free tier for orgs under 50 employees. Enterprise: on-prem deployment."*

---

## Presentation/Demo Questions

### Q: "What was the hardest part?"
> *"Building the dependency graph visualization with a custom force-directed layout. We wanted judges to see the org structure come alive — nodes pulsing, connections lighting up — not just another table."*

### Q: "What would you add next?"
> *"Three things: (1) PostgreSQL for multi-tenant, (2) XGBoost trained on real HRIS data, (3) Slack integration that alerts managers when an employee's burnout risk crosses a threshold."*

### Q: "How did you split the work?"
> *"6 people, 3 tracks: Aradhana owned backend + database, Santosh owned AI + Ollama integration, Prathamesh owned frontend + presentation, Sopan owned QA, Varad owned business analysis + docs, Lokesh owned demo + coordination. We used this document as our single source of truth."*

### Q: "What makes this different from other hackathon projects?"
> *"Most projects are tools looking for a problem. We started with a specific problem — 'Vikram is a single point of failure' — and built the solution around that story. The product works, the data is real, and the business case is quantified."*

---

## The Closing Line (Prathamesh, after last question)

> *"Every dashboard tells you what already happened. TruPulse tells you what's about to. The companies that win the next decade won't be the ones with the most data — they'll be the ones who act on it before it's too late."*
