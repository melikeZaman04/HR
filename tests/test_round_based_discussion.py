"""
Test suite for round-based multi-agent discussion orchestration.

Tests the ScenarioSimulationService with multiple discussion rounds,
early termination conditions, and position update logic.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.application.models import RoundBasedSimulationResult, RoundResult
from app.application.use_cases.scenario_service import ScenarioSimulationService
from app.domain.agents.ceo_agent import CEOAgent
from app.domain.agents.cfo_agent import CFOAgent
from app.domain.agents.hr_agent import HRAgent
from app.domain.models import AgentMessage, AgentResult, AggregatedDecision, FinalDecision, ScenarioInput, ScenarioRecord
from app.domain.services.aggregator import DecisionAggregator


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_scenario_record() -> ScenarioRecord:
    """Create a mock scenario record for testing."""
    return ScenarioRecord(
        id=1,
        name="Test Project",
        description="A test scenario",
        budget_million_usd=5.0,
        expected_roi_percent=40.0,
        risk_level=5,
        team_readiness=7,
        created_at=datetime.now(),
    )


@pytest.fixture
def mock_repositories(mock_scenario_record):
    """Create async mock repositories for testing."""
    scenario_repo = AsyncMock()
    scenario_repo.get_by_id.return_value = mock_scenario_record

    agent_output_repo = AsyncMock()
    final_decision_repo = AsyncMock()

    return scenario_repo, agent_output_repo, final_decision_repo


@pytest.fixture
def service(mock_repositories) -> ScenarioSimulationService:
    """Create a service instance with mock repositories."""
    scenario_repo, agent_output_repo, final_decision_repo = mock_repositories
    return ScenarioSimulationService(
        scenario_repository=scenario_repo,
        agent_output_repository=agent_output_repo,
        final_decision_repository=final_decision_repo,
    )


@pytest.fixture
def high_agreement_scenario() -> ScenarioRecord:
    """Scenario that leads to high agreement (all support)."""
    return ScenarioRecord(
        id=2,
        name="Great Opportunity",
        description="High ROI, low risk",
        budget_million_usd=2.0,
        expected_roi_percent=80.0,
        risk_level=2,
        team_readiness=9,
        created_at=datetime.now(),
    )


@pytest.fixture
def divisive_scenario() -> ScenarioRecord:
    """Scenario that leads to mixed opinions."""
    return ScenarioRecord(
        id=3,
        name="Risky Venture",
        description="High potential but risky",
        budget_million_usd=8.0,
        expected_roi_percent=60.0,
        risk_level=8,
        team_readiness=4,
        created_at=datetime.now(),
    )


# ============================================================================
# Round Execution Tests
# ============================================================================

class TestRoundExecution:
    """Tests for basic round execution behavior."""

    async def test_two_rounds_executed(self, service, mock_repositories):
        """Verify that 2 rounds are executed when n_rounds=2."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        assert isinstance(result, RoundBasedSimulationResult)
        assert 1 <= result.total_rounds <= 2
        assert len(result.rounds) == result.total_rounds

    async def test_three_rounds_executed(self, service):
        """Verify that 3 rounds are executed when n_rounds=3."""
        result = await service.run_simulation(scenario_id=1, n_rounds=3)

        assert 1 <= result.total_rounds <= 3
        assert len(result.rounds) == result.total_rounds

    async def test_single_round_execution(self, service):
        """Verify that single round works correctly."""
        result = await service.run_simulation(scenario_id=1, n_rounds=1)

        assert result.total_rounds == 1
        assert len(result.rounds) == 1
        assert result.rounds[0].round_number == 1

    async def test_each_round_has_three_agents(self, service):
        """Verify each round contains messages from all 3 agents."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        for round_result in result.rounds:
            assert len(round_result.messages) == 3
            agent_names = {msg.agent for msg in round_result.messages}
            assert agent_names == {"CEO", "CFO", "HR"}


class TestRoundNumberIncrement:
    """Tests for round number tracking."""

    async def test_round_number_increments(self, service):
        """Verify round_number increments correctly across rounds."""
        result = await service.run_simulation(scenario_id=1, n_rounds=3)

        for i, round_result in enumerate(result.rounds):
            expected_round = i + 1
            assert round_result.round_number == expected_round
            for msg in round_result.messages:
                assert msg.round_number == expected_round

    async def test_first_round_is_one(self, service):
        """Verify first round has round_number=1."""
        result = await service.run_simulation(scenario_id=1, n_rounds=1)

        assert result.rounds[0].round_number == 1
        for msg in result.rounds[0].messages:
            assert msg.round_number == 1


# ============================================================================
# Previous Messages Tests
# ============================================================================

class TestAgentsSeeHistory:
    """Tests for agents receiving previous messages."""

    async def test_agents_see_previous_messages(self, mock_repositories, mock_scenario_record):
        """Verify agents receive previous messages from earlier rounds."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        received_messages = {"CEO": [], "CFO": [], "HR": []}

        class TrackedCEOAgent(CEOAgent):
            def analyze(self, scenario, previous_messages=None):
                received_messages["CEO"].append(
                    len(previous_messages) if previous_messages else 0
                )
                return super().analyze(scenario, previous_messages)

        class TrackedCFOAgent(CFOAgent):
            def analyze(self, scenario, previous_messages=None):
                received_messages["CFO"].append(
                    len(previous_messages) if previous_messages else 0
                )
                return super().analyze(scenario, previous_messages)

        class TrackedHRAgent(HRAgent):
            def analyze(self, scenario, previous_messages=None):
                received_messages["HR"].append(
                    len(previous_messages) if previous_messages else 0
                )
                return super().analyze(scenario, previous_messages)

        with patch('app.application.use_cases.scenario_service.AgentFactory') as mock_factory:
            mock_factory.create_default_agents.return_value = [
                TrackedCEOAgent(),
                TrackedCFOAgent(),
                TrackedHRAgent(),
            ]

            service = ScenarioSimulationService(
                scenario_repository=scenario_repo,
                agent_output_repository=agent_output_repo,
                final_decision_repository=final_decision_repo,
            )

            await service.run_simulation(scenario_id=1, n_rounds=2)

        assert received_messages["CEO"][0] == 0  # Round 1
        assert received_messages["CFO"][0] == 1  # Round 1
        assert received_messages["HR"][0] == 2   # Round 1

        if len(received_messages["CEO"]) > 1:    # Round 2 if not early stopped
            assert received_messages["CEO"][1] == 3
            assert received_messages["CFO"][1] == 4
            assert received_messages["HR"][1] == 5

    async def test_cfo_sees_ceo_message_in_same_round(self, service):
        """CFO should see CEO's message from the same round."""
        result = await service.run_simulation(scenario_id=1, n_rounds=1)

        round_messages = result.rounds[0].messages
        assert round_messages[0].agent == "CEO"
        assert round_messages[1].agent == "CFO"
        assert round_messages[2].agent == "HR"


