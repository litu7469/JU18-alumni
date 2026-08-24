"""add event registration_fee

Revision ID: 9c8d7e6f5a4b
Revises: 1f2e3d4c5b6a
Create Date: 2026-08-21 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '9c8d7e6f5a4b'
down_revision = '1f2e3d4c5b6a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('events', sa.Column('registration_fee', sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column('events', 'registration_fee')