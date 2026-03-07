"""Add input_path, output_path to test_cases for file upload.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("test_cases", sa.Column("input_path", sa.Text(), nullable=True))
    op.add_column("test_cases", sa.Column("output_path", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("test_cases", "output_path")
    op.drop_column("test_cases", "input_path")
