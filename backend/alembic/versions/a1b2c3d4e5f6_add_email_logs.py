"""add email_logs table

Revision ID: a1b2c3d4e5f6
Revises: 9c8d7e6f5a4b
Create Date: 2026-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '9c8d7e6f5a4b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'email_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('recipient_type', sa.String(), nullable=False),
        sa.Column('recipient_count', sa.Integer(), server_default='0'),
        sa.Column('failed_count', sa.Integer(), server_default='0'),
        sa.Column('sent_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('sent_by_name', sa.String(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('email_logs')
