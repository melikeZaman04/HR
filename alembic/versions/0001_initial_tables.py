"""initial tables

Revision ID: 0001_initial_tables
Revises: 
Create Date: 2026-02-26

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("budget_million_usd", sa.Float(), nullable=False),
        sa.Column("expected_roi_percent", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.Integer(), nullable=False),
        sa.Column("team_readiness", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(op.f("ix_scenarios_id"), "scenarios", ["id"], unique=False)

    op.create_table(
        "agent_outputs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scenario_id", sa.Integer(), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(length=30), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
    )
    op.create_index(op.f("ix_agent_outputs_id"), "agent_outputs", ["id"], unique=False)

    op.create_table(
        "final_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scenario_id", sa.Integer(), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
    )
    op.create_index(op.f("ix_final_decisions_id"), "final_decisions", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_final_decisions_id"), table_name="final_decisions")
    op.drop_table("final_decisions")

    op.drop_index(op.f("ix_agent_outputs_id"), table_name="agent_outputs")
    op.drop_table("agent_outputs")

    op.drop_index(op.f("ix_scenarios_id"), table_name="scenarios")
    op.drop_table("scenarios")
