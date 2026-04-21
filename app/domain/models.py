from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Literal


class FinalDecision(str, Enum):
    """
    Final decision outcome from the aggregator.
    In HireSync AI context:
    - APPROVE = Mülakata Al (HIRE/PROCEED)
    - REVISE  = Beklet (HOLD/REVIEW)
    - REJECT  = Reddet (REJECT)
    """
    APPROVE = "APPROVE"
    REVISE = "REVISE"
    REJECT = "REJECT"


# Type alias for agent stance
Stance = Literal["support", "oppose", "neutral"]


@dataclass(frozen=True)
class ScenarioInput:
    """
    Unified candidate input contract for all HR agents.
    
    Strategy Agent:
      - experience_years: Adayın sektördeki deneyim yılı (int)
      - tech_test_score: Teknik test skoru (int, 0-100)
    
    Culture Agent:
      - avg_months_per_job: Adayın bir şirkette ortalama kalma süresi (ay) (int)
      - glassdoor_score: Adayın eski şirketinin ortalama kültürel skoru (float, 1.0 - 5.0)
    
    Salary Agent:
      - expected_salary: Adayın maaş beklentisi (int)
      - salary_currency: ISO 4217 para birimi kodu (str, varsayılan: "TRY")
    """
    candidate_name: str
    applied_role: str
    experience_years: int
    tech_test_score: int
    avg_months_per_job: int
    glassdoor_score: float
    expected_salary: int
    salary_currency: str = "TRY"


@dataclass(frozen=True)
class ScenarioRecord:
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


@dataclass(frozen=True)
class AgentResult:
    """Legacy agent result for backward compatibility with aggregator."""
    agent_name: str
    score: int
    rationale: str


@dataclass(frozen=True)
class AgentMessage:
    """
    Standardized agent communication message following the project protocol.
    
    Each agent produces this message format during discussion rounds.
    Agents can read previous messages and update their stance/confidence.
    
    Attributes:
        agent: Agent identifier (e.g., "Strategy", "Culture", "Salary", "Question")
        stance: Position on the candidate ("support", "oppose", "neutral")
        confidence: Confidence level in the stance (0.0 to 1.0)
        reasoning: Explanation of the agent's analysis and position
        metrics: Agent-specific numerical metrics dict
            - Strategy: {"tech_alignment": 0-10, "experience_depth": 0-10}
            - Culture: {"churn_risk": 0-10, "cultural_fit": 0-10}
            - Salary: {"budget_fit": 0-10, "market_alignment": 0-10}
        round_number: The discussion round this message was produced in (1-indexed)
    """
    agent: str
    stance: Stance
    confidence: float
    reasoning: str
    metrics: dict = field(default_factory=dict)
    round_number: int = 1
    
    def __post_init__(self):
        """Validate field constraints."""
        if self.stance not in ("support", "oppose", "neutral"):
            raise ValueError(f"Invalid stance: {self.stance}. Must be 'support', 'oppose', or 'neutral'.")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.round_number < 1:
            raise ValueError(f"round_number must be >= 1, got {self.round_number}")
    
    def to_legacy_result(self) -> "AgentResult":
        """
        Convert to legacy AgentResult for backward compatibility with aggregator.
        
        Score mapping:
            - support: confidence * 100
            - neutral: 50
            - oppose: (1 - confidence) * 100
        """
        if self.stance == "support":
            score = int(self.confidence * 100)
        elif self.stance == "oppose":
            score = int((1 - self.confidence) * 100)
        else:  # neutral
            score = 50
        
        return AgentResult(
            agent_name=self.agent,
            score=max(0, min(100, score)),
            rationale=self.reasoning,
        )


def get_agent_metrics(
    previous_messages: list["AgentMessage"] | None,
    agent_name: str,
) -> dict | None:
    """
    Önceki mesajlardan belirli bir agent'ın metriklerini al.
    Birden fazla mesaj varsa en son turunkini döndürür.
    """
    if not previous_messages:
        return None
    agent_msgs = [m for m in previous_messages if m.agent == agent_name]
    if not agent_msgs:
        return None
    latest = max(agent_msgs, key=lambda m: m.round_number)
    return latest.metrics


def get_agent_stance(
    previous_messages: list["AgentMessage"] | None,
    agent_name: str,
) -> tuple[Stance, float] | None:
    """
    Önceki mesajlardan belirli bir agent'ın stance ve confidence'ını al.
    """
    if not previous_messages:
        return None
    agent_msgs = [m for m in previous_messages if m.agent == agent_name]
    if not agent_msgs:
        return None
    latest = max(agent_msgs, key=lambda m: m.round_number)
    return (latest.stance, latest.confidence)


@dataclass(frozen=True)
class AggregatedDecision:
    final_score: float
    decision: FinalDecision
