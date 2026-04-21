"""Tests for the CandidateProfiler service — HireSync candidate context."""
import pytest

from app.domain.models import ScenarioInput
from app.domain.services.classifier import (
    CandidateProfiler,
    ClassificationResult,
    ScenarioType,
)


class TestCandidateProfiler:
    """Tests for CandidateProfiler."""

    @pytest.fixture
    def classifier(self) -> CandidateProfiler:
        return CandidateProfiler()

    # --- High Growth Scenario Tests ---

    def test_classifies_high_growth_scenario(self, classifier: CandidateProfiler):
        """High tech score + deep experience → HIGH_GROWTH."""
        scenario = ScenarioInput(
            candidate_name="Senior Dev",
            applied_role="Backend Developer",
            experience_years=8,
            tech_test_score=90,
            avg_months_per_job=36,
            glassdoor_score=4.5,
            expected_salary=110000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type == ScenarioType.HIGH_GROWTH
        assert result.confidence > 0.2
        assert "Strategy" in result.recommended_weights
        assert result.recommended_weights["Strategy"] > result.recommended_weights["Culture"]

    def test_high_growth_reasoning_mentions_growth(self, classifier: CandidateProfiler):
        """HIGH_GROWTH reasoning should mention growth or senior profile."""
        scenario = ScenarioInput(
            candidate_name="Senior Dev",
            applied_role="Backend Developer",
            experience_years=9,
            tech_test_score=92,
            avg_months_per_job=30,
            glassdoor_score=4.5,
            expected_salary=115000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type == ScenarioType.HIGH_GROWTH
        assert "growth" in result.classification_reasoning.lower() or "senior" in result.classification_reasoning.lower()

    # --- Cost Optimization Scenario Tests ---

    def test_classifies_cost_optimization_scenario(self, classifier: CandidateProfiler):
        """Low salary expectation → COST_OPTIMIZATION."""
        scenario = ScenarioInput(
            candidate_name="Budget Dev",
            applied_role="Backend Developer",
            experience_years=3,
            tech_test_score=70,
            avg_months_per_job=24,
            glassdoor_score=3.5,
            expected_salary=40000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type == ScenarioType.COST_OPTIMIZATION
        assert result.recommended_weights["Salary"] >= result.recommended_weights["Strategy"]

    # --- Team Expansion Scenario Tests ---

    def test_classifies_team_expansion_scenario(self, classifier: CandidateProfiler):
        """Very low experience + good culture fit → TEAM_EXPANSION."""
        scenario = ScenarioInput(
            candidate_name="Junior Dev",
            applied_role="Frontend Developer",
            experience_years=1,
            tech_test_score=55,
            avg_months_per_job=12,
            glassdoor_score=4.2,
            expected_salary=35000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type == ScenarioType.TEAM_EXPANSION
        assert result.recommended_weights["Culture"] >= result.recommended_weights["Salary"]
        assert "Culture" in result.classification_reasoning or "team" in result.classification_reasoning.lower()

    # --- Strategic Pivot Scenario Tests ---

    def test_classifies_strategic_pivot_scenario(self, classifier: CandidateProfiler):
        """High tech score but frequent job changes → STRATEGIC_PIVOT."""
        scenario = ScenarioInput(
            candidate_name="Job Hopper",
            applied_role="Backend Developer",
            experience_years=4,
            tech_test_score=88,
            avg_months_per_job=5,
            glassdoor_score=3.0,
            expected_salary=90000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type == ScenarioType.STRATEGIC_PIVOT
        assert result.confidence > 0.15

    # --- Maintenance Scenario Tests ---

    def test_classifies_maintenance_scenario(self, classifier: CandidateProfiler):
        """Balanced average candidate → MAINTENANCE or COST_OPTIMIZATION."""
        scenario = ScenarioInput(
            candidate_name="Average Dev",
            applied_role="Backend Developer",
            experience_years=6,
            tech_test_score=65,
            avg_months_per_job=36,
            glassdoor_score=3.8,
            expected_salary=80000,
        )

        result = classifier.classify(scenario)

        assert result.primary_type in (ScenarioType.MAINTENANCE, ScenarioType.COST_OPTIMIZATION)

    # --- Classification Result Structure Tests ---

    def test_classification_result_has_all_type_scores(self, classifier: CandidateProfiler):
        """All scenario types should have scores."""
        scenario = ScenarioInput(
            candidate_name="Test Candidate",
            applied_role="Backend Developer",
            experience_years=5,
            tech_test_score=75,
            avg_months_per_job=24,
            glassdoor_score=4.0,
            expected_salary=80000,
        )

        result = classifier.classify(scenario)

        assert len(result.type_scores) == 5
        assert all(st.value in result.type_scores for st in ScenarioType)
        assert all(0 <= score <= 1 for score in result.type_scores.values())

    def test_confidence_is_bounded(self, classifier: CandidateProfiler):
        """Confidence should be between 0 and 1."""
        scenarios = [
            ScenarioInput(candidate_name="A", applied_role="Dev", experience_years=1, tech_test_score=10, avg_months_per_job=1, glassdoor_score=1.0, expected_salary=20000),
            ScenarioInput(candidate_name="B", applied_role="Dev", experience_years=15, tech_test_score=100, avg_months_per_job=60, glassdoor_score=5.0, expected_salary=200000),
            ScenarioInput(candidate_name="C", applied_role="Dev", experience_years=5, tech_test_score=70, avg_months_per_job=24, glassdoor_score=4.0, expected_salary=80000),
        ]

        for scenario in scenarios:
            result = classifier.classify(scenario)
            assert 0.0 <= result.confidence <= 1.0

    def test_recommended_weights_sum_to_one(self, classifier: CandidateProfiler):
        """Recommended weights should sum to approximately 1."""
        scenario = ScenarioInput(
            candidate_name="Test",
            applied_role="Dev",
            experience_years=5,
            tech_test_score=75,
            avg_months_per_job=24,
            glassdoor_score=4.0,
            expected_salary=80000,
        )

        result = classifier.classify(scenario)

        total = sum(result.recommended_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_classification_has_reasoning(self, classifier: CandidateProfiler):
        """Classification should include human-readable reasoning."""
        scenario = ScenarioInput(
            candidate_name="Test",
            applied_role="Dev",
            experience_years=5,
            tech_test_score=75,
            avg_months_per_job=24,
            glassdoor_score=4.0,
            expected_salary=80000,
        )

        result = classifier.classify(scenario)

        assert len(result.classification_reasoning) > 0
        assert "|" in result.classification_reasoning

    # --- Agent Weights Getter Tests ---

    def test_get_agent_weights_for_high_growth(self, classifier: CandidateProfiler):
        """HIGH_GROWTH should prioritize Strategy."""
        weights = classifier.get_agent_weights(ScenarioType.HIGH_GROWTH)

        assert weights["Strategy"] >= weights["Salary"]
        assert weights["Strategy"] >= weights["Culture"]

    def test_get_agent_weights_for_cost_optimization(self, classifier: CandidateProfiler):
        """COST_OPTIMIZATION should prioritize Salary."""
        weights = classifier.get_agent_weights(ScenarioType.COST_OPTIMIZATION)

        assert weights["Salary"] >= weights["Strategy"]
        assert weights["Salary"] >= weights["Culture"]

    def test_get_agent_weights_for_team_expansion(self, classifier: CandidateProfiler):
        """TEAM_EXPANSION should prioritize Culture."""
        weights = classifier.get_agent_weights(ScenarioType.TEAM_EXPANSION)

        assert weights["Culture"] >= weights["Strategy"]
        assert weights["Culture"] >= weights["Salary"]

    # --- Edge Cases ---

    def test_extreme_values_handled(self, classifier: CandidateProfiler):
        """Extreme input values should not crash."""
        extreme_scenarios = [
            ScenarioInput(candidate_name="Min", applied_role="Dev", experience_years=0, tech_test_score=0, avg_months_per_job=1, glassdoor_score=1.0, expected_salary=1),
            ScenarioInput(candidate_name="Max", applied_role="Dev", experience_years=30, tech_test_score=100, avg_months_per_job=120, glassdoor_score=5.0, expected_salary=500000),
        ]

        for scenario in extreme_scenarios:
            result = classifier.classify(scenario)
            assert result.primary_type is not None
            assert 0.0 <= result.confidence <= 1.0

    def test_secondary_type_only_if_confident(self, classifier: CandidateProfiler):
        """Secondary type should only appear if score > 0.2."""
        scenario = ScenarioInput(
            candidate_name="Balanced",
            applied_role="Backend Developer",
            experience_years=5,
            tech_test_score=75,
            avg_months_per_job=24,
            glassdoor_score=4.0,
            expected_salary=80000,
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
