"""Database models for Amazon Marketing Stream data."""
from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class StreamDatasetType(str, PyEnum):
    """Enum for stream dataset types."""

    SP = "SP"  # Sponsored Products
    SB = "SB"  # Sponsored Brands
    SD = "SD"  # Sponsored Display


class StreamMessage(Base):
    """Raw stream message from Amazon Marketing Stream."""

    __tablename__ = "stream_messages"

    id = Column(BigInteger, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    dataset_type = Column(Enum(StreamDatasetType), nullable=False, index=True)
    dataset_name = Column(String(255), nullable=True, index=True)
    profile_id = Column(String(255), nullable=False, index=True)
    raw_data = Column(Text, nullable=False)  # JSON string
    processed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    performance_data = relationship("PerformanceData", back_populates="stream_message")


class PerformanceData(Base):
    """Processed performance metrics from stream messages."""

    __tablename__ = "performance_data"

    id = Column(BigInteger, primary_key=True, index=True)
    stream_message_id = Column(
        BigInteger, ForeignKey("stream_messages.id"), nullable=False, index=True
    )
    dataset_type = Column(Enum(StreamDatasetType), nullable=False, index=True)
    dataset_name = Column(String(255), nullable=True, index=True)
    profile_id = Column(String(255), nullable=False, index=True)
    campaign_id = Column(String(255), nullable=False, index=True)
    campaign_name = Column(String(500), nullable=True)
    ad_group_id = Column(String(255), nullable=True, index=True)
    ad_group_name = Column(String(500), nullable=True)
    keyword_id = Column(String(255), nullable=True, index=True)
    keyword_text = Column(String(500), nullable=True)
    asin = Column(String(20), nullable=True, index=True)

    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    cost = Column(Numeric(10, 2), default=Decimal("0.00"))
    sales = Column(Numeric(10, 2), default=Decimal("0.00"))
    orders = Column(Integer, default=0)
    units_sold = Column(Integer, default=0)

    # Calculated metrics
    ctr = Column(Numeric(5, 4), nullable=True)  # Click-through rate
    cpc = Column(Numeric(10, 4), nullable=True)  # Cost per click
    acos = Column(Numeric(5, 4), nullable=True)  # Advertising Cost of Sales
    roas = Column(Numeric(10, 4), nullable=True)  # Return on Ad Spend
    conversion_rate = Column(Numeric(5, 4), nullable=True)

    # Time period
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    stream_message = relationship("StreamMessage", back_populates="performance_data")
    aggregates = relationship("PerformanceAggregate", back_populates="performance_data")

    # Indexes for common queries
    __table_args__ = (
        Index("idx_performance_campaign_date", "campaign_id", "start_date"),
        Index("idx_performance_profile_date", "profile_id", "start_date"),
    )


class PerformanceAggregate(Base):
    """Hourly and daily aggregated performance metrics."""

    __tablename__ = "performance_aggregates"

    id = Column(BigInteger, primary_key=True, index=True)
    performance_data_id = Column(
        BigInteger, ForeignKey("performance_data.id"), nullable=False, index=True
    )
    dataset_type = Column(Enum(StreamDatasetType), nullable=False, index=True)
    profile_id = Column(String(255), nullable=False, index=True)
    campaign_id = Column(String(255), nullable=False, index=True)

    # Aggregation period
    period_type = Column(String(20), nullable=False, index=True)  # 'hourly' or 'daily'
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Aggregated metrics
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    total_cost = Column(Numeric(10, 2), default=Decimal("0.00"))
    total_sales = Column(Numeric(10, 2), default=Decimal("0.00"))
    total_orders = Column(Integer, default=0)
    total_units_sold = Column(Integer, default=0)

    # Aggregated calculated metrics
    avg_ctr = Column(Numeric(5, 4), nullable=True)
    avg_cpc = Column(Numeric(10, 4), nullable=True)
    avg_acos = Column(Numeric(5, 4), nullable=True)
    avg_roas = Column(Numeric(10, 4), nullable=True)
    avg_conversion_rate = Column(Numeric(5, 4), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    performance_data = relationship("PerformanceData", back_populates="aggregates")

    # Unique constraint to prevent duplicate aggregates
    __table_args__ = (
        Index(
            "idx_aggregate_unique",
            "campaign_id",
            "period_type",
            "period_start",
            unique=True,
        ),
    )


class Alert(Base):
    """Alert records for performance threshold breaches."""

    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # 'ctr_drop', 'spend_spike', etc.
    severity = Column(String(20), nullable=False, index=True)  # 'low', 'medium', 'high'
    campaign_id = Column(String(255), nullable=False, index=True)
    campaign_name = Column(String(500), nullable=True)
    profile_id = Column(String(255), nullable=False, index=True)

    # Alert details
    message = Column(Text, nullable=False)
    metric_value = Column(Numeric(10, 4), nullable=True)
    threshold_value = Column(Numeric(10, 4), nullable=True)
    previous_value = Column(Numeric(10, 4), nullable=True)

    # Status
    sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class BudgetUsageEvent(Base):
    """Budget usage data streamed from AMS."""

    __tablename__ = "budget_usage_events"

    id = Column(BigInteger, primary_key=True, index=True)
    stream_message_id = Column(
        BigInteger, ForeignKey("stream_messages.id"), nullable=False, index=True
    )
    dataset_type = Column(Enum(StreamDatasetType), nullable=False, index=True)
    dataset_name = Column(String(255), nullable=True, index=True)
    profile_id = Column(String(255), nullable=False, index=True)
    campaign_id = Column(String(255), nullable=True, index=True)
    budget_type = Column(String(255), nullable=True)
    budget_name = Column(String(500), nullable=True)
    budget_status = Column(String(255), nullable=True)
    daily_budget = Column(Numeric(12, 2), default=Decimal("0.00"))
    budget_consumed = Column(Numeric(12, 2), default=Decimal("0.00"))
    currency = Column(String(10), nullable=True)
    start_date = Column(DateTime, nullable=True, index=True)
    end_date = Column(DateTime, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    stream_message = relationship("StreamMessage")

