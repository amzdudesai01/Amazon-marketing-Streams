"""Metrics and performance data endpoints."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.stream_data import PerformanceData, PerformanceAggregate, Alert
from app.schemas.stream_data import (
    PerformanceDataResponse,
    PerformanceAggregateResponse,
    AlertResponse,
)

router = APIRouter()


@router.get("/metrics/campaigns/{campaign_id}", response_model=list[PerformanceDataResponse])
async def get_campaign_metrics(
    campaign_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """Get performance metrics for a specific campaign."""
    query = db.query(PerformanceData).filter(PerformanceData.campaign_id == campaign_id)

    if start_date:
        query = query.filter(PerformanceData.start_date >= start_date)
    if end_date:
        query = query.filter(PerformanceData.end_date <= end_date)

    results = query.order_by(PerformanceData.start_date.desc()).limit(100).all()
    return results


@router.get("/metrics/aggregates", response_model=list[PerformanceAggregateResponse])
async def get_aggregates(
    campaign_id: Optional[str] = Query(None),
    period_type: str = Query("daily", regex="^(hourly|daily)$"),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
):
    """Get aggregated performance metrics."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    query = db.query(PerformanceAggregate).filter(
        PerformanceAggregate.period_type == period_type,
        PerformanceAggregate.period_start >= start_date,
        PerformanceAggregate.period_end <= end_date,
    )

    if campaign_id:
        query = query.filter(PerformanceAggregate.campaign_id == campaign_id)

    results = query.order_by(PerformanceAggregate.period_start.desc()).all()
    return results


@router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(
    campaign_id: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    sent: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get alert history."""
    query = db.query(Alert)

    if campaign_id:
        query = query.filter(Alert.campaign_id == campaign_id)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if sent is not None:
        query = query.filter(Alert.sent == sent)

    results = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return results

