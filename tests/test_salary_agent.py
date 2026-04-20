from app.domain.agents.cfo_agent import CFOAgent
from app.domain.models import AgentMessage, ScenarioInput


def test_cfo_scores_high_for_strong_roi_with_low_risk() -> None:
    """High ROI scenario with low risk should yield support stance."""
    agent = CFOAgent()
    scenario = ScenarioInput(
        name="Expansion",
        description="Market expansion",
        budget_million_usd=10.0,
        expected_roi_percent=100.0,  # 100% ROI
        risk_level=2,  # low risk (0.2 risk_factor)
        team_readiness=7,
    )

    # JIRA-02: Test _build_reasoning_prompt
    prompt_desc = agent._build_reasoning_prompt(scenario)
    assert isinstance(prompt_desc, str)
    assert "CFO Metni" in prompt_desc
    assert "Finansal sürdürülebilirlik" in prompt_desc

    result = agent.analyze(scenario)

    assert isinstance(result, AgentMessage)
    assert result.agent == "CFO"
    # High ROI + low risk should yield support stance
    assert result.stance == "support"
    assert result.confidence > 0.6
    assert "ROI" in result.reasoning or "roi" in result.reasoning.lower()
    # Verify legacy conversion
    legacy = result.to_legacy_result()
    assert legacy.score > 60
    assert legacy.score <= 100


def test_cfo_scores_near_zero_for_negative_roi() -> None:
    """Negative ROI scenario should yield oppose stance."""
    agent = CFOAgent()
    scenario = ScenarioInput(
        name="Failed Investment",
        description="Loss-making project",
        budget_million_usd=10.0,
        expected_roi_percent=-50.0,  # -50% ROI (loss)
        risk_level=5,
        team_readiness=6,
    )

    result = agent.analyze(scenario)

    assert result.agent == "CFO"
    # Negative ROI should yield oppose stance
    assert result.stance == "oppose"
    # Legacy score should be very low
    legacy = result.to_legacy_result()
    assert legacy.score < 30


def test_cfo_score_always_within_bounds() -> None:
    """CFO confidence must always be between 0 and 1, legacy score 0-100."""
    agent = CFOAgent()
    
    # Extreme high ROI scenario
    extreme_high = ScenarioInput(
        name="Moon Shot",
        description="Unrealistic gains",
        budget_million_usd=1.0,
        expected_roi_percent=10000.0,  # 10000% ROI
        risk_level=1,  # very low risk
        team_readiness=10,
    )
    result_high = agent.analyze(extreme_high)
    assert 0.0 <= result_high.confidence <= 1.0
    assert result_high.stance == "support"
    legacy_high = result_high.to_legacy_result()
    assert 0 <= legacy_high.score <= 100

    # Extreme high risk scenario
    extreme_risk = ScenarioInput(
        name="Risky Bet",
        description="Maximum risk",
        budget_million_usd=10.0,
        expected_roi_percent=200.0,  # 200% ROI
        risk_level=10,  # maximum risk (1.0 risk_factor, zero penalty)
        team_readiness=3,
    )
    result_risk = agent.analyze(extreme_risk)
    assert 0.0 <= result_risk.confidence <= 1.0
    # High risk should temper the stance
    assert result_risk.stance in ("neutral", "oppose")
    legacy_risk = result_risk.to_legacy_result()
    assert 0 <= legacy_risk.score <= 100
