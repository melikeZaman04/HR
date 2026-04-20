from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.scenario_query_service import ScenarioQueryService
from app.application.use_cases.scenario_service import ScenarioSimulationService
from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.agent_output_repository import SqlAlchemyAgentOutputRepository
from app.infrastructure.repositories.final_decision_repository import SqlAlchemyFinalDecisionRepository
from app.infrastructure.repositories.scenario_repository import SqlAlchemyScenarioRepository


async def get_scenario_service(db: AsyncSession = Depends(get_db_session)) -> ScenarioSimulationService:
    scenario_repo = SqlAlchemyScenarioRepository(db)
    output_repo = SqlAlchemyAgentOutputRepository(db)
    final_repo = SqlAlchemyFinalDecisionRepository(db)
    return ScenarioSimulationService(scenario_repo, output_repo, final_repo)


async def get_scenario_query_service(db: AsyncSession = Depends(get_db_session)) -> ScenarioQueryService:
    scenario_repo = SqlAlchemyScenarioRepository(db)
    output_repo = SqlAlchemyAgentOutputRepository(db)
    final_repo = SqlAlchemyFinalDecisionRepository(db)
    return ScenarioQueryService(scenario_repo, output_repo, final_repo)
