from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class ScenarioORM(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    candidate_name: Mapped[str] = mapped_column(String(120), nullable=False)
    applied_role: Mapped[str] = mapped_column(String(120), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    tech_test_score: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_months_per_job: Mapped[int] = mapped_column(Integer, nullable=False)
    glassdoor_score: Mapped[float] = mapped_column(Float, nullable=False)
    expected_salary: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    agent_outputs = relationship("AgentOutputORM", back_populates="scenario", cascade="all, delete-orphan")
    final_decision = relationship(
        "FinalDecisionORM",
        back_populates="scenario",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AgentOutputORM(Base):
    __tablename__ = "agent_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(30), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    scenario = relationship("ScenarioORM", back_populates="agent_outputs")


class FinalDecisionORM(Base):
    __tablename__ = "final_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    final_score: Mapped[float] = mapped_column(Float, nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)

    scenario = relationship("ScenarioORM", back_populates="final_decision")
