"""add salary_currency to scenarios

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002_hireSync_candidate_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'scenarios',
        sa.Column('salary_currency', sa.String(3), nullable=False, server_default='TRY')
    )


def downgrade() -> None:
    op.drop_column('scenarios', 'salary_currency')
