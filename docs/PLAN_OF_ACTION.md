# TruPulse AI — Plan of Action & Time Management (2-Day Production Build)

> This document outlines how to take the current hackathon prototype and convert it into a production-ready real-world system in 2 calendar days. Each section has time estimates, task assignments, and dependencies.

---

## Overview

The hackathon prototype is **architecturally sound** but needs these upgrades for production:
- **Durable storage** (PostgreSQL/SQLite instead of in-memory)
- **Authentication & authorization** (RBAC)
- **Multi-tenant support** (org_id isolation)
- **Production AI** (fine-tuned model or GPT-4 API)
- **Monitoring & logging** (Prometheus + structured logs)
- **Real user data onboarding** (HRIS integration)

Total estimated effort: **2 days × 6 people = 96 person-hours**

---

## Phase 0: Pre-Work (Night Before Day 1)

| Task | Who | Time | Details |
|------|-----|------|---------|
| Audit current codebase | Aradhana | 2h | Identify all in-memory stores, hardcoded paths, and single-tenant assumptions |
| Review scoring formulas with real HR data | Santosh | 2h | Validate heuristics against actual employee data (not synthetic) |
| Set up production environment | Lokesh | 2h | Provision cloud VM or Kubernetes namespace, CI/CD pipeline |
| Define data schema for PostgreSQL | Aradhana + Santosh | 2h | Tables: employees, teams, projects, knowledge_areas, feedback, reports |

---

## Day 1: Foundation (08:00 – 22:00)

### Slot 1: Data Layer (08:00 – 12:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Replace in-memory stores with SQLite/PostgreSQL | Aradhana | 3h | Generate SQLAlchemy models for Employee, Team, Project, KnowledgeArea, Feedback, Report |
| Create Alembic migrations | Aradhana | 1h | Initial migration + seed data migration |
| Migrate CSV data to DB | Aradhana | 1h | Write import script that reads CSV → SQLAlchemy inserts |
| Add unique constraints, indices, foreign keys | Aradhana | 1h | Ensure data integrity — no duplicate employees, FK to teams |

**Dependency:** Pre-work audit must be complete.

### Slot 2: Authentication & Multi-Tenancy (08:00 – 12:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Add JWT auth (FastAPI + python-jose) | Prathamesh | 2h | Login endpoint, token verification, current_user dependency |
| Add RBAC middleware | Prathamesh | 1h | Roles: admin, manager, viewer; decorators for endpoints |
| Add multi-tenant isolation | Aradhana | 2h | Every query scoped by org_id; tenant header in requests |
| Frontend login page | Prathamesh | 1h | Login form, token storage, auth context, protected routes |

**Dependency:** Data layer (Slot 1) must be partially complete.

### Slot 3: AI Pipeline Production Hardening (08:00 – 12:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Add configurable LLM provider | Santosh | 2h | LangChain abstraction: Ollama / OpenAI / Anthropic — pick via env var |
| Add prompt caching for repeated queries | Santosh | 1h | LangChain cache (SQLite or Redis), cache agent outputs by query hash |
| Add rate limiting and cost tracking | Santosh | 1h | LangChain callbacks for token usage tracking, cost estimation |
| Test with GPT-4-mini + Ollama fallback | Santosh | 1h | Verify both providers produce consistent Pydantic-validated output |

**Dependency:** None — can work in parallel.

### Slot 4: Frontend Refactor (12:00 – 16:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Add loading skeletons to all pages | Prathamesh | 1h | Skeleton components for Dashboard, Employees, What-If |
| Add error boundaries | Prathamesh | 1h | React ErrorBoundary wrapper per page with retry button |
| Add form validation (React Hook Form) | Prathamesh | 1h | Validate What-If inputs, text input, feedback forms |
| Add pagination to Employees table | Prathamesh | 1h | Server-side pagination via query params, page size config |

**Dependency:** None — can work in parallel.

