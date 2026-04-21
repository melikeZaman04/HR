from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.exceptions import SimulationNotFoundError
from app.application.use_cases.scenario_query_service import ScenarioQueryService
from app.domain.models import AgentResult, AggregatedDecision, FinalDecision, ScenarioRecord


def _scenario_record() -> ScenarioRecord:
    return ScenarioRecord(
        id=1,
        candidate_name="Ahmet Yılmaz",
        applied_role="Backend Developer",
        experience_years=5,
        tech_test_score=85,
        avg_months_per_job=18,
        glassdoor_score=4.2,
        expected_salary=90000,
        salary_currency="TRY",
        created_at=datetime(2026, 2, 26, 10, 0, 0),
    )


async def test_list_scenarios_pagination_delegates_to_repository() -> None:
    scenario_repo = AsyncMock()
    scenario_repo.list.return_value = [_scenario_record()]
    output_repo = AsyncMock()
    final_repo = AsyncMock()

    service = ScenarioQueryService(scenario_repo, output_repo, final_repo)
    result = await service.list_scenarios(limit=10, offset=5)

    scenario_repo.list.assert_called_once_with(limit=10, offset=5)
    assert len(result) == 1
    assert result[0].id == 1


async def test_get_simulation_returns_data_when_exists() -> None:
    scenario_repo = AsyncMock()
    scenario_repo.get_by_id.return_value = _scenario_record()

    output_repo = AsyncMock()
    output_repo.get_outputs_by_scenario_id.return_value = [
        AgentResult(agent_name="Strategy", score=80, rationale="ok"),
        AgentResult(agent_name="Salary", score=70, rationale="ok"),
        AgentResult(agent_name="Culture", score=75, rationale="ok"),
    ]

    final_repo = AsyncMock()
    final_repo.get_final_decision_by_scenario_id.return_value = AggregatedDecision(
        final_score=75.0,
        decision=FinalDecision.APPROVE,
    )

    service = ScenarioQueryService(scenario_repo, output_repo, final_repo)
    result = await service.get_simulation(1)

    assert result.scenario.id == 1
    assert len(result.agent_outputs) == 3
    assert result.aggregated_decision.decision == FinalDecision.APPROVE


async def test_get_simulation_raises_when_not_run() -> None:
    scenario_repo = AsyncMock()
    scenario_repo.get_by_id.return_value = _scenario_record()

    output_repo = AsyncMock()
    output_repo.get_outputs_by_scenario_id.return_value = []

    final_repo = AsyncMock()
    final_repo.get_final_decision_by_scenario_id.return_value = None

    service = ScenarioQueryService(scenario_repo, output_repo, final_repo)

    with pytest.raises(SimulationNotFoundError):
        await service.get_simulation(1)
