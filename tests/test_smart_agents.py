import pytest
from app.domain.models import AgentMessage, ScenarioInput, get_agent_metrics, get_agent_stance
from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.salary_agent import SalaryAgent
from app.domain.agents.culture_agent import CultureAgent

@pytest.fixture
def high_budget_scenario():
    return ScenarioInput(
        candidate_name="Senior Engineer",
        applied_role="Backend Developer",
        experience_years=8,
        tech_test_score=90,
        avg_months_per_job=24,
        glassdoor_score=4.5,
        expected_salary=150000,
    )

@pytest.fixture
def small_budget_scenario():
    return ScenarioInput(
        candidate_name="Junior Engineer",
        applied_role="Backend Developer",
        experience_years=2,
        tech_test_score=75,
        avg_months_per_job=18,
        glassdoor_score=4.0,
        expected_salary=55000,
    )

def test_round_number_tracking(small_budget_scenario):
    strategy = StrategyAgent()

    msg1 = strategy.analyze(small_budget_scenario, previous_messages=None)
    assert msg1.round_number == 1

    msg2 = strategy.analyze(small_budget_scenario, previous_messages=[msg1])
    assert msg2.round_number == 2

def test_cross_metric_reading():
    previous_messages = [
        AgentMessage(
            agent="Salary",
            stance="oppose",
            confidence=0.9,
            reasoning="Too expensive",
            metrics={"budget_fit": 2.0},
            round_number=1
        ),
        AgentMessage(
            agent="Culture",
            stance="support",
            confidence=0.6,
            reasoning="Good cultural fit",
            metrics={"churn_risk": 3.0},
            round_number=1
        )
    ]

    salary_metrics = get_agent_metrics(previous_messages, "Salary")
    assert salary_metrics["budget_fit"] == 2.0

    culture_stance = get_agent_stance(previous_messages, "Culture")
    assert culture_stance == ("support", 0.6)

def test_two_round_debate(high_budget_scenario):
    """Simulate a 2-round debate where agents influence each other."""
    strategy = StrategyAgent()
    salary = SalaryAgent()
    culture = CultureAgent()

    # --- ROUND 1 ---
    strategy_msg1 = strategy.analyze(high_budget_scenario)
    salary_msg1 = salary.analyze(high_budget_scenario)
    culture_msg1 = culture.analyze(high_budget_scenario)

    round1_msgs = [strategy_msg1, salary_msg1, culture_msg1]
    assert all(m.round_number == 1 for m in round1_msgs)
    assert "budget_fit" in salary_msg1.metrics
    assert "market_alignment" in salary_msg1.metrics

    # --- ROUND 2 ---
    strategy_msg2 = strategy.analyze(high_budget_scenario, round1_msgs)
    salary_msg2 = salary.analyze(high_budget_scenario, round1_msgs)

    assert strategy_msg2.round_number == 2
    assert salary_msg2.round_number == 2

    changed_confidence = (
        strategy_msg2.confidence != strategy_msg1.confidence or
        salary_msg2.confidence != salary_msg1.confidence
    )

    cross_analysis_in_reasoning = (
        "Cross analysis" in strategy_msg2.reasoning or
        "Cross analysis" in salary_msg2.reasoning or
        "confidence" in strategy_msg2.reasoning.lower()
    )

    assert changed_confidence or cross_analysis_in_reasoning

def test_stance_shift():
    """Strategy confidence should reduce when both other agents oppose."""
    scenario = ScenarioInput(
        candidate_name="Tech Candidate",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=85,
        avg_months_per_job=24,
        glassdoor_score=4.5,
        expected_salary=80000,
    )

    strategy = StrategyAgent()
    msg1 = strategy.analyze(scenario)
    assert msg1.stance == "support"
    initial_confidence = msg1.confidence

    opposition_msgs = [
        msg1,
        AgentMessage("Salary", "oppose", 0.9, "Too expensive", {}, 1),
        AgentMessage("Culture", "oppose", 0.9, "High churn risk", {}, 1),
    ]

    msg2 = strategy.analyze(scenario, opposition_msgs)
    assert msg2.confidence < initial_confidence

def test_dynamic_thresholds():
    """Low salary expectation should support; very high should oppose."""
    low_salary = ScenarioInput(
        candidate_name="Budget Friendly",
        applied_role="Backend Developer",
        experience_years=3,
        tech_test_score=80,
        avg_months_per_job=24,
        glassdoor_score=4.0,
        expected_salary=60000,
    )

    high_salary = ScenarioInput(
        candidate_name="Expensive Hire",
        applied_role="Backend Developer",
        experience_years=3,
        tech_test_score=80,
        avg_months_per_job=24,
        glassdoor_score=4.0,
        expected_salary=200000,
    )

    salary = SalaryAgent()
    msg_low = salary.analyze(low_salary)
    msg_high = salary.analyze(high_salary)

    assert msg_low.stance == "support"
    assert msg_high.stance == "oppose"

def test_backward_compatibility():
    """Ensure older code that doesn't know about round_number still works."""
    msg = AgentMessage("Strategy", "support", 0.8, "Reasoning")
    assert msg.round_number == 1

    legacy_res = msg.to_legacy_result()
    assert legacy_res.score == 80
