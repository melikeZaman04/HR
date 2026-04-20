from app.domain.agents.hr_agent import HRAgent
from app.domain.models import AgentMessage, ScenarioInput


def test_hr_scores_high_when_ready_team_low_hiring_load() -> None:
    """High team readiness with low hiring needs should yield support stance."""
    agent = HRAgent()
    scenario = ScenarioInput(
        name="Enablement",
        description="Upskilling initiative",
        budget_million_usd=2.0,  # low budget → low hiring_needed
        expected_roi_percent=10.0,
        risk_level=2,  # low risk → low hiring_needed
        team_readiness=9,  # high readiness
    )

    # JIRA-02: Test _build_reasoning_prompt
    prompt_desc = agent._build_reasoning_prompt(scenario)
    assert isinstance(prompt_desc, str)
    assert "HR Metni" in prompt_desc
    assert "Ekip kapasitesi" in prompt_desc

    result = agent.analyze(scenario)

    assert isinstance(result, AgentMessage)
    assert result.agent == "HR"
    # High readiness + low hiring should yield support or neutral
    assert result.stance in ("support", "neutral")
    assert "team" in result.reasoning.lower() or "HR" in result.reasoning
    # Legacy score should be reasonable
    legacy = result.to_legacy_result()
    assert legacy.score >= 40


def test_hr_scores_near_zero_when_low_readiness_high_hiring() -> None:
    """Low team readiness with high hiring needs should yield oppose or neutral."""
    agent = HRAgent()
    scenario = ScenarioInput(
        name="Disruptive Change",
        description="Org restructure",
        budget_million_usd=8.0,  # high budget → high hiring_needed
        expected_roi_percent=12.0,
        risk_level=9,  # high risk → high hiring_needed
        team_readiness=2,  # low readiness
    )

    result = agent.analyze(scenario)

    assert result.agent == "HR"
    # Low readiness + high hiring should not yield strong support
    assert result.stance in ("oppose", "neutral")
    # Legacy score should be lower
    legacy = result.to_legacy_result()
    assert legacy.score < 70


def test_hr_score_always_within_bounds() -> None:
    """HR confidence must always be between 0 and 1, legacy score 0-100."""
    agent = HRAgent()
    
    # Extreme high readiness, minimal hiring
    extreme_ready = ScenarioInput(
        name="Perfect Team",
        description="Expert force",
        budget_million_usd=0.5,
        expected_roi_percent=50.0,
        risk_level=1,
        team_readiness=10,
    )
    result_ready = agent.analyze(extreme_ready)
    assert 0.0 <= result_ready.confidence <= 1.0
    legacy_ready = result_ready.to_legacy_result()
    assert 0 <= legacy_ready.score <= 100
    assert legacy_ready.score > 40  # Should be decent

    # Extreme low readiness, massive hiring
    extreme_unready = ScenarioInput(
        name="Massive Ramp",
        description="Scale from zero",
        budget_million_usd=20.0,
        expected_roi_percent=5.0,
        risk_level=10,
        team_readiness=1,
    )
    result_unready = agent.analyze(extreme_unready)
    assert 0.0 <= result_unready.confidence <= 1.0
    assert result_unready.stance in ("oppose", "neutral")
    legacy_unready = result_unready.to_legacy_result()
    assert 0 <= legacy_unready.score <= 100
