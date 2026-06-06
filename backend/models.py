"""
TruPulse AI — Formal API Specification Models
Spec-driven development: all request/response contracts are typed via Pydantic.
"""

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class WhatIfRequest(BaseModel):
    scenario_type: str = "attrition"
    removed_employees: list[str] = []
    workload_increase_pct: int = 0
    restructure_team: Optional[str] = None


class PipelineRequest(BaseModel):
    scenario_type: str = "attrition"
    removed_employees: list[str] = []
    workload_increase_pct: int = 0
    restructure_team: Optional[str] = None
    use_fallback: bool = False


class FeedbackRequest(BaseModel):
    employee: str
    action_title: str
    decision: str  # accept | veto | modify
    reason: str = ""


class QueryRequest(BaseModel):
    query: str


class TextInputRequest(BaseModel):
    text: str = Field(..., description="Plain text employee data, one employee per line")
    source: str = "manual"


class SuggestionAction(BaseModel):
    id: str
    title: str
    description: str
    type: str  # cross_train | document | hire | restructure | upskill
    target_employee: str = ""
    target_team: str = ""
    estimated_impact: str = ""
    estimated_cost_usd: int = 0


class ApplyDecisionsRequest(BaseModel):
    accepted_ids: list[str] = []
    rejected_ids: list[str] = []
    modified: list[dict[str, Any]] = []
    user_added: list[dict[str, Any]] = []


class ScenarioRunRequest(BaseModel):
    scenario_type: str = "attrition"
    removed_employees: list[str] = []
    workload_increase_pct: int = 0
    restructure_team: Optional[str] = None
    reaction_type: str = "standard"  # standard | pipeline | human_loop | agent_intervention | random
    probability: Optional[int] = None  # 0-100, None = use default


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------

class IndicatorScore(BaseModel):
    score: float
    risk_level: str
    details: dict[str, Any] = {}


class OrgHealthResponse(BaseModel):
    composite_score: float
    overall_risk: str
    employee_count: int
    team_count: int
    project_count: int
    indicators: dict[str, IndicatorScore]


class WhatIfComparison(BaseModel):
    baseline_composite: float
    projected_composite: float
    composite_delta: float
    indicator_deltas: dict[str, Any]
    revenue_at_risk_usd: float


class WhatIfResponse(BaseModel):
    baseline: dict[str, Any]
    projected: dict[str, Any]
    comparison: WhatIfComparison


class ScenarioRunResponse(BaseModel):
    reaction_type: str
    scenario_params: dict[str, Any]
    baseline: dict[str, Any]
    projected: dict[str, Any]
    comparison: WhatIfComparison
    pipeline: Optional[dict[str, Any]] = None
    human_decisions: Optional[list[dict[str, Any]]] = None
    agent_suggestions: Optional[list[dict[str, Any]]] = None
    probability: int = 50
    expected_delta: float = 0
    expected_revenue_loss: int = 0
    risk_weighted_score: float = 0  # composite considering probability and impact


class FeedbackResponse(BaseModel):
    id: int
    employee: str
    action_title: str
    decision: str
    reason: str


class SuggestionResponse(BaseModel):
    suggestions: list[SuggestionAction]
    total_count: int


class RecalculateResponse(BaseModel):
    before_score: float
    after_score: float
    delta: float
    applied_actions: list[dict[str, Any]]
    projected_indicators: dict[str, Any]


class TextInputResponse(BaseModel):
    parsed_count: int
    employees: list[dict[str, str]]
    message: str


class HealthCheckResponse(BaseModel):
    message: str
    version: str
    endpoints: list[str]
