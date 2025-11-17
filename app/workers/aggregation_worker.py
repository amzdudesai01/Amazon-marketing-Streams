"""Worker for aggregating performance data."""
import logging

from app.core.database import SessionLocal
from app.services.aggregation_service import AggregationService

logger = logging.getLogger(__name__)


class AggregationWorker:
    """Worker that aggregates performance data."""

    def aggregate_hourly(self):
        """Run hourly aggregation."""
        db = SessionLocal()
        try:
            service = AggregationService(db)
            service.aggregate_hourly(hours=24)
        except Exception as e:
            logger.error(f"Error in hourly aggregation: {e}", exc_info=True)
        finally:
            db.close()

    def aggregate_daily(self):
        """Run daily aggregation."""
        db = SessionLocal()
        try:
            service = AggregationService(db)
            service.aggregate_daily(days=7)
        except Exception as e:
            logger.error(f"Error in daily aggregation: {e}", exc_info=True)
        finally:
            db.close()

