from abc import ABC, abstractmethod

from app.domain.models import AgentResult, AggregatedDecision, ScenarioInput, ScenarioRecord


class ScenarioRepository(ABC):
    @abstractmethod
    async def create(self, scenario: ScenarioInput) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list(self, limit: int = 20, offset: int = 0) -> list[ScenarioRecord]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, scenario_id: int) -> ScenarioRecord | None:
        raise NotImplementedError


class AgentOutputRepository(ABC):
    @abstractmethod
    async def create_many(self, scenario_id: int, results: list[AgentResult]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_outputs_by_scenario_id(self, scenario_id: int) -> list[AgentResult]:
        raise NotImplementedError


class FinalDecisionRepository(ABC):
    @abstractmethod
    async def create(self, scenario_id: int, decision: AggregatedDecision) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_final_decision_by_scenario_id(self, scenario_id: int) -> AggregatedDecision | None:
        raise NotImplementedError
