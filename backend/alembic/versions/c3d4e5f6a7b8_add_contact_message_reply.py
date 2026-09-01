"""add reply tracking to contact_messages

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('contact_messages', sa.Column('replied', sa.Boolean(), server_default=sa.false()))
    op.add_column('contact_messages', sa.Column('reply_text', sa.Text(), nullable=True))
    op.add_column('contact_messages', sa.Column('replied_at', sa.DateTime(), nullable=True))
    op.add_column('contact_messages', sa.Column('replied_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True))


def downgrade() -> None:
    op.drop_column('contact_messages', 'replied_by')
    op.drop_column('contact_messages', 'replied_at')
    op.drop_column('contact_messages', 'reply_text')
    op.drop_column('contact_messages', 'replied')
