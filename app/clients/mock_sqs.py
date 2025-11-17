"""Mock SQS client for local development."""
import json
import logging
import time
from collections import deque
from typing import Any, Dict, List, Optional

from app.clients.base import SQSClientInterface

logger = logging.getLogger(__name__)


class MockSQSClient(SQSClientInterface):
    """Mock SQS client that uses in-memory queue for local development."""

    def __init__(self):
        """Initialize mock SQS client."""
        self._queue: deque = deque()
        self._processed_messages: set = set()

    def receive_messages(
        self, max_messages: int = 10, wait_time_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """Receive messages from mock queue."""
        messages = []
        start_time = time.time()

        while len(messages) < max_messages:
            if self._queue:
                msg = self._queue.popleft()
                receipt_handle = f"mock_receipt_{len(self._processed_messages)}"
                messages.append(
                    {
                        "receipt_handle": receipt_handle,
                        "message_id": msg.get("message_id", f"mock_msg_{len(messages)}"),
                        "body": msg.get("body", {}),
                        "attributes": msg.get("attributes", {}),
                    }
                )
                self._processed_messages.add(receipt_handle)
            elif time.time() - start_time < wait_time_seconds:
                time.sleep(0.1)  # Small delay to simulate waiting
            else:
                break

        return messages

    def delete_message(self, receipt_handle: str) -> None:
        """Delete a message from mock queue."""
        if receipt_handle in self._processed_messages:
            self._processed_messages.remove(receipt_handle)
            logger.debug(f"Deleted mock message: {receipt_handle}")

    def send_message(
        self, message_body: str, message_attributes: Optional[Dict] = None
    ) -> None:
        """Add a message to mock queue."""
        try:
            body = json.loads(message_body) if isinstance(message_body, str) else message_body
            self._queue.append(
                {
                    "body": body,
                    "attributes": message_attributes or {},
                    "message_id": f"mock_{int(time.time() * 1000)}",
                }
            )
            logger.debug(f"Added message to mock queue: {len(self._queue)} messages")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message body: {message_body}")

    def add_sample_message(self, message: Dict[str, Any]) -> None:
        """Helper method to add sample messages for testing."""
        self.send_message(json.dumps(message))

