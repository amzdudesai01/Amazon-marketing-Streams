"""Add dataset_name columns and budget usage table."""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    stream_enum = postgresql.ENUM(
        "SP", "SB", "SD", name="streamdatasettype", create_type=False
    )
    op.add_column(
        "stream_messages",
        sa.Column("dataset_name", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_stream_messages_dataset_name"),
        "stream_messages",
        ["dataset_name"],
        unique=False,
    )

    op.add_column(
        "performance_data",
        sa.Column("dataset_name", sa.String(length=255), nullable=True),
    )
    op.create_index(
        op.f("ix_performance_data_dataset_name"),
        "performance_data",
        ["dataset_name"],
        unique=False,
    )

    op.create_table(
        "budget_usage_events",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("stream_message_id", sa.BigInteger(), nullable=False),
        sa.Column("dataset_type", stream_enum, nullable=False),
        sa.Column("dataset_name", sa.String(length=255), nullable=True),
        sa.Column("profile_id", sa.String(length=255), nullable=False),
        sa.Column("campaign_id", sa.String(length=255), nullable=True),
        sa.Column("budget_type", sa.String(length=255), nullable=True),
        sa.Column("budget_name", sa.String(length=500), nullable=True),
        sa.Column("budget_status", sa.String(length=255), nullable=True),
        sa.Column("daily_budget", sa.Numeric(12, 2), nullable=True),
        sa.Column("budget_consumed", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["stream_message_id"],
            ["stream_messages.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_budget_usage_events_stream_message_id"),
        "budget_usage_events",
        ["stream_message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_budget_usage_events_dataset_name"),
        "budget_usage_events",
        ["dataset_name"],
        unique=False,
    )
    op.create_index(
        op.f("ix_budget_usage_events_dataset_type"),
        "budget_usage_events",
        ["dataset_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_budget_usage_events_profile_id"),
        "budget_usage_events",
        ["profile_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_budget_usage_events_campaign_id"),
        "budget_usage_events",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_budget_usage_events_start_date"),
        "budget_usage_events",
        ["start_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_budget_usage_events_start_date"), table_name="budget_usage_events")
    op.drop_index(op.f("ix_budget_usage_events_campaign_id"), table_name="budget_usage_events")
    op.drop_index(op.f("ix_budget_usage_events_profile_id"), table_name="budget_usage_events")
    op.drop_index(op.f("ix_budget_usage_events_dataset_type"), table_name="budget_usage_events")
    op.drop_index(op.f("ix_budget_usage_events_dataset_name"), table_name="budget_usage_events")
    op.drop_index(op.f("ix_budget_usage_events_stream_message_id"), table_name="budget_usage_events")
    op.drop_table("budget_usage_events")

    op.drop_index(op.f("ix_performance_data_dataset_name"), table_name="performance_data")
    op.drop_column("performance_data", "dataset_name")

    op.drop_index(op.f("ix_stream_messages_dataset_name"), table_name="stream_messages")
    op.drop_column("stream_messages", "dataset_name")