### Slot 5: Analytics & Scoring Optimization (12:00 – 16:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Profile scoring engine for large datasets | Aradhana | 1h | Test with 10K employees, optimize O(n) loops |
| Add caching layer (Redis) for analytics | Aradhana | 2h | Cache org-health, spof-ranking, skill-gaps; invalidate on data change |
| Add async report generation | Aradhana | 1h | Move 11-section report to background task + WebSocket progress |

**Dependency:** Data layer (Slot 1) must be complete.

### Slot 6: Vector DB Scaling (12:00 – 16:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Benchmark ChromaDB with 10K embeddings | Santosh | 1h | Query latency, memory usage, disk size |
| Evaluate FAISS vs ChromaDB for scale | Santosh | 1h | FAISS is faster for >100K vectors; ChromaDB better for <50K |
| Add background re-indexing | Santosh | 1h | Re-index embeddings when employee data changes (hook via SQLAlchemy events) |
| Add embedding model swap | Santosh | 1h | Make model configurable: `text-embedding-3-small` (OpenAI) or `all-MiniLM-L6-v2` (local) |

**Dependency:** None — can work in parallel.

### Slot 7: Testing & QA (16:00 – 20:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Write unit tests for scoring engine | Sopan | 1.5h | pytest: test compute_org_health, simulate_scenario, compare_scenarios |
| Write unit tests for analytics modules | Sopan | 1.5h | pytest: test all 6 modules with known inputs/outputs |
| Write API integration tests | Sopan | 1.5h | FastAPI TestClient: test all 15+ endpoints, auth, error cases |
| Test report format generation | Sopan | 0.5h | Verify HTML/Text/PDF all generate valid output |
| Test multi-tenant isolation | Sopan | 0.5h | Tenant A cannot see Tenant B data |

**Dependency:** Slots 1 + 2 + 3 must be stable.

### Slot 8: Monitoring & Logging (16:00 – 20:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Add structured logging (JSON logs) | Aradhana | 1h | Log all API requests, errors, AI pipeline latency |
| Add Prometheus metrics | Aradhana | 1h | Request count, latency histogram, error rate, score distribution |
| Add Grafana dashboard | Lokesh | 1h | Dashboard with API health, AI pipeline metrics, active tenants |
| Add health check endpoint with dependencies | Aradhana | 0.5h | `/health` with DB, ChromaDB, LLM provider status |
| Add alerting (email/Slack webhook) | Lokesh | 0.5h | Alert on error rate >5%, AI pipeline failures |

**Dependency:** None — can work in parallel.

### Slot 9: Documentation & Final Integration (20:00 – 22:00) — 2 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Update API docs for new production endpoints | Varad | 1h | Add auth, multi-tenant, caching to docs |
| Write production runbook | Varad | 1h | Deployment, backup/restore, scaling, incident response |
| Final integration smoke test | Everyone | 1h | End-to-end: login → upload → dashboard → what-if → feedback → report |
| Tag release v2.0-production | Lokesh | 0.5h | Git tag, CHANGELOG, release notes |

---

## Day 2: Polish & Deploy (08:00 – 18:00)

### Slot 10: Performance Optimization (08:00 – 12:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Database query optimization | Aradhana | 2h | Add missing indices, optimize JOINs, analyze explain plans |
| Frontend bundle optimization | Prathamesh | 1h | Code-split pages, lazy-load Recharts, tree-shake unused Tailwind |
| CDN setup for static assets | Lokesh | 1h | CloudFront / Cloudflare for frontend assets |

### Slot 11: UX Enhancements (08:00 – 12:00) — 4 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Add dark mode | Prathamesh | 1h | Tailwind `dark:` variant, theme toggle |
| Add keyboard shortcuts | Prathamesh | 1h | `Ctrl+Enter` to run pipeline, `p` to open report |
| Add tour/onboarding | Prathamesh | 2h | Shepherd.js or custom onboarding overlay for new users |

### Slot 12: Security Audit (12:00 – 14:00) — 2 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Dependency vulnerability scan | Sopan | 0.5h | `pip-audit` + `npm audit`, fix critical issues |
| OWASP Top 10 check | Sopan | 1h | SQL injection (SQLAlchemy handles it), XSS (React handles it), CSRF, rate limiting |
| Penetration test basic | Sopan | 0.5h | Test auth bypass, tenant isolation bypass, data leakage |

