"""Service for aggregating performance data."""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.stream_data import PerformanceData, PerformanceAggregate, StreamDatasetType

logger = logging.getLogger(__name__)


class AggregationService:
    """Service for aggregating performance metrics."""

    def __init__(self, db: Session):
        """Initialize aggregation service."""
        self.db = db

    def aggregate_hourly(self, hours: int = 24) -> List[PerformanceAggregate]:
        """Aggregate performance data by hour."""
        end_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(hours=hours)

        # Get all campaigns with data in the period
        campaigns = (
            self.db.query(
                PerformanceData.campaign_id,
                PerformanceData.dataset_type,
                PerformanceData.profile_id,
            )
            .filter(
                PerformanceData.start_date >= start_time,
                PerformanceData.end_date <= end_time,
            )
            .distinct()
            .all()
        )

        aggregates = []
        for campaign_id, dataset_type, profile_id in campaigns:
            # Aggregate for each hour
            current_hour = start_time
            while current_hour < end_time:
                hour_end = current_hour + timedelta(hours=1)

                # Get all performance data for this hour
                performance_records = (
                    self.db.query(PerformanceData)
                    .filter(
                        PerformanceData.campaign_id == campaign_id,
                        PerformanceData.dataset_type == dataset_type,
                        PerformanceData.start_date >= current_hour,
                        PerformanceData.end_date < hour_end,
                    )
                    .all()
                )

                if performance_records:
                    aggregate = self._create_aggregate(
                        performance_records,
                        "hourly",
                        current_hour,
                        hour_end,
                        campaign_id,
                        dataset_type,
                        profile_id,
                    )
                    if aggregate:
                        aggregates.append(aggregate)

                current_hour = hour_end

        if aggregates:
            self.db.commit()
            logger.info(f"Created {len(aggregates)} hourly aggregates")

        return aggregates

    def aggregate_daily(self, days: int = 7) -> List[PerformanceAggregate]:
        """Aggregate performance data by day."""
        end_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(days=days)

        # Get all campaigns with data in the period
        campaigns = (
            self.db.query(
                PerformanceData.campaign_id,
                PerformanceData.dataset_type,
                PerformanceData.profile_id,
            )
            .filter(
                PerformanceData.start_date >= start_time,
                PerformanceData.end_date <= end_time,
            )
            .distinct()
            .all()
        )

        aggregates = []
        for campaign_id, dataset_type, profile_id in campaigns:
            # Aggregate for each day
            current_day = start_time
            while current_day < end_time:
                day_end = current_day + timedelta(days=1)

                # Get all performance data for this day
                performance_records = (
                    self.db.query(PerformanceData)
                    .filter(
                        PerformanceData.campaign_id == campaign_id,
                        PerformanceData.dataset_type == dataset_type,
                        PerformanceData.start_date >= current_day,
                        PerformanceData.end_date < day_end,
                    )
                    .all()
                )

                if performance_records:
                    aggregate = self._create_aggregate(
                        performance_records,
                        "daily",
                        current_day,
                        day_end,
                        campaign_id,
                        dataset_type,
                        profile_id,
                    )
                    if aggregate:
                        aggregates.append(aggregate)

                current_day = day_end

        if aggregates:
            self.db.commit()
            logger.info(f"Created {len(aggregates)} daily aggregates")

        return aggregates

    def _create_aggregate(
        self,
        performance_records: List[PerformanceData],
        period_type: str,
        period_start: datetime,
        period_end: datetime,
        campaign_id: str,
        dataset_type: StreamDatasetType,
        profile_id: str,
    ) -> PerformanceAggregate:
        """Create an aggregate record from performance records."""
        # Check if aggregate already exists
        existing = (
            self.db.query(PerformanceAggregate)
            .filter(
                PerformanceAggregate.campaign_id == campaign_id,
                PerformanceAggregate.period_type == period_type,
                PerformanceAggregate.period_start == period_start,
            )
            .first()
        )

        if existing:
            return existing

        # Calculate aggregates
        total_impressions = sum(r.impressions for r in performance_records)
        total_clicks = sum(r.clicks for r in performance_records)
        total_cost = sum(r.cost for r in performance_records)
        total_sales = sum(r.sales for r in performance_records)
        total_orders = sum(r.orders for r in performance_records)
        total_units_sold = sum(r.units_sold for r in performance_records)

        # Calculate averages
        valid_records = [r for r in performance_records if r.ctr is not None]
        avg_ctr = (
            sum(r.ctr for r in valid_records) / len(valid_records)
            if valid_records
            else None
        )

        valid_records = [r for r in performance_records if r.cpc is not None]
        avg_cpc = (
            sum(r.cpc for r in valid_records) / len(valid_records)
            if valid_records
            else None
        )

        valid_records = [r for r in performance_records if r.acos is not None]
        avg_acos = (
            sum(r.acos for r in valid_records) / len(valid_records)
            if valid_records
            else None
        )

        valid_records = [r for r in performance_records if r.roas is not None]
        avg_roas = (
            sum(r.roas for r in valid_records) / len(valid_records)
            if valid_records
            else None
        )

        valid_records = [r for r in performance_records if r.conversion_rate is not None]
        avg_conversion_rate = (
            sum(r.conversion_rate for r in valid_records) / len(valid_records)
            if valid_records
            else None
        )

        # Create aggregate record
        aggregate = PerformanceAggregate(
            performance_data_id=performance_records[0].id,  # Reference to first record
            dataset_type=dataset_type,
            profile_id=profile_id,
            campaign_id=campaign_id,
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            total_cost=total_cost,
            total_sales=total_sales,
            total_orders=total_orders,
            total_units_sold=total_units_sold,
            avg_ctr=avg_ctr,
            avg_cpc=avg_cpc,
            avg_acos=avg_acos,
            avg_roas=avg_roas,
            avg_conversion_rate=avg_conversion_rate,
        )

        self.db.add(aggregate)
        self.db.flush()

        return aggregate

