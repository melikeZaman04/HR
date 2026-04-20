"""
Test suite for AgentMessage schema validation.

Ensures all agents produce messages conforming to the standardized
communication protocol with correct field types and constraints.
"""

import pytest

from app.domain.agents.ceo_agent import CEOAgent
from app.domain.agents.cfo_agent import CFOAgent
from app.domain.agents.hr_agent import HRAgent
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
    """High-risk, high-reward scenario."""
    return ScenarioInput(
        name="Risky Venture",
        description="High risk scenario for edge case testing",
        budget_million_usd=20.0,
        expected_roi_percent=80.0,
        risk_level=9,
        team_readiness=3,
    )


@pytest.fixture
def low_risk_scenario() -> ScenarioInput:
    """Conservative low-risk scenario."""
    return ScenarioInput(
        name="Safe Bet",
        description="Low risk scenario for edge case testing",
        budget_million_usd=2.0,
        expected_roi_percent=15.0,
        risk_level=2,
        team_readiness=9,
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
# CEO Agent Schema Tests
# ============================================================================

class TestCEOAgentMessageSchema:
    """Tests for CEO agent message format compliance."""
    
    def test_ceo_message_has_required_fields(self, sample_scenario):
        """CEO message should have all required AgentMessage fields."""
        agent = CEOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "CEO"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_ceo_metrics_keys(self, sample_scenario):
        """CEO metrics should contain expected keys."""
        agent = CEOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert "growth_potential" in msg.metrics
        assert "market_alignment" in msg.metrics
    
    def test_ceo_metrics_values_in_range(self, sample_scenario):
        """CEO metric values should be within 0-10 range."""
        agent = CEOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert 0 <= msg.metrics["growth_potential"] <= 10
        assert 0 <= msg.metrics["market_alignment"] <= 10
    
    def test_ceo_with_previous_messages(self, sample_scenario):
        """CEO should accept and process previous messages."""
        cfo_msg = AgentMessage(
            agent="CFO",
            stance="oppose",
            confidence=0.8,
            reasoning="Financial concerns",
            metrics={"risk_score": 7, "cost_impact": 5.0, "roi_estimate": 10.0},
        )
        
        agent = CEOAgent()
        msg = agent.analyze(sample_scenario, previous_messages=[cfo_msg])
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "CEO"


# ============================================================================
# CFO Agent Schema Tests
# ============================================================================

class TestCFOAgentMessageSchema:
    """Tests for CFO agent message format compliance."""
    
    def test_cfo_message_has_required_fields(self, sample_scenario):
        """CFO message should have all required AgentMessage fields."""
        agent = CFOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "CFO"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_cfo_metrics_keys(self, sample_scenario):
        """CFO metrics should contain expected keys."""
        agent = CFOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert "risk_score" in msg.metrics
        assert "cost_impact" in msg.metrics
        assert "roi_estimate" in msg.metrics
    
    def test_cfo_metrics_risk_score_in_range(self, sample_scenario):
        """CFO risk_score should be within 0-10 range."""
        agent = CFOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert 0 <= msg.metrics["risk_score"] <= 10
    
    def test_cfo_metrics_cost_impact_is_positive(self, sample_scenario):
        """CFO cost_impact should be non-negative."""
        agent = CFOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert msg.metrics["cost_impact"] >= 0
    
    def test_cfo_metrics_roi_estimate_is_float(self, sample_scenario):
        """CFO roi_estimate should be a float representing percentage."""
        agent = CFOAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg.metrics["roi_estimate"], float)


# ============================================================================
# HR Agent Schema Tests
# ============================================================================

class TestHRAgentMessageSchema:
    """Tests for HR agent message format compliance."""
    
    def test_hr_message_has_required_fields(self, sample_scenario):
        """HR message should have all required AgentMessage fields."""
        agent = HRAgent()
        msg = agent.analyze(sample_scenario)
        
        assert isinstance(msg, AgentMessage)
        assert msg.agent == "HR"
        assert msg.stance in ("support", "oppose", "neutral")
        assert isinstance(msg.confidence, float)
        assert 0.0 <= msg.confidence <= 1.0
        assert isinstance(msg.reasoning, str)
        assert len(msg.reasoning) > 0
        assert isinstance(msg.metrics, dict)
    
    def test_hr_metrics_keys(self, sample_scenario):
        """HR metrics should contain expected keys."""
        agent = HRAgent()
        msg = agent.analyze(sample_scenario)
        
        assert "talent_availability" in msg.metrics
        assert "team_impact" in msg.metrics
        assert "workload_score" in msg.metrics
    
    def test_hr_metrics_values_in_range(self, sample_scenario):
        """HR metric values should be within 0-10 range."""
        agent = HRAgent()
        msg = agent.analyze(sample_scenario)
        
        assert 0 <= msg.metrics["talent_availability"] <= 10
        assert 0 <= msg.metrics["team_impact"] <= 10
        assert 0 <= msg.metrics["workload_score"] <= 10


# ============================================================================
# Cross-Agent Integration Tests
# ============================================================================

class TestAgentInteraction:
    """Tests for agent interaction via previous_messages."""
    
    def test_sequential_agent_execution(self, sample_scenario):
        """Agents should be able to run sequentially with message passing."""
        ceo = CEOAgent()
        cfo = CFOAgent()
        hr = HRAgent()
        
        # CEO analyzes first (no previous messages)
        ceo_msg = ceo.analyze(sample_scenario)
        assert ceo_msg.agent == "CEO"
        
        # CFO sees CEO's message
        cfo_msg = cfo.analyze(sample_scenario, previous_messages=[ceo_msg])
        assert cfo_msg.agent == "CFO"
        
        # HR sees both CEO and CFO messages
        hr_msg = hr.analyze(sample_scenario, previous_messages=[ceo_msg, cfo_msg])
        assert hr_msg.agent == "HR"
    
    def test_all_agents_produce_valid_legacy_results(self, sample_scenario):
        """All agent messages should convert to valid legacy results."""
        agents = [CEOAgent(), CFOAgent(), HRAgent()]
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
        ceo = CEOAgent()
        cfo = CFOAgent()
        hr = HRAgent()
        
        ceo_msg = ceo.analyze(high_risk_scenario)
        cfo_msg = cfo.analyze(high_risk_scenario, [ceo_msg])
        hr_msg = hr.analyze(high_risk_scenario, [ceo_msg, cfo_msg])
        
        # All messages should be valid
        for msg in [ceo_msg, cfo_msg, hr_msg]:
            assert 0.0 <= msg.confidence <= 1.0
            assert msg.stance in ("support", "oppose", "neutral")
    
    def test_edge_case_low_risk_scenario(self, low_risk_scenario):
        """Agents should handle conservative low-risk scenarios."""
        ceo = CEOAgent()
        cfo = CFOAgent()
        hr = HRAgent()
        
        ceo_msg = ceo.analyze(low_risk_scenario)
        cfo_msg = cfo.analyze(low_risk_scenario, [ceo_msg])
        hr_msg = hr.analyze(low_risk_scenario, [ceo_msg, cfo_msg])
        
        # All messages should be valid
        for msg in [ceo_msg, cfo_msg, hr_msg]:
            assert 0.0 <= msg.confidence <= 1.0
            assert msg.stance in ("support", "oppose", "neutral")
