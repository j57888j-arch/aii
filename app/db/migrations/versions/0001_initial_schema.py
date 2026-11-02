"""Initial StudyHelper identity and onboarding schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("language", sa.String(length=2), server_default=sa.text("'uz'"), nullable=False),
        sa.Column("default_mode", sa.String(length=32), server_default=sa.text("'chat'"), nullable=False),
        sa.Column("timezone", sa.String(length=64), server_default=sa.text("'Asia/Tashkent'"), nullable=False),
        sa.Column("referral_code", sa.String(length=24), nullable=False),
        sa.Column("referred_by_id", sa.Integer(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("incognito", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("onboarding_goal", sa.String(length=24), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["referred_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
        sa.UniqueConstraint("referral_code", name="uq_users_referral_code"),
    )
    op.create_index("ix_users_referred_by_id", "users", ["referred_by_id"])
    op.create_index("ix_users_created_at", "users", ["created_at"])
    op.create_index("ix_users_last_seen_at", "users", ["last_seen_at"])


def downgrade() -> None:
    op.drop_index("ix_users_last_seen_at", table_name="users")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_index("ix_users_referred_by_id", table_name="users")
    op.drop_table("users")
