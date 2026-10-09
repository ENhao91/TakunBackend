"""Add missing category and video metadata columns.

Revision ID: 20261009_add_missing_fields
Revises: 20261009_initial
Create Date: 2026-10-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20261009_add_missing_fields"
down_revision = "20261009_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "category" in table_names:
        category_columns = {col["name"] for col in inspector.get_columns("category")}
        if "sort_order" not in category_columns:
            op.add_column("category", sa.Column("sort_order", sa.Integer(), nullable=True))
        if "created_at" not in category_columns:
            op.add_column("category", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
        if "updated_at" not in category_columns:
            op.add_column("category", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

        op.execute(sa.text("UPDATE category SET sort_order = id WHERE sort_order IS NULL"))
        op.execute(sa.text("UPDATE category SET created_at = NOW() WHERE created_at IS NULL"))
        op.execute(sa.text("UPDATE category SET updated_at = NOW() WHERE updated_at IS NULL"))

        with op.batch_alter_table("category") as batch_op:
            batch_op.alter_column("category_name", existing_type=sa.Text(), nullable=False)
            batch_op.alter_column("sort_order", existing_type=sa.Integer(), nullable=False)
            batch_op.alter_column("created_at", existing_type=sa.DateTime(timezone=True), nullable=False)
            batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)

    if "videos" in table_names:
        video_columns = {col["name"] for col in inspector.get_columns("videos")}
        if "sort_order" not in video_columns:
            op.add_column("videos", sa.Column("sort_order", sa.Integer(), nullable=True))
            op.execute(sa.text("UPDATE videos SET sort_order = id WHERE sort_order IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("sort_order", existing_type=sa.Integer(), nullable=False)
        if "created_at" not in video_columns:
            op.add_column("videos", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
            op.execute(sa.text("UPDATE videos SET created_at = NOW() WHERE created_at IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("created_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        if "updated_at" not in video_columns:
            op.add_column("videos", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
            op.execute(sa.text("UPDATE videos SET updated_at = NOW() WHERE updated_at IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "category" in inspector.get_table_names():
        category_columns = {col["name"] for col in inspector.get_columns("category")}
        if "sort_order" in category_columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("sort_order")
        if "created_at" in category_columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("created_at")
        if "updated_at" in category_columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("updated_at")

    if "videos" in inspector.get_table_names():
        video_columns = {col["name"] for col in inspector.get_columns("videos")}
        if "sort_order" in video_columns:
            with op.batch_alter_table("videos") as batch_op:
                batch_op.drop_column("sort_order")
        if "created_at" in video_columns:
            with op.batch_alter_table("videos") as batch_op:
                batch_op.drop_column("created_at")
        if "updated_at" in video_columns:
            with op.batch_alter_table("videos") as batch_op:
                batch_op.drop_column("updated_at")
