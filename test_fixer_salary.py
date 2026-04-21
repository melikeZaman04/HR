import os

content = '''from app.domain.agents.salary_agent import SalaryAgent
from app.domain.models import AgentMessage, ScenarioInput

def test_salary_supports_within_budget() -> None:
    agent = SalaryAgent()
    scenario = ScenarioInput(
        candidate_name="Cheap Coder",
        applied_role="Backend Developer",
        experience_years=3,
        tech_test_score=80,
        avg_months_per_job=24,
        glassdoor_score=4.0,
        expected_salary=60000
    )
    result = agent.analyze(scenario)
    assert isinstance(result, AgentMessage)
    assert result.stance == "support"
    assert result.metrics["budget_fit"] > 5

def test_salary_opposes_over_budget() -> None:
    agent = SalaryAgent()
    scenario = ScenarioInput(
        candidate_name="Expensive Coder",
        applied_role="Backend Developer",
        experience_years=3,
        tech_test_score=80,
        avg_months_per_job=24,
        glassdoor_score=4.0,
        expected_salary=200000
    )
    result = agent.analyze(scenario)
    assert result.stance == "oppose"
    assert result.metrics["budget_fit"] < 5
'''

with open('tests/test_salary_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
