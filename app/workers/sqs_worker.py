"""SQS worker for processing messages."""
import logging
from typing import List

from sqlalchemy.orm import Session

from app.clients.sqs_client import SQSClient
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.alert_service import AlertService
from app.services.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class SQSWorker:
    """Worker that polls SQS and processes messages."""

    def __init__(self):
        """Initialize SQS worker."""
        self.sqs_client = SQSClient()
        self.running = False

    def process_messages(self) -> int:
        """Process messages from SQS queue."""
        if not settings.worker_enabled:
            logger.debug("Worker is disabled")
            return 0

        try:
            messages = self.sqs_client.receive_messages(
                max_messages=settings.max_messages_per_poll,
                wait_time_seconds=settings.sqs_poll_interval_seconds,
            )

            if not messages:
                return 0

            processed_count = 0
            db: Session = SessionLocal()

            try:
                processor = MessageProcessor(db)
                alert_service = AlertService(db)

                for message in messages:
                    try:
                        # Process message
                        performance_data = processor.process_message(message["body"])

                        if performance_data:
                            # Check for alerts
                            alert_service.check_and_create_alerts(performance_data)
                            processed_count += 1

                        # Delete message from queue
                        self.sqs_client.delete_message(message["receipt_handle"])

                    except Exception as e:
                        logger.error(
                            f"Error processing message {message.get('message_id')}: {e}",
                            exc_info=True,
                        )
                        # Don't delete message on error - let it be retried

            finally:
                db.close()

            if processed_count > 0:
                logger.info(f"Processed {processed_count} messages from SQS")

            return processed_count

        except Exception as e:
            logger.error(f"Error in SQS worker: {e}", exc_info=True)
            return 0

    def start(self):
        """Start the worker (for continuous operation)."""
        self.running = True
        logger.info("SQS worker started")

    def stop(self):
        """Stop the worker."""
        self.running = False
        logger.info("SQS worker stopped")

