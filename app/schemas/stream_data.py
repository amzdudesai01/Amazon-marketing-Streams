"""Pydantic schemas for stream data."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class StreamMessageCreate(BaseModel):
    """Schema for creating a stream message."""

    message_id: str
    dataset_type: str  # SP, SB, or SD
    profile_id: str
    raw_data: str


class StreamMessageResponse(BaseModel):
    """Schema for stream message response."""

    id: int
    message_id: str
    dataset_type: str
    profile_id: str
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PerformanceDataCreate(BaseModel):
    """Schema for creating performance data."""

    stream_message_id: int
    dataset_type: str
    profile_id: str
    campaign_id: str
    campaign_name: Optional[str] = None
    ad_group_id: Optional[str] = None
    ad_group_name: Optional[str] = None
    keyword_id: Optional[str] = None
    keyword_text: Optional[str] = None
    asin: Optional[str] = None
    impressions: int = 0
    clicks: int = 0
    cost: Decimal = Decimal("0.00")
    sales: Decimal = Decimal("0.00")
    orders: int = 0
    units_sold: int = 0
    start_date: datetime
    end_date: datetime


class PerformanceDataResponse(BaseModel):
    """Schema for performance data response."""

    id: int
    campaign_id: str
    campaign_name: Optional[str]
    impressions: int
    clicks: int
    cost: Decimal
    sales: Decimal
    orders: int
    units_sold: int
    ctr: Optional[Decimal]
    cpc: Optional[Decimal]
    acos: Optional[Decimal]
    roas: Optional[Decimal]
    conversion_rate: Optional[Decimal]
    start_date: datetime
    end_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PerformanceAggregateResponse(BaseModel):
    """Schema for performance aggregate response."""

    id: int
    campaign_id: str
    period_type: str
    period_start: datetime
    period_end: datetime
    total_impressions: int
    total_clicks: int
    total_cost: Decimal
    total_sales: Decimal
    total_orders: int
    avg_ctr: Optional[Decimal]
    avg_acos: Optional[Decimal]
    avg_roas: Optional[Decimal]

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Schema for creating an alert."""

    alert_type: str
    severity: str
    campaign_id: str
    campaign_name: Optional[str] = None
    profile_id: str
    message: str
    metric_value: Optional[Decimal] = None
    threshold_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None


class AlertResponse(BaseModel):
    """Schema for alert response."""

    id: int
    alert_type: str
    severity: str
    campaign_id: str
    campaign_name: Optional[str]
    message: str
    metric_value: Optional[Decimal]
    threshold_value: Optional[Decimal]
    sent: bool
    created_at: datetime

    class Config:
        from_attributes = True

