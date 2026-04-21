from datetime import datetime

from fastapi.testclient import TestClient

from app.application.exceptions import ScenarioNotFoundError, SimulationNotFoundError
from app.application.models import SimulationReadResult
from app.domain.models import AgentResult, AggregatedDecision, FinalDecision, ScenarioRecord
from app.main import app
from app.presentation.dependencies import get_scenario_query_service


class FakeScenarioQueryService:
    def __init__(self) -> None:
        self.scenario = ScenarioRecord(
            id=1,
            candidate_name="Ahmet Yılmaz",
            applied_role="Backend Developer",
            experience_years=5,
            tech_test_score=85,
            avg_months_per_job=18,
            glassdoor_score=4.2,
            expected_salary=90000,
            created_at=datetime(2026, 2, 26, 10, 0, 0),
        )

    async def list_scenarios(self, limit: int = 20, offset: int = 0):
        return [self.scenario][offset : offset + limit]

    async def get_scenario(self, scenario_id: int):
        return self.scenario

    async def get_simulation(self, scenario_id: int) -> SimulationReadResult:
        return SimulationReadResult(
            scenario=self.scenario,
            agent_outputs=[
                AgentResult(agent_name="Strategy", score=80, rationale="ok"),
                AgentResult(agent_name="Salary", score=70, rationale="ok"),
                AgentResult(agent_name="Culture", score=75, rationale="ok"),
            ],
            aggregated_decision=AggregatedDecision(
                final_score=75.0,
                decision=FinalDecision.APPROVE,
            ),
        )


class FakeScenarioNotFoundQueryService(FakeScenarioQueryService):
    async def get_scenario(self, scenario_id: int):
        raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")


class FakeSimulationNotFoundQueryService(FakeScenarioQueryService):
    async def get_simulation(self, scenario_id: int) -> SimulationReadResult:
        raise SimulationNotFoundError(f"Simulation for scenario {scenario_id} not found")


def test_get_list_scenarios_happy_path() -> None:
    app.dependency_overrides[get_scenario_query_service] = lambda: FakeScenarioQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/scenarios")

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 20
    assert payload["offset"] == 0
    assert len(payload["items"]) == 1
    assert payload["items"][0]["id"] == 1

    app.dependency_overrides.clear()


def test_get_scenario_detail_happy_path() -> None:
    app.dependency_overrides[get_scenario_query_service] = lambda: FakeScenarioQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/scenarios/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["candidate_name"] == "Ahmet Yılmaz"

    app.dependency_overrides.clear()


def test_get_simulation_happy_path() -> None:
    app.dependency_overrides[get_scenario_query_service] = lambda: FakeScenarioQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/scenarios/1/simulation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["scenario"]["id"] == 1
    assert len(payload["agent_outputs"]) == 3
    assert payload["final_decision"] == "APPROVE"

    app.dependency_overrides.clear()


def test_get_scenario_detail_returns_404_when_not_found() -> None:
    app.dependency_overrides[get_scenario_query_service] = lambda: FakeScenarioNotFoundQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/scenarios/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Scenario 999 not found"

    app.dependency_overrides.clear()


def test_get_simulation_returns_404_when_not_run() -> None:
    app.dependency_overrides[get_scenario_query_service] = lambda: FakeSimulationNotFoundQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/scenarios/1/simulation")

    assert response.status_code == 404
    assert response.json()["detail"] == "Simulation for scenario 1 not found"

    app.dependency_overrides.clear()