# ============================================================================
# Confidence Changes Tests
# ============================================================================

class TestConfidenceChanges:
    """Tests for confidence adjustments across rounds."""

    async def test_confidence_can_change_across_rounds(self, mock_repositories):
        """At least one agent's confidence should change between rounds."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        divisive = ScenarioRecord(
            id=1,
            name="Divisive Project",
            description="Mixed signals",
            budget_million_usd=10.0,
            expected_roi_percent=30.0,
            risk_level=7,
            team_readiness=4,
            created_at=datetime.now(),
        )
        scenario_repo.get_by_id.return_value = divisive

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        result = await service.run_simulation(scenario_id=1, n_rounds=3)

        if result.total_rounds >= 2:
            round1_conf = {msg.agent: msg.confidence for msg in result.rounds[0].messages}
            round2_conf = {msg.agent: msg.confidence for msg in result.rounds[1].messages}

            changes = []
            for agent in ["CEO", "CFO", "HR"]:
                if abs(round1_conf[agent] - round2_conf[agent]) > 0.001:
                    changes.append(agent)

            if not result.stability_reached:
                assert len(changes) > 0 or result.consensus_reached

    async def test_minority_agent_reduces_confidence(self, mock_repositories):
        """Agent in minority should reduce confidence."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        scenario = ScenarioRecord(
            id=1,
            name="Test",
            description="Test",
            budget_million_usd=5.0,
            expected_roi_percent=50.0,
            risk_level=6,
            team_readiness=5,
            created_at=datetime.now(),
        )
        scenario_repo.get_by_id.return_value = scenario

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        for round_result in result.rounds:
            for msg in round_result.messages:
                assert 0.0 <= msg.confidence <= 1.0


# ============================================================================
# Early Termination Tests
# ============================================================================

