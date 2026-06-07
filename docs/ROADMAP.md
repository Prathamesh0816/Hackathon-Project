# TruPulse AI — Product Roadmap

## Vision
> *"Every organization in the world knows its resilience score — just like it knows its revenue, headcount, and NPS."*

---

## Phase 0: Hackathon MVP ✅ (Current)
- **5-agent LangChain + LangGraph pipeline** with Pydantic validation, revision loop
- **9 LangChain tools** wrapping scoring and analytics engines
- **Org health scoring** (4 indicators: Resilience, Trust, Burnout, Retention)
- **SPOF detection** (56 SPOFs in demo data)
- **Scenario simulation** (3 types: attrition, workload, restructure)
- **Time Machine comparison** (before/after with composite deltas)
- **Dependency graph visualization** (force-directed layout)
- **AI Chat** (natural language scenario queries)
- **Human-in-the-loop feedback** (accept/reject/edit AI recommendations)
- **Governance Panel** (confidence scores, bias checks, counter-arguments)
- **Management Report** (HTML/PDF/Text — 1-click)
- **Offline-capable** (Ollama local LLM, no cloud dependency)

---

## Phase 1: Production Hardening (Months 0–3)

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| PostgreSQL migration (SQLAlchemy) | P0 | 3 days | Multi-tenant, ACID compliance, audit logging |
| JWT authentication + RBAC | P0 | 2 days | Admin/Manager/Viewer roles |
| API rate limiting & cost tracking | P1 | 1 day | Avoid abuse, track usage |
| Structured logging (JSON) | P1 | 0.5 day | Debugging, audit trail |
| Unit test suite (pytest, 80%+ coverage) | P0 | 3 days | Regression prevention |
| E2E test suite (Cypress) | P1 | 2 days | Frontend stability |
| Docker Compose health checks | P1 | 0.5 day | Production reliability |
| CI/CD pipeline (GitHub Actions) | P0 | 1 day | Automated test → deploy |
| LangChain caching layer (Redis/SQLite) | P2 | 1 day | Faster repeated queries |
| Embedding model config swap (env var) | P2 | 0.5 day | Flexibility for different models |

**Milestone:** Production-ready v2.0 — deployable to any cloud or on-prem.

---

## Phase 2: AI & ML Deepening (Months 3–6)

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| **XGBoost/LightGBM scoring model** | P0 | 2 weeks | ML-predictive instead of heuristic |replace scoring.py heuristics with trained models|
| **Historical data training pipeline** | P0 | 1 week | Train on past attrition data to calibrate weights |
| **OpenAI/Claude provider support** | P1 | 2 days | Switch between Ollama/OpenAI/Anthropic via env var |
| **GPT-4-mini / Claude Haiku for low-latency agents** | P1 | 1 day | Faster agent responses (optional cloud) |
| **LangChain callback-based monitoring** | P2 | 1 day | Token usage, latency, cost per pipeline run |
| **LLM prompt A/B testing framework** | P2 | 2 days | Optimize system prompts systematically |
| **Knowledge graph (Neo4j) for dependency mapping** | P2 | 1 week | Richer relationship model than adjacency lists |
| **Anomaly detection (auto-encoder)** | P3 | 1 week | Detect unusual behavior patterns automatically |

**Milestone:** AI-predictive v3.0 — heuristics replaced by ML, cloud LLM optional.

---

## Phase 3: Integrations & Scale (Months 6–12)

| Feature | Priority | Effort | Impact |
|---------|----------|--------|--------|
| **Workday API integration** | P0 | 2 weeks | Auto-sync employee data |
| **BambooHR API integration** | P0 | 1 week | Same — auto-sync |
| **Slack bot** (daily SPOF digests) | P1 | 1 week | Proactive alerts to managers |
| **Microsoft Teams integration** | P1 | 1 week | Same — enterprise preferred channel |
| **Okta/SSO integration** | P1 | 2 days | Enterprise auth requirement |
| **Multi-org admin dashboard** | P1 | 1 week | For consulting partners/HRIS resellers |
| **Bulk CSV export (all data, any format)** | P2 | 2 days | Data portability |
| **Custom report builder** (drag-drop) | P2 | 2 weeks | Self-serve BI-style reports |
| **Compliance templates** (SOC2, GDPR, ISO 27001) | P2 | 1 week | Enterprise procurement requirement |
| **Performance: 100K employee benchmark** | P2 | 3 days | Prove scale; optimize for large orgs |
| **FAISS vector search (replace ChromaDB for scale)** | P3 | 3 days | Faster semantic search at >100K vectors |

**Milestone:** Enterprise v4.0 — connected to HRIS, scalable to 100K employees.

---

## Phase 4: Industry Solutions (Months 12–18)

| Solution | Target | Key Feature | Revenue Potential |
|----------|--------|-------------|-------------------|
| **TruPulse for Healthcare** | Hospitals, clinics | Regulatory compliance risk, shift dependency, certification tracking | $30K–$150K/account |
| **TruPulse for Manufacturing** | Factories, supply chain | Shift-critical roles, safety certification dependencies, union transition planning | $25K–$100K/account |
| **TruPulse for Financial Services** | Banks, fintech, insurance | Regulatory SPOFs (compliance officers), audit trail, continuity planning | $50K–$200K/account |
| **TruPulse for Gov/Defense** | Government agencies | Clearance-level dependencies, succession for classified roles, zero-trust reporting | Custom ($100K+) |

**Milestone:** Industry-specific v5.0 — 4 vertical solutions, 10x addressable market.

---

## Phase 5: Platform Ecosystem (Months 18–24)

- **Public API** (REST + GraphQL) — 3rd-party developers build on TruPulse
- **Marketplace** — community scenario templates, report templates, integrations
- **TruPulse Benchmark** — anonymized aggregate data: "how your org compares to peers"
- **Mobile app** — push alerts: "Your SPOF score changed" / "Recommended action updated"
- **White-label** — HRIS platforms resell TruPulse as embedded module
- **TruPulse for Individuals** — personal career resilience dashboard (freemium)

---

## What We'd Say to a Judge Asking "What's Next?"

> *"Phase 1 is production hardening — PostgreSQL, auth, CI/CD — making this deployable in any enterprise tomorrow. Phase 2 replaces our heuristics with XGBoost trained on actual HRIS data. Phase 3 connects to Workday and Slack so alerts land in the tools leaders already use. Phase 4 builds industry-specific versions — healthcare, manufacturing, financial services. Phase 5 opens the platform. We've priced it from free (50-person orgs) to enterprise ($5K/mo). Payback is under 6 days. Our first feature after the hackathon is the Workday integration — because that's what the first paying customer will ask for."*
