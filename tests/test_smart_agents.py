import pytest
from app.domain.models import AgentMessage, ScenarioInput, get_agent_metrics, get_agent_stance
from app.domain.agents.ceo_agent import CEOAgent
from app.domain.agents.cfo_agent import CFOAgent
from app.domain.agents.hr_agent import HRAgent

@pytest.fixture
def high_budget_scenario():
    return ScenarioInput(
        name="Big Project",
        description="High budget expansion",
        budget_million_usd=15.0,
        expected_roi_percent=45.0,
        risk_level=7,
        team_readiness=4
    )

@pytest.fixture
def small_budget_scenario():
    return ScenarioInput(
        name="Small Project",
        description="Small optimization",
        budget_million_usd=1.0,
        expected_roi_percent=45.0,
        risk_level=7, 
        team_readiness=8
    )

def test_round_number_tracking(small_budget_scenario):
    ceo = CEOAgent()
    
    # Round 1
    msg1 = ceo.analyze(small_budget_scenario, previous_messages=None)
    assert msg1.round_number == 1
    
    # Round 2
    msg2 = ceo.analyze(small_budget_scenario, previous_messages=[msg1])
    assert msg2.round_number == 2

def test_cross_metric_reading():
    previous_messages = [
        AgentMessage(
            agent="CFO", 
            stance="oppose", 
            confidence=0.9, 
            reasoning="Too risky",
            metrics={"risk_score": 8.5},
            round_number=1
        ),
        AgentMessage(
            agent="HR",
            stance="support",
            confidence=0.6,
            reasoning="We can hire",
            metrics={"talent_availability": 7.0},
            round_number=1
        )
    ]
    
    cfo_metrics = get_agent_metrics(previous_messages, "CFO")
    assert cfo_metrics["risk_score"] == 8.5
    
    hr_stance = get_agent_stance(previous_messages, "HR")
    assert hr_stance == ("support", 0.6)

def test_two_round_debate(high_budget_scenario):
    """
    Simulate a 2-round debate where agents influence each other.
    """
    ceo = CEOAgent()
    cfo = CFOAgent()
    hr = HRAgent()
    
    # --- ROUND 1 ---
    ceo_msg1 = ceo.analyze(high_budget_scenario)
    cfo_msg1 = cfo.analyze(high_budget_scenario)
    hr_msg1 = hr.analyze(high_budget_scenario)
    
    round1_msgs = [ceo_msg1, cfo_msg1, hr_msg1]
    
    # Verify Round 1 basics
    assert all(m.round_number == 1 for m in round1_msgs)
    # CFO likely opposes due to high risk (7) and large budget tier
    assert cfo_msg1.metrics["risk_score"] == 7.0
    
    # --- ROUND 2 ---
    ceo_msg2 = ceo.analyze(high_budget_scenario, round1_msgs)
    cfo_msg2 = cfo.analyze(high_budget_scenario, round1_msgs)
    
    # Verify reaction in Round 2
    assert ceo_msg2.round_number == 2
    assert cfo_msg2.round_number == 2
    
    # Check if ANY agent changed their confidence or stance, or added cross-analysis notes
    changed_confidence = (
        ceo_msg2.confidence != ceo_msg1.confidence or
        cfo_msg2.confidence != cfo_msg1.confidence
    )
    
    cross_analysis_in_reasoning = (
        "Çapraz analiz" in ceo_msg2.reasoning or
        "Çapraz analiz" in cfo_msg2.reasoning
    )
    
    assert changed_confidence or cross_analysis_in_reasoning, "Agents should react to each other in Round 2"

def test_stance_shift():
    """
    Test if CEO shifts to neutral when facing opposition, even if initially supportive.
    """
    scenario = ScenarioInput(
        name="Risky Growth",
        description="...",
        budget_million_usd=5.0,
        expected_roi_percent=80.0, # High ROI -> CEO support initially
        risk_level=4, # Lowish risk -> CEO support
        team_readiness=8
    )
    
    ceo = CEOAgent()
    msg1 = ceo.analyze(scenario)
    assert msg1.stance == "support"
    
    # Inject opposition
    opposition_msgs = [
        msg1,
        AgentMessage("CFO", "oppose", 0.9, "No money", {}, 1),
        AgentMessage("HR", "oppose", 0.9, "No people", {}, 1)
    ]
    
    msg2 = ceo.analyze(scenario, opposition_msgs)
    
    # Should shift to neutral due to team opposition
    assert msg2.stance == "neutral"
    assert "NÖTR" in msg2.reasoning or "neutral" in msg2.reasoning.lower()

def test_dynamic_thresholds():
    """
    Compare CFO reaction to same ROI/Risk but different budget sizes.
    """
    common_roi = 25.0 # Moderate ROI
    common_risk = 5   # Moderate Risk
    
    # Small project: budget 1M creates Small Tier -> adjusted ROI might pass lower threshold
    small = ScenarioInput("S", "d", 1.0, common_roi, common_risk, 5)
    
    # Large project: budget 20M creates Large Tier -> same adjusted ROI might fail higher threshold
    large = ScenarioInput("L", "d", 20.0, common_roi, common_risk, 5)
    
    cfo = CFOAgent()
    
    msg_small = cfo.analyze(small)
    msg_large = cfo.analyze(large)
    
    # In 'small' tier, support threshold is 0.20. Adjusted ROI = 0.25 * (1-0.5) = 0.125 -> Neutral/Oppose
    # Wait, risk factor is risk_level / 10 = 0.5. Risk penalty = 0.5.
    # Adjusted ROI = 0.25 * 0.5 = 0.125.
    
    # Let's use parameters where it makes a difference.
    # Small threshold: 0.20, Medium: 0.30, Large: 0.35.
    # We need adjusted ROI to be between e.g. 0.25 and 0.30?
    
    # If ROI=60%, Risk=2 (0.2). Adjusted = 0.60 * 0.8 = 0.48. Supports all.
    # If ROI=40%, Risk=4 (0.4). Adjusted = 0.40 * 0.6 = 0.24.
    # Small (thresh 0.20): Support.
    # Large (thresh 0.35): Neutral/Oppose.
    
    s_test = ScenarioInput("S", "d", 1.0, 40.0, 4, 8)
    l_test = ScenarioInput("L", "d", 20.0, 40.0, 4, 8)
    
    m_s = cfo.analyze(s_test)
    m_l = cfo.analyze(l_test)
    
    # m_s should be support (0.24 >= 0.20)
    # m_l should be neutral or oppose (0.24 < 0.35)
    
    assert m_s.stance == "support"
    assert m_l.stance != "support"

def test_backward_compatibility():
    """Ensure older code that doesn't know about round_number still works."""
    msg = AgentMessage("CEO", "support", 0.8, "Reasoning")
    assert msg.round_number == 1
    
    legacy_res = msg.to_legacy_result()
    assert legacy_res.score == 80
