"""Service for processing stream messages."""
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.stream_data import (
    StreamMessage,
    PerformanceData,
    StreamDatasetType,
    BudgetUsageEvent,
)
from app.utils.metrics_calculator import MetricsCalculator

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Processes Amazon Marketing Stream messages."""

    def __init__(self, db: Session):
        """Initialize message processor."""
        self.db = db
        self.metrics_calculator = MetricsCalculator()

    def process_message(
        self, message_body: Dict[str, Any]
    ) -> Optional[PerformanceData]:
        """Process a single stream message."""
        try:
            # Extract message metadata
            message_id = self._get_first_value(
                message_body,
                "messageId",
                "id",
                "idempotency_id",
                "idempotencyId",
            )
            dataset_type_str = self._get_first_value(
                message_body, "datasetType", "dataset_type", "dataset_id"
            )
            dataset_name = self._normalize_dataset_name(dataset_type_str)
            profile_id = self._get_first_value(
                message_body, "profileId", "profile_id", "advertiser_id"
            )

            if not all([message_id, dataset_type_str, profile_id]):
                logger.warning(f"Missing required fields in message: {message_body}")
                return None

            # Determine dataset type
            try:
                dataset_type = self._map_dataset_type(dataset_name or dataset_type_str)
            except ValueError:
                logger.warning(f"Unknown dataset type: {dataset_type_str}")
                return None

            # Check if message already processed
            existing = (
                self.db.query(StreamMessage)
                .filter(StreamMessage.message_id == message_id)
                .first()
            )
            if existing:
                logger.debug(f"Message already processed: {message_id}")
                return None

            # Store raw message
            stream_message = StreamMessage(
                message_id=message_id,
                dataset_type=dataset_type,
                dataset_name=dataset_name,
                profile_id=profile_id,
                raw_data=json.dumps(message_body),
                processed=False,
            )
            self.db.add(stream_message)
            self.db.flush()

            result_obj = None
            if dataset_name and "budget" in dataset_name:
                result_obj = self._extract_budget_usage(
                    stream_message, message_body, dataset_name
                )
            else:
                result_obj = self._extract_performance_data(
                    stream_message, message_body, dataset_name
                )

            if result_obj:
                stream_message.processed = True
                stream_message.processed_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"Processed message {message_id}")
                return (
                    result_obj
                    if isinstance(result_obj, PerformanceData)
                    else None
                )
            else:
                self.db.rollback()
                logger.warning(f"Failed to extract performance data from message {message_id}")
                return None

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self.db.rollback()
            return None

    def _extract_performance_data(
        self,
        stream_message: StreamMessage,
        message_body: Dict[str, Any],
        dataset_name: Optional[str],
    ) -> Optional[PerformanceData]:
        """Extract performance data from message body."""
        try:
            data = (
                message_body.get("data")
                or message_body.get("payload")
                or message_body
            )

            # Extract campaign information
            campaign_id = self._get_first_value(
                data,
                "campaignId",
                "campaign_id",
                ("campaign", "id"),
            )
            if not campaign_id:
                logger.warning("No campaign ID found in message")
                return None

            campaign_name = self._get_first_value(
                data,
                "campaignName",
                "campaign_name",
                ("campaign", "name"),
            )

            # Extract metrics
            impressions = int(self._get_first_value(data, "impressions") or 0)
            clicks = int(self._get_first_value(data, "clicks") or 0)
            cost = Decimal(
                str(self._get_first_value(data, "cost", "spend", "ad_cost") or 0)
            )
            sales = Decimal(
                str(
                    self._get_first_value(
                        data,
                        "sales",
                        "revenue",
                        "attributed_sales_1d",
                        "attributed_sales_7d",
                    )
                    or 0
                )
            )
            orders = int(
                self._get_first_value(
                    data, "orders", "conversions", "attributed_conversions_1d"
                )
                or 0
            )
            units_sold = int(
                self._get_first_value(
                    data, "unitsSold", "units_sold", "attributed_units_ordered_1d"
                )
                or 0
            )

            # Extract time period
            start_date_str = self._get_first_value(
                data,
                "time_window_start",
                "startDate",
                "start_date",
                "date",
                ("period", "start"),
            )
            end_date_str = self._get_first_value(
                data,
                "time_window_end",
                "endDate",
                "end_date",
                ("period", "end"),
            )

            # Parse dates (assuming ISO format)
            try:
                start_date = (
                    datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                    if start_date_str
                    else datetime.utcnow()
                )
                end_date = (
                    datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                    if end_date_str
                    else datetime.utcnow()
                )
            except (ValueError, AttributeError):
                start_date = datetime.utcnow()
                end_date = datetime.utcnow()

            # Create performance data record
            performance_data = PerformanceData(
                stream_message_id=stream_message.id,
                dataset_type=stream_message.dataset_type,
                dataset_name=dataset_name,
                profile_id=stream_message.profile_id,
                campaign_id=str(campaign_id),
                campaign_name=campaign_name,
                ad_group_id=self._get_first_value(
                    data,
                    "adGroupId",
                    "ad_group_id",
                    ("ad_group", "id"),
                ),
                ad_group_name=self._get_first_value(
                    data,
                    "adGroupName",
                    "ad_group_name",
                    ("ad_group", "name"),
                ),
                keyword_id=self._get_first_value(data, "keywordId", "keyword_id"),
                keyword_text=self._get_first_value(
                    data, "keywordText", "keyword_text", "search_term"
                ),
                asin=self._get_first_value(data, "asin", "ASIN", ("product", "asin")),
                impressions=impressions,
                clicks=clicks,
                cost=cost,
                sales=sales,
                orders=orders,
                units_sold=units_sold,
                start_date=start_date,
                end_date=end_date,
            )

            # Calculate metrics
            metrics = self.metrics_calculator.calculate_metrics(performance_data)
            performance_data.ctr = metrics.get("ctr")
            performance_data.cpc = metrics.get("cpc")
            performance_data.acos = metrics.get("acos")
            performance_data.roas = metrics.get("roas")
            performance_data.conversion_rate = metrics.get("conversion_rate")

            self.db.add(performance_data)
            self.db.flush()

            return performance_data

        except Exception as e:
            logger.error(
                f"Error extracting performance data: {e}", exc_info=True
            )
            return None

    def _extract_budget_usage(
        self,
        stream_message: StreamMessage,
        message_body: Dict[str, Any],
        dataset_name: Optional[str],
    ) -> Optional[BudgetUsageEvent]:
        """Extract budget usage information."""
        try:
            data = (
                message_body.get("data")
                or message_body.get("payload")
                or message_body
            )

            campaign_id = self._get_first_value(
                data, "campaignId", "campaign_id", ("campaign", "id")
            )
            budget_type = self._get_first_value(
                data, "budgetType", "budget_type"
            )
            budget_name = self._get_first_value(
                data, "budgetName", "budget_name"
            )
            budget_status = self._get_first_value(
                data, "budgetStatus", "budget_status", "status"
            )
            currency = self._get_first_value(
                data, "currency", "currencyCode", "currency_code"
            )
            daily_budget = Decimal(
                str(
                    self._get_first_value(
                        data,
                        "dailyBudget",
                        "budget",
                        "budgetLimit",
                        "budget_limit",
                        "maxBudget",
                        "max_budget",
                    )
                    or 0
                )
            )
            budget_consumed = Decimal(
                str(
                    self._get_first_value(
                        data,
                        "budgetConsumed",
                        "budget_consumed",
                        "amountSpent",
                        "amount_spent",
                        "spend",
                    )
                    or 0
                )
            )

            start_date = self._parse_datetime(
                self._get_first_value(
                    data,
                    "time_window_start",
                    "startDate",
                    "start_date",
                    "date",
                )
            )
            end_date = self._parse_datetime(
                self._get_first_value(
                    data,
                    "time_window_end",
                    "endDate",
                    "end_date",
                )
            )

            budget_event = BudgetUsageEvent(
                stream_message_id=stream_message.id,
                dataset_type=stream_message.dataset_type,
                dataset_name=dataset_name,
                profile_id=stream_message.profile_id,
                campaign_id=str(campaign_id) if campaign_id else None,
                budget_type=budget_type,
                budget_name=budget_name,
                budget_status=budget_status,
                daily_budget=daily_budget,
                budget_consumed=budget_consumed,
                currency=currency,
                start_date=start_date,
                end_date=end_date,
                details=json.dumps(data),
            )

            self.db.add(budget_event)
            self.db.flush()
            return budget_event
        except Exception as exc:
            logger.error(
                f"Error extracting budget usage data: {exc}", exc_info=True
            )
            return None

    @staticmethod
    def _get_first_value(data: Dict[str, Any], *keys):
        """Return first non-null value for provided keys. Supports tuple paths."""
        for key in keys:
            if key is None:
                continue
            if isinstance(key, tuple):
                current = data
                for part in key:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        current = None
                        break
                if current is not None:
                    return current
            elif isinstance(data, dict) and key in data and data[key] is not None:
                return data[key]
        return None

    @staticmethod
    def _map_dataset_type(raw_value: str) -> StreamDatasetType:
        """Map dataset id/name to StreamDatasetType."""
        if not raw_value:
            raise ValueError("Dataset type missing")

        normalized = raw_value.strip().lower()

        if normalized.startswith("sp"):
            return StreamDatasetType.SP
        if normalized.startswith("sb"):
            return StreamDatasetType.SB
        if normalized.startswith("sd"):
            return StreamDatasetType.SD

        # allow direct enum names (SP/SB/SD)
        return StreamDatasetType(normalized.upper())

    @staticmethod
    def _normalize_dataset_name(raw_value: Optional[str]) -> Optional[str]:
        """Normalize dataset id/name for consistent comparisons."""
        if not raw_value:
            return None
        return raw_value.strip().lower()

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime strings safely."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

