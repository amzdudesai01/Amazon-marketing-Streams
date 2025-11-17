"""Base client interface for external services."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SQSClientInterface(ABC):
    """Interface for SQS client operations."""

    @abstractmethod
    def receive_messages(
        self, max_messages: int = 10, wait_time_seconds: int = 5
    ) -> List[Dict[str, Any]]:
        """Receive messages from SQS queue."""
        pass

    @abstractmethod
    def delete_message(self, receipt_handle: str) -> None:
        """Delete a message from the queue."""
        pass

    @abstractmethod
    def send_message(self, message_body: str, message_attributes: Optional[Dict] = None) -> None:
        """Send a message to the queue."""
        pass


class SlackClientInterface(ABC):
    """Interface for Slack client operations."""

    @abstractmethod
    def send_message(self, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Send a message to Slack."""
        pass

    @abstractmethod
    def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        campaign_id: str,
        campaign_name: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an alert to Slack."""
        pass