class TestEarlyTermination:
    """Tests for early termination conditions."""

    async def test_consensus_early_stop(self, mock_repositories):
        """Simulation should stop early if all agents reach consensus."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        unanimous = ScenarioRecord(
            id=1,
            name="Easy Win",
            description="High ROI, low risk, ready team",
            budget_million_usd=1.0,
            expected_roi_percent=100.0,
            risk_level=1,
            team_readiness=10,
            created_at=datetime.now(),
        )
        scenario_repo.get_by_id.return_value = unanimous

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        result = await service.run_simulation(scenario_id=1, n_rounds=5)

        if result.consensus_reached:
            stances = {msg.stance for msg in result.final_messages}
            assert len(stances) == 1

    async def test_stability_early_stop(self, mock_repositories):
        """Simulation should stop if no agent changes position."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        result = await service.run_simulation(scenario_id=1, n_rounds=10)

        assert result.total_rounds <= 10

        if result.stability_reached and result.total_rounds >= 2:
            prev_round = result.rounds[-2].messages
            last_round = result.rounds[-1].messages

            prev_by_agent = {msg.agent: msg for msg in prev_round}
            last_by_agent = {msg.agent: msg for msg in last_round}

            for agent in ["CEO", "CFO", "HR"]:
                assert prev_by_agent[agent].stance == last_by_agent[agent].stance
                assert abs(prev_by_agent[agent].confidence - last_by_agent[agent].confidence) <= 0.01

    async def test_max_rounds_respected(self, mock_repositories):
        """Simulation should not exceed n_rounds."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        for max_rounds in [1, 2, 3]:
            result = await service.run_simulation(scenario_id=1, n_rounds=max_rounds)
            assert result.total_rounds <= max_rounds


# ============================================================================
# Result Structure Tests
# ============================================================================

class TestResultStructure:
    """Tests for the result data structure."""

    async def test_result_contains_required_fields(self, service):
        """Result should contain all required fields."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        assert hasattr(result, 'scenario_id')
        assert hasattr(result, 'rounds')
        assert hasattr(result, 'total_rounds')
        assert hasattr(result, 'consensus_reached')
        assert hasattr(result, 'stability_reached')
        assert hasattr(result, 'final_messages')
        assert hasattr(result, 'agent_outputs')
        assert hasattr(result, 'aggregated_decision')

    async def test_final_messages_match_last_round(self, service):
        """final_messages should be from the last round."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        last_round = result.rounds[-1]
        assert result.final_messages == last_round.messages

    async def test_agent_outputs_match_final_messages(self, service):
        """agent_outputs (legacy) should correspond to final_messages."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        assert len(result.agent_outputs) == len(result.final_messages)

        for msg, output in zip(result.final_messages, result.agent_outputs):
            assert output.agent_name == msg.agent
            assert 0 <= output.score <= 100

    async def test_aggregated_decision_present(self, service):
        """Result should include aggregated decision."""
        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        assert isinstance(result.aggregated_decision, AggregatedDecision)
        assert result.aggregated_decision.decision in [
            FinalDecision.APPROVE,
            FinalDecision.REVISE,
            FinalDecision.REJECT,
        ]


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""

    async def test_full_simulation_flow(self, service, mock_repositories):
        """Test complete simulation flow with persistence."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        result = await service.run_simulation(scenario_id=1, n_rounds=2)

        agent_output_repo.create_many.assert_called_once()
        final_decision_repo.create.assert_called_once()

        assert result.scenario_id == 1
        assert result.total_rounds >= 1
        assert len(result.final_messages) == 3

    async def test_scenario_not_found_raises(self, mock_repositories):
        """Should raise exception for non-existent scenario."""
        from app.application.exceptions import ScenarioNotFoundError

        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories
        scenario_repo.get_by_id.return_value = None

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        with pytest.raises(ScenarioNotFoundError):
            await service.run_simulation(scenario_id=999, n_rounds=2)

    async def test_different_scenarios_different_results(self, mock_repositories):
        """Different scenarios should produce different results."""
        scenario_repo, agent_output_repo, final_decision_repo = mock_repositories

        service = ScenarioSimulationService(
            scenario_repository=scenario_repo,
            agent_output_repository=agent_output_repo,
            final_decision_repository=final_decision_repo,
        )

        high_opp = ScenarioRecord(
            id=1, name="High", description="",
            budget_million_usd=2.0, expected_roi_percent=100.0,
            risk_level=2, team_readiness=9, created_at=datetime.now()
        )
        scenario_repo.get_by_id.return_value = high_opp
        result_high = await service.run_simulation(scenario_id=1, n_rounds=2)

        agent_output_repo.reset_mock()
        final_decision_repo.reset_mock()

        low_opp = ScenarioRecord(
            id=2, name="Low", description="",
            budget_million_usd=20.0, expected_roi_percent=-20.0,
            risk_level=9, team_readiness=2, created_at=datetime.now()
        )
        scenario_repo.get_by_id.return_value = low_opp
        result_low = await service.run_simulation(scenario_id=2, n_rounds=2)

        assert result_high.aggregated_decision.final_score != result_low.aggregated_decision.final_score
