"""add blood_group and tshirt_size to members

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('members', sa.Column('blood_group', sa.String(), nullable=True))
    op.add_column('members', sa.Column('tshirt_size', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('members', 'tshirt_size')
    op.drop_column('members', 'blood_group')
