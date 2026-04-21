"""
Test suite for AgentMessage schema validation.

Ensures all agents produce messages conforming to the standardized
communication protocol with correct field types and constraints.
"""

import pytest

from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.salary_agent import SalaryAgent
from app.domain.agents.culture_agent import CultureAgent
from app.domain.models import AgentMessage, ScenarioInput


# ============================================================================
# Test Fixtures
# ============================================================================

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


@pytest.fixture
def high_risk_scenario() -> ScenarioInput:
    """High churn risk candidate scenario."""
    return ScenarioInput(
        candidate_name="Risky Candidate",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=85,
        avg_months_per_job=4,
        glassdoor_score=2.5,
        expected_salary=120000,
    )


@pytest.fixture
def low_risk_scenario() -> ScenarioInput:
    """Stable, conservative candidate scenario."""
    return ScenarioInput(
        candidate_name="Safe Candidate",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=75,
        avg_months_per_job=36,
        glassdoor_score=4.5,
        expected_salary=70000,
    )


# ============================================================================
# AgentMessage Model Validation Tests
# ============================================================================

class TestAgentMessageValidation:
    """Tests for AgentMessage dataclass validation."""
    
    def test_valid_support_stance(self):
        """Support stance with valid confidence should succeed."""
        msg = AgentMessage(
            agent="TEST",
            stance="support",
            confidence=0.8,
            reasoning="Test reasoning",
            metrics={"test_metric": 5},
        )
        assert msg.stance == "support"
        assert msg.confidence == 0.8
    
    def test_valid_oppose_stance(self):
        """Oppose stance with valid confidence should succeed."""
        msg = AgentMessage(
            agent="TEST",
            stance="oppose",
            confidence=0.6,
            reasoning="Test reasoning",
            metrics={},
        )
        assert msg.stance == "oppose"
    
    def test_valid_neutral_stance(self):
        """Neutral stance with valid confidence should succeed."""
        msg = AgentMessage(
            agent="TEST",
            stance="neutral",
            confidence=0.5,
            reasoning="Test reasoning",
        )
        assert msg.stance == "neutral"
    
    def test_invalid_stance_raises_error(self):
        """Invalid stance value should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid stance"):
            AgentMessage(
                agent="TEST",
                stance="invalid",  # type: ignore
                confidence=0.5,
                reasoning="Test",
            )
    
    def test_confidence_below_zero_raises_error(self):
        """Confidence below 0.0 should raise ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            AgentMessage(
                agent="TEST",
                stance="support",
                confidence=-0.1,
                reasoning="Test",
            )
    
    def test_confidence_above_one_raises_error(self):
        """Confidence above 1.0 should raise ValueError."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            AgentMessage(
                agent="TEST",
                stance="support",
                confidence=1.5,
                reasoning="Test",
            )
    
    def test_confidence_boundary_zero(self):
        """Confidence of exactly 0.0 should be valid."""
        msg = AgentMessage(
            agent="TEST",
            stance="oppose",
            confidence=0.0,
            reasoning="Test",
        )
        assert msg.confidence == 0.0
    
    def test_confidence_boundary_one(self):
        """Confidence of exactly 1.0 should be valid."""
        msg = AgentMessage(
            agent="TEST",
            stance="support",
            confidence=1.0,
            reasoning="Test",
        )
        assert msg.confidence == 1.0


class TestAgentMessageLegacyConversion:
    """Tests for AgentMessage.to_legacy_result() conversion."""
    
    def test_support_high_confidence_yields_high_score(self):
        """Support with high confidence should produce high score."""
        msg = AgentMessage(
            agent="TEST",
            stance="support",
            confidence=0.9,
            reasoning="Strong support",
        )
        result = msg.to_legacy_result()
        assert result.agent_name == "TEST"
        assert result.score == 90  # 0.9 * 100
        assert result.rationale == "Strong support"
    
    def test_oppose_high_confidence_yields_low_score(self):
        """Oppose with high confidence should produce low score."""
        msg = AgentMessage(
            agent="TEST",
            stance="oppose",
            confidence=0.9,
            reasoning="Strong opposition",
        )
        result = msg.to_legacy_result()
        # (1 - 0.9) * 100 = 10, but int conversion may give 9 or 10 due to float precision
        assert result.score <= 10
    
    def test_neutral_yields_middle_score(self):
        """Neutral stance should produce score of 50."""
        msg = AgentMessage(
            agent="TEST",
            stance="neutral",
            confidence=0.7,
            reasoning="Undecided",
        )
        result = msg.to_legacy_result()
        assert result.score == 50


# ============================================================================
# Strategy Agent Schema Tests
# ============================================================================

class TestStrategyAgentMessageSchema:
    """Tests for Strategy agent message format compliance."""
    
    def test_ceo_message_has_required_fields(self, sample_scenario):
        """Strategy message should have all required AgentMessage fields."""
        agent = StrategyAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "Strategy"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_ceo_metrics_keys(self, sample_scenario):
        """Strategy metrics should contain expected keys."""
        agent = StrategyAgent()
        msg = agent.analyze(sample_scenario)

        assert "tech_alignment" in msg.metrics
        assert "experience_depth" in msg.metrics

    def test_ceo_metrics_values_in_range(self, sample_scenario):
        """Strategy metric values should be within 0-10 range."""
        agent = StrategyAgent()
        msg = agent.analyze(sample_scenario)

        assert 0 <= msg.metrics["tech_alignment"] <= 10
        assert 0 <= msg.metrics["experience_depth"] <= 10
    
    def test_ceo_with_previous_messages(self, sample_scenario):
        """Strategy should accept and process previous messages."""
        cfo_msg = AgentMessage(
            agent="Salary",
            stance="oppose",
            confidence=0.8,
            reasoning="Financial concerns",
            metrics={"risk_score": 7, "cost_impact": 5.0, "roi_estimate": 10.0},
        )
        
        agent = StrategyAgent()
        msg = agent.analyze(sample_scenario, previous_messages=[cfo_msg])
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "Strategy"


# ============================================================================
# Salary Agent Schema Tests
# ============================================================================

class TestSalaryAgentMessageSchema:
    """Tests for Salary agent message format compliance."""
    
    def test_cfo_message_has_required_fields(self, sample_scenario):
        """Salary message should have all required AgentMessage fields."""
        agent = SalaryAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "Salary"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_cfo_metrics_keys(self, sample_scenario):
        """Salary metrics should contain expected keys."""
        agent = SalaryAgent()
        msg = agent.analyze(sample_scenario)

        assert "budget_fit" in msg.metrics
        assert "market_alignment" in msg.metrics

    def test_cfo_metrics_budget_fit_in_range(self, sample_scenario):
        """Salary budget_fit should be within 0-10 range."""
        agent = SalaryAgent()
        msg = agent.analyze(sample_scenario)

        assert 0 <= msg.metrics["budget_fit"] <= 10

    def test_cfo_metrics_market_alignment_in_range(self, sample_scenario):
        """Salary market_alignment should be within 0-10 range."""
        agent = SalaryAgent()
        msg = agent.analyze(sample_scenario)

        assert 0 <= msg.metrics["market_alignment"] <= 10


# ============================================================================
# Culture Agent Schema Tests
# ============================================================================

class TestCultureAgentMessageSchema:
    """Tests for Culture agent message format compliance."""
    
    def test_hr_message_has_required_fields(self, sample_scenario):
        """Culture message should have all required AgentMessage fields."""
        agent = CultureAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "Culture"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_hr_metrics_keys(self, sample_scenario):
        """Culture metrics should contain expected keys."""
        agent = CultureAgent()
        msg = agent.analyze(sample_scenario)

        assert "churn_risk" in msg.metrics
        assert "cultural_fit" in msg.metrics

    def test_hr_metrics_values_in_range(self, sample_scenario):
        """Culture metric values should be within 0-10 range."""
        agent = CultureAgent()
        msg = agent.analyze(sample_scenario)

        assert 0 <= msg.metrics["churn_risk"] <= 10
        assert 0 <= msg.metrics["cultural_fit"] <= 10


# ============================================================================
# Cross-Agent Integration Tests
# ============================================================================

class TestAgentInteraction:
    """Tests for agent interaction via previous_messages."""
    
    def test_sequential_agent_execution(self, sample_scenario):
        """Agents should be able to run sequentially with message passing."""
        ceo = StrategyAgent()
        cfo = SalaryAgent()
        hr = CultureAgent()
        
        # Strategy analyzes first (no previous messages)
        ceo_msg = ceo.analyze(sample_scenario)
        assert ceo_msg.agent == "Strategy"
        
        # Salary sees Strategy's message
        cfo_msg = cfo.analyze(sample_scenario, previous_messages=[ceo_msg])
        assert cfo_msg.agent == "Salary"
        
        # Culture sees both Strategy and Salary messages
        hr_msg = hr.analyze(sample_scenario, previous_messages=[ceo_msg, cfo_msg])
        assert hr_msg.agent == "Culture"
    
    def test_all_agents_produce_valid_legacy_results(self, sample_scenario):
        """All agent messages should convert to valid legacy results."""
        agents = [StrategyAgent(), SalaryAgent(), CultureAgent()]
        messages = []
        
        for agent in agents:
            msg = agent.analyze(sample_scenario, previous_messages=messages or None)
            messages.append(msg)
            
            # Verify legacy conversion works
            legacy = msg.to_legacy_result()
            assert 0 <= legacy.score <= 100
            assert isinstance(legacy.rationale, str)
    
    def test_edge_case_high_risk_scenario(self, high_risk_scenario):
        """Agents should handle extreme high-risk scenarios."""
        ceo = StrategyAgent()
        cfo = SalaryAgent()
        hr = CultureAgent()
        
        ceo_msg = ceo.analyze(high_risk_scenario)
        cfo_msg = cfo.analyze(high_risk_scenario, [ceo_msg])
        hr_msg = hr.analyze(high_risk_scenario, [ceo_msg, cfo_msg])
        
        # All messages should be valid
        for msg in [ceo_msg, cfo_msg, hr_msg]:
            assert 0.0 <= msg.confidence <= 1.0
            assert msg.stance in ("support", "oppose", "neutral")
    
    def test_edge_case_low_risk_scenario(self, low_risk_scenario):
        """Agents should handle conservative low-risk scenarios."""
        ceo = StrategyAgent()
        cfo = SalaryAgent()
        hr = CultureAgent()
        
        ceo_msg = ceo.analyze(low_risk_scenario)
        cfo_msg = cfo.analyze(low_risk_scenario, [ceo_msg])
        hr_msg = hr.analyze(low_risk_scenario, [ceo_msg, cfo_msg])
        
        # All messages should be valid
        for msg in [ceo_msg, cfo_msg, hr_msg]:
            assert 0.0 <= msg.confidence <= 1.0
            assert msg.stance in ("support", "oppose", "neutral")
