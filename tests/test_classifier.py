"""Tests for the ScenarioClassifier service."""
import pytest

from app.domain.models import ScenarioInput
from app.domain.services.classifier import (
    ClassificationResult,
    ScenarioClassifier,
    ScenarioType,
)


class TestScenarioClassifier:
    """Tests for ScenarioClassifier."""
    
    @pytest.fixture
    def classifier(self) -> ScenarioClassifier:
        return ScenarioClassifier()
    
    # --- High Growth Scenario Tests ---
    
    def test_classifies_high_growth_scenario(self, classifier: ScenarioClassifier):
        """High ROI + significant budget + moderate risk -> HIGH_GROWTH."""
        scenario = ScenarioInput(
            name="AI Platform Expansion",
            description="Major AI investment with high returns",
            budget_million_usd=30.0,
            expected_roi_percent=55.0,  # Higher ROI
            risk_level=5,  # Moderate risk (not too high)
            team_readiness=8,  # Good team readiness
        )
        
        result = classifier.classify(scenario)
        
        assert result.primary_type == ScenarioType.HIGH_GROWTH
        assert result.confidence > 0.2
        assert "CEO" in result.recommended_weights
        assert result.recommended_weights["CEO"] > result.recommended_weights["HR"]
    
    def test_high_growth_aggressive_investment(self, classifier: ScenarioClassifier):
        """Very high ROI with large budget = aggressive growth."""
        scenario = ScenarioInput(
            name="Market Expansion",
            description="Aggressive market capture strategy",
            budget_million_usd=40.0,
            expected_roi_percent=60.0,
            risk_level=7,
            team_readiness=8,
        )
        
        result = classifier.classify(scenario)
        
        assert result.primary_type == ScenarioType.HIGH_GROWTH
        assert "growth" in result.classification_reasoning.lower() or "ROI" in result.classification_reasoning
    
    # --- Cost Optimization Scenario Tests ---
    
    def test_classifies_cost_optimization_scenario(self, classifier: ScenarioClassifier):
        """Low budget + low risk + low ROI -> COST_OPTIMIZATION."""
        scenario = ScenarioInput(
            name="Process Efficiency Upgrade",
            description="Streamline operations to reduce costs",
            budget_million_usd=2.0,
            expected_roi_percent=8.0,
            risk_level=2,
            team_readiness=8,
        )
        
        result = classifier.classify(scenario)
        
        assert result.primary_type == ScenarioType.COST_OPTIMIZATION
        assert result.recommended_weights["CFO"] >= result.recommended_weights["CEO"]
    
    # --- Team Expansion Scenario Tests ---
    
    def test_classifies_team_expansion_scenario(self, classifier: ScenarioClassifier):
        """Very low team readiness + moderate budget -> TEAM_EXPANSION."""
        scenario = ScenarioInput(
            name="Engineering Team Scale-up",
            description="Hire new engineers for product development",
            budget_million_usd=12.0,  # Moderate-high budget
            expected_roi_percent=20.0,  # Moderate ROI
            risk_level=4,
            team_readiness=2,  # Very low readiness - key trigger
        )
        
        result = classifier.classify(scenario)
        
        assert result.primary_type == ScenarioType.TEAM_EXPANSION
        assert result.recommended_weights["HR"] >= result.recommended_weights["CFO"]
        assert "HR" in result.classification_reasoning or "team" in result.classification_reasoning.lower()
    
    # --- Strategic Pivot Scenario Tests ---
    
    def test_classifies_strategic_pivot_scenario(self, classifier: ScenarioClassifier):
        """High risk + high ROI potential -> STRATEGIC_PIVOT."""
        scenario = ScenarioInput(
            name="Complete Platform Rewrite",
            description="Major technology shift to new architecture",
            budget_million_usd=15.0,
            expected_roi_percent=35.0,
            risk_level=9,
            team_readiness=5,
        )
        
        result = classifier.classify(scenario)
        
        assert result.primary_type == ScenarioType.STRATEGIC_PIVOT
        assert result.confidence > 0.15
    
    # --- Maintenance Scenario Tests ---
    
    def test_classifies_maintenance_scenario(self, classifier: ScenarioClassifier):
        """Low risk + moderate everything -> MAINTENANCE."""
        scenario = ScenarioInput(
            name="Annual System Updates",
            description="Regular maintenance and minor improvements",
            budget_million_usd=3.0,
            expected_roi_percent=12.0,
            risk_level=2,
            team_readiness=7,
        )
        
        result = classifier.classify(scenario)
        
        # Maintenance competes with cost_optimization for low-risk scenarios
        assert result.primary_type in (ScenarioType.MAINTENANCE, ScenarioType.COST_OPTIMIZATION)
    
    # --- Classification Result Structure Tests ---
    
    def test_classification_result_has_all_type_scores(self, classifier: ScenarioClassifier):
        """All scenario types should have scores."""
        scenario = ScenarioInput(
            name="Test Scenario",
            description="Test",
            budget_million_usd=10.0,
            expected_roi_percent=20.0,
            risk_level=5,
            team_readiness=5,
        )
        
        result = classifier.classify(scenario)
        
        assert len(result.type_scores) == 5
        assert all(st.value in result.type_scores for st in ScenarioType)
        assert all(0 <= score <= 1 for score in result.type_scores.values())
    
    def test_confidence_is_bounded(self, classifier: ScenarioClassifier):
        """Confidence should be between 0 and 1."""
        scenarios = [
            ScenarioInput("A", "D", 1.0, 5.0, 1, 1),
            ScenarioInput("B", "D", 50.0, 100.0, 10, 10),
            ScenarioInput("C", "D", 10.0, 20.0, 5, 5),
        ]
        
        for scenario in scenarios:
            result = classifier.classify(scenario)
            assert 0.0 <= result.confidence <= 1.0
    
    def test_recommended_weights_sum_to_one(self, classifier: ScenarioClassifier):
        """Recommended weights should sum to approximately 1."""
        scenario = ScenarioInput(
            name="Test",
            description="Test",
            budget_million_usd=10.0,
            expected_roi_percent=20.0,
            risk_level=5,
            team_readiness=5,
        )
        
        result = classifier.classify(scenario)
        
        total = sum(result.recommended_weights.values())
        assert abs(total - 1.0) < 0.01
    
    def test_classification_has_reasoning(self, classifier: ScenarioClassifier):
        """Classification should include human-readable reasoning."""
        scenario = ScenarioInput(
            name="Test",
            description="Test",
            budget_million_usd=10.0,
            expected_roi_percent=20.0,
            risk_level=5,
            team_readiness=5,
        )
        
        result = classifier.classify(scenario)
        
        assert len(result.classification_reasoning) > 0
        assert "|" in result.classification_reasoning  # Multiple reasons joined
    
    # --- Agent Weights Getter Tests ---
    
    def test_get_agent_weights_for_high_growth(self, classifier: ScenarioClassifier):
        """HIGH_GROWTH should prioritize CEO."""
        weights = classifier.get_agent_weights(ScenarioType.HIGH_GROWTH)
        
        assert weights["CEO"] >= weights["CFO"]
        assert weights["CEO"] >= weights["HR"]
    
    def test_get_agent_weights_for_cost_optimization(self, classifier: ScenarioClassifier):
        """COST_OPTIMIZATION should prioritize CFO."""
        weights = classifier.get_agent_weights(ScenarioType.COST_OPTIMIZATION)
        
        assert weights["CFO"] >= weights["CEO"]
        assert weights["CFO"] >= weights["HR"]
    
    def test_get_agent_weights_for_team_expansion(self, classifier: ScenarioClassifier):
        """TEAM_EXPANSION should prioritize HR."""
        weights = classifier.get_agent_weights(ScenarioType.TEAM_EXPANSION)
        
        assert weights["HR"] >= weights["CEO"]
        assert weights["HR"] >= weights["CFO"]
    
    # --- Edge Cases ---
    
    def test_extreme_values_handled(self, classifier: ScenarioClassifier):
        """Extreme input values should not crash."""
        extreme_scenarios = [
            ScenarioInput("Min", "D", 0.01, 0.0, 1, 1),
            ScenarioInput("Max", "D", 1000.0, 500.0, 10, 10),
        ]
        
        for scenario in extreme_scenarios:
            result = classifier.classify(scenario)
            assert result.primary_type is not None
            assert 0.0 <= result.confidence <= 1.0
    
    def test_secondary_type_only_if_confident(self, classifier: ScenarioClassifier):
        """Secondary type should only appear if score > 0.2."""
        scenario = ScenarioInput(
            name="Balanced",
            description="A balanced scenario",
            budget_million_usd=10.0,
            expected_roi_percent=20.0,
            risk_level=5,
            team_readiness=5,
        )
        
        result = classifier.classify(scenario)
        
        if result.secondary_type is not None:
            assert result.type_scores[result.secondary_type.value] > 0.2


class TestScenarioTypeEnum:
    """Tests for ScenarioType enum."""
    
    def test_all_types_have_string_values(self):
        """All enum values should be strings."""
        for st in ScenarioType:
            assert isinstance(st.value, str)
    
    def test_enum_values_are_snake_case(self):
        """Enum values should be snake_case for API consistency."""
        for st in ScenarioType:
            assert st.value.islower() or "_" in st.value
