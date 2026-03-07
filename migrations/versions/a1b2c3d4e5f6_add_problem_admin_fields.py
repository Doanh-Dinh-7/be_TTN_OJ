"""Add problem admin fields (slug, input_format, output_format, constraints, created_by, status).

Revision ID: a1b2c3d4e5f6
Revises: 3ffe3341c178
Create Date: 2026-03-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "3ffe3341c178"
branch_labels = None
depends_on = None

# PostgreSQL enum for problem status
PROBLEM_STATUS_ENUM = sa.Enum("DRAFT", "PUBLISHED", name="problemstatus")


def upgrade():
    # Create enum type (PostgreSQL)
    PROBLEM_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    # Add new columns to problems (nullable first for existing rows)
    op.add_column("problems", sa.Column("slug", sa.String(length=255), nullable=True))
    op.add_column("problems", sa.Column("input_format", sa.Text(), nullable=True))
    op.add_column("problems", sa.Column("output_format", sa.Text(), nullable=True))
    op.add_column("problems", sa.Column("constraints", sa.Text(), nullable=True))
    op.add_column(
        "problems",
        sa.Column("created_by", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "problems",
        sa.Column("status", PROBLEM_STATUS_ENUM, nullable=True),
    )

    # Backfill existing rows: slug from id, status DRAFT
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE problems SET slug = 'p-' || REPLACE(id::text, '-', ''), status = 'DRAFT' WHERE slug IS NULL"
        )
    )

    # Make slug and status non-nullable
    op.alter_column(
        "problems",
        "slug",
        existing_type=sa.String(255),
        nullable=False,
    )
    op.alter_column(
        "problems",
        "status",
        existing_type=PROBLEM_STATUS_ENUM,
        nullable=False,
        server_default=sa.text("'DRAFT'::problemstatus"),
    )
    op.create_index(op.f("ix_problems_slug"), "problems", ["slug"], unique=False)

    # Unique constraint on title
    op.create_unique_constraint("uq_problems_title", "problems", ["title"])


def downgrade():
    op.drop_constraint("uq_problems_title", "problems", type_="unique")
    op.drop_index(op.f("ix_problems_slug"), table_name="problems")
    op.drop_column("problems", "status")
    op.drop_column("problems", "created_by")
    op.drop_column("problems", "constraints")
    op.drop_column("problems", "output_format")
    op.drop_column("problems", "input_format")
    op.drop_column("problems", "slug")
    PROBLEM_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
