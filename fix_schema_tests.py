import os

content = '''import pytest
from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.culture_agent import CultureAgent
from app.domain.agents.salary_agent import SalaryAgent
from app.domain.models import AgentMessage, ScenarioInput

@pytest.fixture
def sample_scenario() -> ScenarioInput:
    return ScenarioInput(
        candidate_name="Ahmet Yýlmaz",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=85,
        avg_months_per_job=18,
        glassdoor_score=4.2,
        expected_salary=90000,
    )

class TestStrategyAgentMessageSchema:
    def test_strategy_metrics_keys(self, sample_scenario):
        agent = StrategyAgent()
        msg = agent.analyze(sample_scenario)
        assert "tech_score_fit" in msg.metrics or "tech_alignment" in msg.metrics

class TestSalaryAgentMessageSchema:
    def test_salary_metrics_keys(self, sample_scenario):
        agent = SalaryAgent()
        msg = agent.analyze(sample_scenario)
        assert "budget_fit" in msg.metrics
        assert "market_alignment" in msg.metrics

class TestCultureAgentMessageSchema:
    def test_culture_metrics_keys(self, sample_scenario):
        agent = CultureAgent()
        msg = agent.analyze(sample_scenario)
        assert "churn_risk" in msg.metrics or "retention_probability" in msg.metrics
'''

with open('tests/test_agent_message_schema.py', 'w', encoding='utf-8') as f:
    f.write(content)
