import os

content = '''from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.models import AgentMessage, ScenarioInput

def test_strategy_scores_high_for_strong_tech_score() -> None:
    agent = StrategyAgent()
    scenario = ScenarioInput(
        candidate_name="Genius Coder",
        applied_role="Backend Developer",
        experience_years=8,
        tech_test_score=95,
        avg_months_per_job=24,
        glassdoor_score=4.5,
        expected_salary=80000
    )

    result = agent.analyze(scenario)

    assert isinstance(result, AgentMessage)
    assert result.stance == "support"
    assert result.metrics["tech_score_fit"] > 8

def test_strategy_opposes_low_tech_score() -> None:
    agent = StrategyAgent()
    scenario = ScenarioInput(
        candidate_name="Junior Coder",
        applied_role="Backend Developer",
        experience_years=2,
        tech_test_score=40,
        avg_months_per_job=12,
        glassdoor_score=4.0,
        expected_salary=40000
    )

    result = agent.analyze(scenario)

    assert isinstance(result, AgentMessage)
    assert result.stance == "oppose"
    assert result.confidence > 0.5
'''

with open('tests/test_strategy_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
