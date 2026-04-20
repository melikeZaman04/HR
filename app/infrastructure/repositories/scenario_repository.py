from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import ScenarioInput, ScenarioRecord
from app.domain.repositories import ScenarioRepository
from app.infrastructure.database.models import ScenarioORM


class SqlAlchemyScenarioRepository(ScenarioRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, scenario: ScenarioInput) -> int:
        row = ScenarioORM(
            candidate_name=scenario.candidate_name,
            applied_role=scenario.applied_role,
            experience_years=scenario.experience_years,
            tech_test_score=scenario.tech_test_score,
            avg_months_per_job=scenario.avg_months_per_job,
            glassdoor_score=scenario.glassdoor_score,
            expected_salary=scenario.expected_salary,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row.id

    async def list(self, limit: int = 20, offset: int = 0) -> list[ScenarioRecord]:
        stmt = (
            select(ScenarioORM)
            .order_by(ScenarioORM.created_at.desc(), ScenarioORM.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    async def get_by_id(self, scenario_id: int) -> ScenarioRecord | None:
        row = await self.db.get(ScenarioORM, scenario_id)
        if row is None:
            return None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: ScenarioORM) -> ScenarioRecord:
        return ScenarioRecord(
            id=row.id,
            candidate_name=row.candidate_name,
            applied_role=row.applied_role,
            experience_years=row.experience_years,
            tech_test_score=row.tech_test_score,
            avg_months_per_job=row.avg_months_per_job,
            glassdoor_score=row.glassdoor_score,
            expected_salary=row.expected_salary,
            created_at=row.created_at,
        )
