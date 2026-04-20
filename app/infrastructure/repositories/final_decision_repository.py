from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import AggregatedDecision, FinalDecision
from app.domain.repositories import FinalDecisionRepository
from app.infrastructure.database.models import FinalDecisionORM


class SqlAlchemyFinalDecisionRepository(FinalDecisionRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, scenario_id: int, decision: AggregatedDecision) -> None:
        """Create or update a final decision for a scenario (upsert)."""
        stmt = select(FinalDecisionORM).where(FinalDecisionORM.scenario_id == scenario_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.final_score = decision.final_score
            existing.decision = decision.decision.value
        else:
            row = FinalDecisionORM(
                scenario_id=scenario_id,
                final_score=decision.final_score,
                decision=decision.decision.value,
            )
            self.db.add(row)

        await self.db.commit()

    async def get_final_decision_by_scenario_id(self, scenario_id: int) -> AggregatedDecision | None:
        stmt = select(FinalDecisionORM).where(FinalDecisionORM.scenario_id == scenario_id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None

        return AggregatedDecision(
            final_score=row.final_score,
            decision=FinalDecision(row.decision),
        )
