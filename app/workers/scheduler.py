"""Scheduler for background tasks."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.workers.sqs_worker import SQSWorker
from app.workers.aggregation_worker import AggregationWorker

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler = None
_sqs_worker: SQSWorker = None
_aggregation_worker: AggregationWorker = None


def start_scheduler():
    """Start the background scheduler."""
    global _scheduler, _sqs_worker, _aggregation_worker

    if _scheduler and _scheduler.running:
        logger.warning("Scheduler is already running")
        return

    _scheduler = BackgroundScheduler()
    _sqs_worker = SQSWorker()
    _aggregation_worker = AggregationWorker()

    # Schedule SQS polling
    _scheduler.add_job(
        func=_sqs_worker.process_messages,
        trigger=IntervalTrigger(seconds=settings.sqs_poll_interval_seconds),
        id="sqs_poller",
        name="SQS Message Poller",
        replace_existing=True,
    )

    # Schedule hourly aggregation (runs every hour)
    _scheduler.add_job(
        func=_aggregation_worker.aggregate_hourly,
        trigger=IntervalTrigger(hours=1),
        id="hourly_aggregation",
        name="Hourly Performance Aggregation",
        replace_existing=True,
    )

    # Schedule daily aggregation (runs once per day at midnight)
    _scheduler.add_job(
        func=_aggregation_worker.aggregate_daily,
        trigger=IntervalTrigger(days=1),
        id="daily_aggregation",
        name="Daily Performance Aggregation",
        replace_existing=True,
    )

    _scheduler.start()
    _sqs_worker.start()
    logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler, _sqs_worker, _aggregation_worker

    if _sqs_worker:
        _sqs_worker.stop()

    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.info("Background scheduler stopped")

