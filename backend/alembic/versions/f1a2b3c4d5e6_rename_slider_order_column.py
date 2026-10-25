"""rename slider_images.order to display_order

The original table was created with a column named "order", but the
SQLAlchemy model (SliderImage.display_order) was renamed at some point
without a matching migration ever being written, so production never
picked up the change. This was causing the public /api/public/homepage
endpoint to 500 on every request, since its slider-image query reads
SliderImage.display_order.

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-10-26 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f1a2b3c4d5e6'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('slider_images', 'order', new_column_name='display_order')


def downgrade() -> None:
    op.alter_column('slider_images', 'display_order', new_column_name='order')
