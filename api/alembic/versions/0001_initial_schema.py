"""initial schema — books, tags, book_tags, loans, label_templates

Revision ID: 0001
Revises: None
Create Date: 2026-05-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("isbn_13", sa.String(13), nullable=True),
        sa.Column("isbn_10", sa.String(10), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("subtitle", sa.Text(), nullable=True),
        sa.Column(
            "authors",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("publisher", sa.Text(), nullable=True),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("pages", sa.Integer(), nullable=True),
        sa.Column("cover_url", sa.Text(), nullable=True),
        sa.Column("dewey_code", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_books_isbn_13", "books", ["isbn_13"])

    op.create_table(
        "tags",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "color", sa.String(7), nullable=False, server_default=sa.text("'#6366f1'")
        ),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "book_tags",
        sa.Column(
            "book_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tags.id", ondelete="RESTRICT"),
            primary_key=True,
        ),
    )

    op.create_table(
        "loans",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "book_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("books.id"),
            nullable=False,
        ),
        sa.Column("borrower_name", sa.Text(), nullable=False),
        sa.Column(
            "loaned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "label_templates",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("width_mm", sa.Float(), nullable=False, server_default=sa.text("50.0")),
        sa.Column(
            "height_mm", sa.Float(), nullable=False, server_default=sa.text("30.0")
        ),
        sa.Column("font_size", sa.Integer(), nullable=False, server_default=sa.text("8")),
        sa.Column("show_dewey", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("show_title", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "show_barcode", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("label_templates")
    op.drop_table("loans")
    op.drop_table("book_tags")
    op.drop_table("tags")
    op.drop_index("ix_books_isbn_13", table_name="books")
    op.drop_table("books")
