import os

content = '''from app.domain.agents.culture_agent import CultureAgent
from app.domain.models import AgentMessage, ScenarioInput

def test_culture_supports_long_tenure() -> None:
    agent = CultureAgent()
    scenario = ScenarioInput(
        candidate_name="Loyal Employee",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=80,
        avg_months_per_job=36,
        glassdoor_score=4.5,
        expected_salary=80000
    )
    result = agent.analyze(scenario)
    assert isinstance(result, AgentMessage)
    assert result.stance == "support"
    assert result.metrics["churn_risk"] < 3

def test_culture_opposes_job_hopper() -> None:
    agent = CultureAgent()
    scenario = ScenarioInput(
        candidate_name="Job Hopper",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=80,
        avg_months_per_job=4,
        glassdoor_score=4.0,
        expected_salary=80000
    )
    result = agent.analyze(scenario)
    assert isinstance(result, AgentMessage)
    assert result.stance == "oppose"
    assert result.metrics["churn_risk"] > 5
'''

with open('tests/test_culture_agent.py', 'w', encoding='utf-8') as f:
    f.write(content)
