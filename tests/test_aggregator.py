from app.domain.models import AgentResult, FinalDecision
from app.domain.services.aggregator import DecisionAggregator


def test_aggregator_returns_approve_for_high_average() -> None:
    aggregator = DecisionAggregator()
    result = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=90, rationale=""),
            AgentResult(agent_name="CFO", score=85, rationale=""),
            AgentResult(agent_name="HR", score=80, rationale=""),
        ]
    )

    assert result.final_score == 85.0
    assert result.decision == FinalDecision.APPROVE


def test_aggregator_returns_revise_for_mid_average() -> None:
    aggregator = DecisionAggregator()
    result = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=60, rationale=""),
            AgentResult(agent_name="CFO", score=50, rationale=""),
            AgentResult(agent_name="HR", score=55, rationale=""),
        ]
    )

    assert result.final_score == 55.0
    assert result.decision == FinalDecision.REVISE


def test_aggregator_returns_reject_for_low_average() -> None:
    aggregator = DecisionAggregator()
    result = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=30, rationale=""),
            AgentResult(agent_name="CFO", score=40, rationale=""),
            AgentResult(agent_name="HR", score=35, rationale=""),
        ]
    )

    assert result.final_score == 35.0
    assert result.decision == FinalDecision.REJECT


def test_aggregator_boundary_approve_threshold() -> None:
    """Test boundary at 75: score=74.99 should be REVISE, score=75 should be APPROVE."""
    aggregator = DecisionAggregator()
    
    # Average of ~74.99 should be REVISE
    result_below = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=74, rationale=""),
            AgentResult(agent_name="CFO", score=75, rationale=""),
            AgentResult(agent_name="HR", score=75, rationale=""),
        ]
    )
    # (74 + 75 + 75) / 3 = 74.67
    assert result_below.final_score == 74.67
    assert result_below.decision == FinalDecision.REVISE
    
    # Average of 75 should be APPROVE
    result_at = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=75, rationale=""),
            AgentResult(agent_name="CFO", score=75, rationale=""),
            AgentResult(agent_name="HR", score=75, rationale=""),
        ]
    )
    assert result_at.final_score == 75.0
    assert result_at.decision == FinalDecision.APPROVE


def test_aggregator_boundary_revise_threshold() -> None:
    """Test boundary at 50: score=49.99 should be REJECT, score=50 should be REVISE."""
    aggregator = DecisionAggregator()
    
    # Average of ~49.67 should be REJECT
    result_below = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=49, rationale=""),
            AgentResult(agent_name="CFO", score=50, rationale=""),
            AgentResult(agent_name="HR", score=50, rationale=""),
        ]
    )
    # (49 + 50 + 50) / 3 = 49.67
    assert result_below.final_score == 49.67
    assert result_below.decision == FinalDecision.REJECT
    
    # Average of 50 should be REVISE
    result_at = aggregator.aggregate(
        [
            AgentResult(agent_name="CEO", score=50, rationale=""),
            AgentResult(agent_name="CFO", score=50, rationale=""),
            AgentResult(agent_name="HR", score=50, rationale=""),
        ]
    )
    assert result_at.final_score == 50.0
    assert result_at.decision == FinalDecision.REVISE
