"""add memories updated_at

Revision ID: 1f2e3d4c5b6a
Revises: ff47fe6e507d
Create Date: 2026-08-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '1f2e3d4c5b6a'
down_revision = 'ff47fe6e507d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('memories', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))


def downgrade() -> None:
    op.drop_column('memories', 'updated_at')