### Slot 13: Load Testing (12:00 – 14:00) — 2 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Write locustfile for load test | Santosh | 1h | Simulate 100 concurrent users, mixed read/write |
| Run load test, identify bottlenecks | Santosh | 1h | Target: <500ms p95 for all endpoints at 100 RPS |

### Slot 14: Production Deployment (14:00 – 16:00) — 2 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Docker image optimization | Lokesh | 1h | Multi-stage builds, reduce image size <200MB |
| Deploy to production (cloud VM) | Lokesh | 1h | Docker Compose on cloud VM or Kubernetes |
| SSL/TLS setup | Lokesh | 0.5h | Let's Encrypt cert, HTTPS redirect |
| DNS + reverse proxy (Nginx/Traefik) | Lokesh | 0.5h | Configure domain, routing, WebSocket support |

### Slot 15: Final Testing & Go-Live (16:00 – 18:00) — 2 hours

| Task | Who | Time | Details |
|------|-----|------|---------|
| Full E2E on production | Sopan | 1h | Test login, upload real data, run all features |
| Rollback test | Sopan | 0.5h | Deploy old version, verify rollback works |
| Monitor after deployment | Everyone | 0.5h | Watch Grafana, fix any immediate issues |
| Go live! | Lokesh | 0h | Flip DNS, announce |

---

## Time Summary (96 Person-Hours)

| Phase | Hours | People | Person-Hours |
|-------|-------|--------|-------------|
| Pre-work | 8 | 4 | 8 |
| Day 1 Slots 1-9 | 14 | 6 | 84 |
| Day 2 Slots 10-15 | 10 | 6 | 60 |
| **Total** | | | **152** |

> 152 hours of work with 6 people = ~25 hours each over 2 days. Tight but achievable with the right prioritization.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| PostgreSQL migration breaks data | Medium | High | Run with SQLite first (file-based, no server needed); validate data before switching |
| AI provider API key issues | Medium | Medium | Keep Ollama fallback; Ollama runs completely offline |
| Load test reveals bottleneck | High | Medium | Use caching layer (Redis) as first-line defense; horizontally scale API with Docker Compose replicas |
| Frontend regressions | Medium | High | Sopan runs E2E tests after every merged PR; Cypress test suite in CI |
| Team member unavailable | Low | Medium | Cross-train: each person has a backup from a different discipline |

---

## Critical Path

```
Pre-work → Slot 1 (Data Layer) → Slot 5 (Analytics) → Slot 7 (Testing)
                                                    → Slot 9 (Final Integration)
Pre-work → Slot 2 (Auth) → Slot 7 (Testing)
Slot 3 (AI Pipeline) → Slot 7 (Testing)
```

Slots 3, 4, 6, 8 can run fully in parallel. The critical path is ~14 hours (Day 1).

---

## Contingency: If We Run Out of Time

Cut these features (in order):
1. Dark mode + keyboard shortcuts (Slot 11) — 4h saved
2. Load testing beyond basic (Slot 13) — 2h saved
3. Prometheus/Grafana (Slot 8) — 2.5h saved (keep structured logging)
4. Multi-tenant isolation — reduce to simple org_id column without full RBAC
5. AI provider abstraction — keep Ollama-only for MVP, add API key later

---

## Tools & Services Needed

| Purpose | Tool | Cost |
|---------|------|------|
| Cloud hosting | DigitalOcean / AWS EC2 / Azure VM | ~$20/month |
| Database | PostgreSQL (Supabase free tier or self-hosted) | Free – $25/month |
| CI/CD | GitHub Actions | Free |
| Monitoring | Grafana + Prometheus (self-hosted) or Datadog | Free – $15/month |
| CDN | Cloudflare (free tier) | Free |
| AI API (optional) | OpenAI GPT-4-mini | ~$2/10K queries |
| Redis | Upstash (free tier) or self-hosted | Free |
