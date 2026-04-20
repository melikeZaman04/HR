from app.application.exceptions import ScenarioNotFoundError, SimulationNotFoundError
from app.application.models import SimulationReadResult
from app.domain.repositories import AgentOutputRepository, FinalDecisionRepository, ScenarioRepository


class ScenarioQueryService:
    def __init__(
        self,
        scenario_repository: ScenarioRepository,
        agent_output_repository: AgentOutputRepository,
        final_decision_repository: FinalDecisionRepository,
    ) -> None:
        self.scenario_repository = scenario_repository
        self.agent_output_repository = agent_output_repository
        self.final_decision_repository = final_decision_repository

    async def list_scenarios(self, limit: int = 20, offset: int = 0):
        return await self.scenario_repository.list(limit=limit, offset=offset)

    async def get_scenario(self, scenario_id: int):
        scenario = await self.scenario_repository.get_by_id(scenario_id)
        if scenario is None:
            raise ScenarioNotFoundError(f"Scenario {scenario_id} not found")
        return scenario

    async def get_simulation(self, scenario_id: int) -> SimulationReadResult:
        scenario = await self.get_scenario(scenario_id)
        outputs = await self.agent_output_repository.get_outputs_by_scenario_id(scenario_id)
        final_decision = await self.final_decision_repository.get_final_decision_by_scenario_id(scenario_id)

        if not outputs or final_decision is None:
            raise SimulationNotFoundError(f"Simulation for scenario {scenario_id} not found")

        return SimulationReadResult(
            scenario=scenario,
            agent_outputs=outputs,
            aggregated_decision=final_decision,
        )
