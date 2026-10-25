"""rename committee_members.order to display_order

Same schema drift as the slider_images fix: the original table was
created with a column named "order", but the SQLAlchemy model
(CommitteeMember.display_order) was renamed at some point without a
matching migration ever being written, so production never picked up
the change. This was causing the public /api/public/homepage endpoint
to 500 on every request, since its committee-members query reads
CommitteeMember.display_order.

Revision ID: 3845b2a4c3ab
Revises: f1a2b3c4d5e6
Create Date: 2026-10-26 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '3845b2a4c3ab'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('committee_members', 'order', new_column_name='display_order')


def downgrade() -> None:
    op.alter_column('committee_members', 'display_order', new_column_name='order')
