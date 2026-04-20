from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import AgentResult
from app.domain.repositories import AgentOutputRepository
from app.infrastructure.database.models import AgentOutputORM


class SqlAlchemyAgentOutputRepository(AgentOutputRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_many(self, scenario_id: int, results: list[AgentResult]) -> None:
        """Create agent outputs, replacing any existing ones for this scenario."""
        delete_stmt = delete(AgentOutputORM).where(AgentOutputORM.scenario_id == scenario_id)
        await self.db.execute(delete_stmt)

        rows = [
            AgentOutputORM(
                scenario_id=scenario_id,
                agent_name=result.agent_name,
                score=result.score,
                rationale=result.rationale,
            )
            for result in results
        ]
        self.db.add_all(rows)
        await self.db.commit()

    async def get_outputs_by_scenario_id(self, scenario_id: int) -> list[AgentResult]:
        stmt = (
            select(AgentOutputORM)
            .where(AgentOutputORM.scenario_id == scenario_id)
            .order_by(AgentOutputORM.id.asc())
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [
            AgentResult(agent_name=row.agent_name, score=row.score, rationale=row.rationale)
            for row in rows
        ]
