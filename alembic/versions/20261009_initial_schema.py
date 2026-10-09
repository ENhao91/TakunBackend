"""Initial schema for categories and videos.

Revision ID: 20261009_initial
Revises: 
Create Date: 2026-10-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20261009_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "category" not in tables:
        op.create_table(
            "category",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("category_name", sa.String(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
    else:
        columns = {col["name"] for col in inspector.get_columns("category")}
        if "sort_order" not in columns:
            op.add_column("category", sa.Column("sort_order", sa.Integer(), nullable=True))
        if "created_at" not in columns:
            op.add_column("category", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
        if "updated_at" not in columns:
            op.add_column("category", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

        op.execute(sa.text("UPDATE category SET category_name = '未命名分類' WHERE category_name IS NULL OR TRIM(category_name) = ''"))
        op.execute(sa.text("UPDATE category SET sort_order = id WHERE sort_order IS NULL"))
        op.execute(sa.text("UPDATE category SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
        op.execute(sa.text("UPDATE category SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))

        with op.batch_alter_table("category") as batch_op:
            batch_op.alter_column("category_name", existing_type=sa.String(), nullable=False)
            batch_op.alter_column("sort_order", existing_type=sa.Integer(), nullable=False)
            batch_op.alter_column("created_at", existing_type=sa.DateTime(timezone=True), nullable=False)
            batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)

    if "videos" not in tables:
        op.create_table(
            "videos",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("category_id", sa.Integer(), sa.ForeignKey("category.id"), nullable=True),
            sa.Column("drive_file_id", sa.String(), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index(op.f("ix_videos_category_id"), "videos", ["category_id"], unique=False, if_not_exists=True)
    else:
        video_columns = {col["name"] for col in inspector.get_columns("videos")}
        if "sort_order" not in video_columns:
            op.add_column("videos", sa.Column("sort_order", sa.Integer(), nullable=True))
            op.execute(sa.text("UPDATE videos SET sort_order = id WHERE sort_order IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("sort_order", existing_type=sa.Integer(), nullable=False)
        if "created_at" not in video_columns:
            op.add_column("videos", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True))
            op.execute(sa.text("UPDATE videos SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("created_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        if "updated_at" not in video_columns:
            op.add_column("videos", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
            op.execute(sa.text("UPDATE videos SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        if "drive_file_id" not in video_columns:
            op.add_column("videos", sa.Column("drive_file_id", sa.String(), nullable=True))
            op.execute(sa.text("UPDATE videos SET drive_file_id = 'unknown' WHERE drive_file_id IS NULL"))
            with op.batch_alter_table("videos") as batch_op:
                batch_op.alter_column("drive_file_id", existing_type=sa.String(), nullable=False)
        op.create_index(op.f("ix_videos_category_id"), "videos", ["category_id"], unique=False, if_not_exists=True)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "videos" in inspector.get_table_names():
        op.drop_table("videos")
    if "category" in inspector.get_table_names():
        # Keep existing category data intact for safety; only drop the added columns if they are newer than initial state.
        columns = {col["name"] for col in inspector.get_columns("category")}
        if "sort_order" in columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("sort_order")
        if "created_at" in columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("created_at")
        if "updated_at" in columns:
            with op.batch_alter_table("category") as batch_op:
                batch_op.drop_column("updated_at")
