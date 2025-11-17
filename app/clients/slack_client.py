"""Slack client implementation."""
import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.clients.base import SlackClientInterface
from app.core.config import settings

logger = logging.getLogger(__name__)


class SlackClient(SlackClientInterface):
    """Slack client using webhook URL."""

    def __init__(self):
        """Initialize Slack client."""
        self.webhook_url = settings.slack_webhook_url
        self.enabled = settings.has_slack_webhook

    def send_message(self, text: str, blocks: Optional[List[Dict]] = None) -> bool:
        """Send a message to Slack."""
        if not self.enabled:
            logger.info(f"[MOCK SLACK] {text}")
            return True

        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error sending message to Slack: {e}")
            return False

    def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        campaign_id: str,
        campaign_name: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an alert to Slack with formatted blocks."""
        severity_colors = {
            "low": "#36a64f",  # Green
            "medium": "#ff9900",  # Orange
            "high": "#ff0000",  # Red
        }

        color = severity_colors.get(severity.lower(), "#808080")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Campaign Alert: {alert_type.upper()}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Campaign ID:*\n`{campaign_id}`",
                    },
                ],
            },
        ]

        if campaign_name:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Campaign:* {campaign_name}",
                    },
                }
            )

        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Message:*\n{message}"},
            }
        )

        if metrics:
            metrics_text = "\n".join(
                [f"• *{k}:* {v}" for k, v in metrics.items()]
            )
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Metrics:*\n{metrics_text}"},
                }
            )

        blocks.append({"type": "divider"})

        payload = {
            "text": f"Campaign Alert: {alert_type}",
            "blocks": blocks,
            "attachments": [{"color": color}],
        }

        if not self.enabled:
            logger.info(f"[MOCK SLACK ALERT]\n{json.dumps(payload, indent=2)}")
            return True

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error sending alert to Slack: {e}")
            return False

