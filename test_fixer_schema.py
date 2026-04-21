import os

schema_test_content = '''"""
Test suite for AgentMessage schema validation.
Ensures all agents produce messages conforming to the standardized protocol.
"""

import pytest

from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.salary_agent import SalaryAgent
from app.domain.agents.culture_agent import CultureAgent
from app.domain.models import AgentMessage, ScenarioInput

@pytest.fixture
def sample_scenario() -> ScenarioInput:
    """Standard test Candidate scenario with moderate values."""
    return ScenarioInput(
        candidate_name="Ahmet Yılmaz",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=85,
        avg_months_per_job=18,
        glassdoor_score=4.2,
        expected_salary=90000,
    )

class TestStrategyAgentMessageSchema:
    def test_message_structure(self, sample_scenario: ScenarioInput) -> None:
        agent = StrategyAgent()
        result = agent.analyze(sample_scenario)

        assert isinstance(result, AgentMessage)
        assert result.agent == "Strategy"
        assert result.stance in ("support", "oppose", "neutral")
        assert 0.0 <= result.confidence <= 1.0
        assert "tech_score_fit" in result.metrics
        assert "experience_fit" in result.metrics

class TestSalaryAgentMessageSchema:
    def test_message_structure(self, sample_scenario: ScenarioInput) -> None:
        agent = SalaryAgent()
        result = agent.analyze(sample_scenario)

        assert isinstance(result, AgentMessage)
        assert result.agent == "Salary"
        assert result.stance in ("support", "oppose", "neutral")
        assert 0.0 <= result.confidence <= 1.0
        assert "budget_fit" in result.metrics
        assert "market_alignment" in result.metrics

class TestCultureAgentMessageSchema:
    def test_message_structure(self, sample_scenario: ScenarioInput) -> None:
        agent = CultureAgent()
        result = agent.analyze(sample_scenario)

        assert isinstance(result, AgentMessage)
        assert result.agent == "Culture"
        assert result.stance in ("support", "oppose", "neutral")
        assert 0.0 <= result.confidence <= 1.0
        assert "retention_probability" in result.metrics
        assert "churn_risk" in result.metrics
'''

with open('tests/test_agent_message_schema.py', 'w', encoding='utf-8') as f:
    f.write(schema_test_content)
