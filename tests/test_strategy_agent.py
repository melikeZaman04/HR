from app.domain.agents.ceo_agent import CEOAgent
from app.domain.models import AgentMessage, ScenarioInput


def test_ceo_scores_high_for_strong_strategic_fit_low_market_risk() -> None:
    """High ROI with low market risk should yield high confidence support."""
    agent = CEOAgent()
    scenario = ScenarioInput(
        name="Strategic Expansion",
        description="Market opportunity",
        budget_million_usd=5.0,
        expected_roi_percent=80.0,  # high strategic fit (0.8)
        risk_level=2,  # low market risk (0.2)
        team_readiness=7,
    )

    # JIRA-02: Test _build_reasoning_prompt
    prompt_desc = agent._build_reasoning_prompt(scenario)
    assert isinstance(prompt_desc, str)
    assert "CEO Metni" in prompt_desc
    assert "Stratejik büyüme ve pazar uyumu odaklı analiz" in prompt_desc

    result = agent.analyze(scenario)

    assert isinstance(result, AgentMessage)
    assert result.agent == "CEO"
    # High strategic fit + low risk should yield support stance
    assert result.stance == "support"
    assert result.confidence > 0.6
    assert "strategic" in result.reasoning.lower() or "Strategic" in result.reasoning
    # Verify legacy conversion works
    legacy = result.to_legacy_result()
    assert legacy.score > 60
    assert legacy.score <= 100


def test_ceo_scores_low_for_poor_strategic_fit_high_market_risk() -> None:
    """Low ROI with high market risk should yield oppose or neutral stance."""
    agent = CEOAgent()
    scenario = ScenarioInput(
        name="Risky Bet",
        description="Uncertain market",
        budget_million_usd=10.0,
        expected_roi_percent=5.0,  # low strategic fit (0.05)
        risk_level=9,  # high market risk (0.9)
        team_readiness=5,
    )

    result = agent.analyze(scenario)

    assert result.agent == "CEO"
    # Low strategic fit + high risk should not yield support
    assert result.stance in ("oppose", "neutral")
    # Legacy score should be low
    legacy = result.to_legacy_result()
    assert legacy.score < 60


def test_ceo_score_always_within_bounds() -> None:
    """CEO confidence must always be between 0 and 1, legacy score 0-100."""
    agent = CEOAgent()
    
    # Extreme high strategic fit, zero market risk
    extreme_high = ScenarioInput(
        name="Perfect Play",
        description="Guaranteed winner",
        budget_million_usd=1.0,
        expected_roi_percent=500.0,  # 5x ROI, clamped to strategic_fit=1.0
        risk_level=1,  # minimal risk (0.1)
        team_readiness=10,
    )
    result_high = agent.analyze(extreme_high)
    assert 0.0 <= result_high.confidence <= 1.0
    assert result_high.stance == "support"
    legacy_high = result_high.to_legacy_result()
    assert 0 <= legacy_high.score <= 100
    assert legacy_high.score > 70  # Should be very high

    # Extreme low strategic fit, maximum market risk
    extreme_risk = ScenarioInput(
        name="Dubious Venture",
        description="Highly uncertain",
        budget_million_usd=20.0,
        expected_roi_percent=-30.0,  # negative ROI → strategic_fit=0
        risk_level=10,  # maximum risk (1.0)
        team_readiness=3,
    )
    result_risk = agent.analyze(extreme_risk)
    assert 0.0 <= result_risk.confidence <= 1.0
    assert result_risk.stance in ("oppose", "neutral")
    legacy_risk = result_risk.to_legacy_result()
    assert 0 <= legacy_risk.score <= 100
