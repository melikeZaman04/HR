from datetime import datetime

from pydantic import BaseModel, Field


class CreateScenarioRequest(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=120)
    applied_role: str = Field(min_length=1)
    experience_years: int = Field(ge=0)
    tech_test_score: int = Field(ge=0, le=100)
    avg_months_per_job: int = Field(ge=0)
    glassdoor_score: float = Field(ge=1.0, le=5.0)
    expected_salary: int = Field(gt=0)
    salary_currency: str = Field(default="TRY", min_length=3, max_length=3, description="ISO 4217 currency code")


class CreateScenarioResponse(BaseModel):
    scenario_id: int


class AgentOutputResponse(BaseModel):
    agent_name: str
    score: int
    rationale: str


class ScenarioResponse(BaseModel):
    id: int
    candidate_name: str
    applied_role: str
    experience_years: int
    tech_test_score: int
    avg_months_per_job: int
    glassdoor_score: float
    expected_salary: int
    salary_currency: str
    created_at: datetime


class ScenarioListResponse(BaseModel):
    items: list[ScenarioResponse]
    limit: int
    offset: int


class SimulationResponse(BaseModel):
    scenario_id: int
    agent_outputs: list[AgentOutputResponse]
    final_score: float
    final_decision: str


class SimulationDetailResponse(BaseModel):
    scenario: ScenarioResponse
    agent_outputs: list[AgentOutputResponse]
    final_score: float
    final_decision: str


class ClassificationRequest(BaseModel):
    """Request to classify a candidate profile without saving."""
    candidate_name: str = Field(min_length=1, max_length=120)
    applied_role: str = Field(min_length=1)
    experience_years: int = Field(ge=0)
    tech_test_score: int = Field(ge=0, le=100)
    avg_months_per_job: int = Field(ge=0)
    glassdoor_score: float = Field(ge=1.0, le=5.0)
    expected_salary: int = Field(gt=0)
    salary_currency: str = Field(default="TRY", min_length=3, max_length=3)


class AgentWeightsResponse(BaseModel):
    """Recommended agent weights based on candidate profile."""
    Strategy: float
    Salary: float
    Culture: float


class ClassificationResponse(BaseModel):
    """Candidate profile classification result (heuristic rule-based engine)."""
    primary_type: str = Field(description="Primary scenario classification")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    secondary_type: str | None = Field(description="Secondary classification if applicable")
    type_scores: dict[str, float] = Field(description="Confidence scores for all types")
    recommended_weights: AgentWeightsResponse = Field(description="Suggested agent weights")
    classification_reasoning: str = Field(description="Human-readable reasoning")
