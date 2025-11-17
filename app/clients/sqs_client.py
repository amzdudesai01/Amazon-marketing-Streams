"""SQS client implementation."""
import json
import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from app.clients.base import SQSClientInterface
from app.clients.mock_sqs import MockSQSClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class SQSClient(SQSClientInterface):
    """Real SQS client using boto3."""

    def __init__(self):
        """Initialize SQS client."""
        if not settings.has_aws_credentials or not settings.has_sqs_queue:
            logger.warning(
                "AWS credentials or SQS queue URL not configured. Using mock client."
            )
            self._client = None
            self._mock_client = MockSQSClient()
        else:
            self._client = boto3.client(
                "sqs",
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            self._queue_url = settings.sqs_queue_url
            self._mock_client = None

    def receive_messages(
        self, max_messages: int = 10, wait_time_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """Receive messages from SQS queue."""
        if self._mock_client:
            return self._mock_client.receive_messages(max_messages, wait_time_seconds)

        try:
            response = self._client.receive_message(
                QueueUrl=self._queue_url,
                MaxNumberOfMessages=min(max_messages, 10),
                WaitTimeSeconds=wait_time_seconds,
                MessageAttributeNames=["All"],
            )

            messages = response.get("Messages", [])
            result = []
            for msg in messages:
                try:
                    body = json.loads(msg["Body"])
                    result.append(
                        {
                            "receipt_handle": msg["ReceiptHandle"],
                            "message_id": msg["MessageId"],
                            "body": body,
                            "attributes": msg.get("MessageAttributes", {}),
                        }
                    )
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse message body: {msg.get('Body')}")
                    continue

            return result
        except ClientError as e:
            logger.error(f"Error receiving messages from SQS: {e}")
            return []

    def delete_message(self, receipt_handle: str) -> None:
        """Delete a message from the queue."""
        if self._mock_client:
            return self._mock_client.delete_message(receipt_handle)

        try:
            self._client.delete_message(
                QueueUrl=self._queue_url, ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            logger.error(f"Error deleting message from SQS: {e}")

    def send_message(
        self, message_body: str, message_attributes: Optional[Dict] = None
    ) -> None:
        """Send a message to the queue."""
        if self._mock_client:
            return self._mock_client.send_message(message_body, message_attributes)

        try:
            params = {"QueueUrl": self._queue_url, "MessageBody": message_body}
            if message_attributes:
                params["MessageAttributes"] = message_attributes

            self._client.send_message(**params)
        except ClientError as e:
            logger.error(f"Error sending message to SQS: {e}")

