"""Service for detecting and sending alerts."""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.clients.slack_client import SlackClient
from app.core.config import settings
from app.models.stream_data import Alert, PerformanceData, PerformanceAggregate

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing performance alerts."""

    def __init__(self, db: Session):
        """Initialize alert service."""
        self.db = db
        self.slack_client = SlackClient()

    def check_and_create_alerts(
        self, performance_data: PerformanceData
    ) -> List[Alert]:
        """Check performance data against thresholds and create alerts."""
        alerts = []

        # Check CTR drop
        ctr_alert = self._check_ctr_drop(performance_data)
        if ctr_alert:
            alerts.append(ctr_alert)

        # Check spend spike
        spend_alert = self._check_spend_spike(performance_data)
        if spend_alert:
            alerts.append(spend_alert)

        # Check ACOS threshold
        acos_alert = self._check_acos_threshold(performance_data)
        if acos_alert:
            alerts.append(acos_alert)

        # Check ROAS threshold
        roas_alert = self._check_roas_threshold(performance_data)
        if roas_alert:
            alerts.append(roas_alert)

        # Send alerts to Slack
        for alert in alerts:
            self._send_alert(alert)

        return alerts

    def _check_ctr_drop(self, performance_data: PerformanceData) -> Optional[Alert]:
        """Check if CTR has dropped significantly."""
        if not performance_data.ctr:
            return None

        # Get previous CTR for comparison (last 24 hours)
        previous_period_start = performance_data.start_date - timedelta(hours=24)
        previous_data = (
            self.db.query(PerformanceData)
            .filter(
                PerformanceData.campaign_id == performance_data.campaign_id,
                PerformanceData.start_date >= previous_period_start,
                PerformanceData.start_date < performance_data.start_date,
            )
            .order_by(PerformanceData.start_date.desc())
            .first()
        )

        if not previous_data or not previous_data.ctr:
            return None

        ctr_change = (performance_data.ctr - previous_data.ctr) / previous_data.ctr

        if ctr_change <= -settings.alert_ctr_drop_threshold:
            alert = Alert(
                alert_type="ctr_drop",
                severity="high" if abs(ctr_change) > 0.4 else "medium",
                campaign_id=performance_data.campaign_id,
                campaign_name=performance_data.campaign_name,
                profile_id=performance_data.profile_id,
                message=f"CTR dropped by {abs(ctr_change) * 100:.1f}% (from {previous_data.ctr:.2%} to {performance_data.ctr:.2%})",
                metric_value=performance_data.ctr,
                threshold_value=Decimal(str(settings.alert_ctr_drop_threshold)),
                previous_value=previous_data.ctr,
            )
            self.db.add(alert)
            self.db.commit()
            return alert

        return None

    def _check_spend_spike(self, performance_data: PerformanceData) -> Optional[Alert]:
        """Check if spend has spiked significantly."""
        if performance_data.cost == 0:
            return None

        # Get previous spend for comparison (last 24 hours)
        previous_period_start = performance_data.start_date - timedelta(hours=24)
        previous_spend = (
            self.db.query(func.sum(PerformanceData.cost))
            .filter(
                PerformanceData.campaign_id == performance_data.campaign_id,
                PerformanceData.start_date >= previous_period_start,
                PerformanceData.start_date < performance_data.start_date,
            )
            .scalar()
            or Decimal("0")
        )

        if previous_spend == 0:
            return None

        spend_ratio = performance_data.cost / previous_spend

        if spend_ratio >= settings.alert_spend_spike_threshold:
            alert = Alert(
                alert_type="spend_spike",
                severity="high" if spend_ratio > 2.0 else "medium",
                campaign_id=performance_data.campaign_id,
                campaign_name=performance_data.campaign_name,
                profile_id=performance_data.profile_id,
                message=f"Spend increased by {(spend_ratio - 1) * 100:.1f}% (from ${previous_spend:.2f} to ${performance_data.cost:.2f})",
                metric_value=performance_data.cost,
                threshold_value=Decimal(str(settings.alert_spend_spike_threshold)),
                previous_value=previous_spend,
            )
            self.db.add(alert)
            self.db.commit()
            return alert

        return None

    def _check_acos_threshold(self, performance_data: PerformanceData) -> Optional[Alert]:
        """Check if ACOS exceeds threshold."""
        if not performance_data.acos:
            return None

        if performance_data.acos >= Decimal(str(settings.alert_acos_threshold)):
            alert = Alert(
                alert_type="high_acos",
                severity="high" if performance_data.acos > 0.5 else "medium",
                campaign_id=performance_data.campaign_id,
                campaign_name=performance_data.campaign_name,
                profile_id=performance_data.profile_id,
                message=f"ACOS is {performance_data.acos:.2%}, exceeding threshold of {settings.alert_acos_threshold:.2%}",
                metric_value=performance_data.acos,
                threshold_value=Decimal(str(settings.alert_acos_threshold)),
            )
            self.db.add(alert)
            self.db.commit()
            return alert

        return None

    def _check_roas_threshold(self, performance_data: PerformanceData) -> Optional[Alert]:
        """Check if ROAS is below threshold."""
        if not performance_data.roas:
            return None

        if performance_data.roas < Decimal(str(settings.alert_roas_threshold)):
            alert = Alert(
                alert_type="low_roas",
                severity="high" if performance_data.roas < 1.0 else "medium",
                campaign_id=performance_data.campaign_id,
                campaign_name=performance_data.campaign_name,
                profile_id=performance_data.profile_id,
                message=f"ROAS is {performance_data.roas:.2f}, below threshold of {settings.alert_roas_threshold:.2f}",
                metric_value=performance_data.roas,
                threshold_value=Decimal(str(settings.alert_roas_threshold)),
            )
            self.db.add(alert)
            self.db.commit()
            return alert

        return None

    def _send_alert(self, alert: Alert) -> None:
        """Send alert to Slack."""
        try:
            metrics = {}
            if alert.metric_value:
                metrics["Current Value"] = str(alert.metric_value)
            if alert.previous_value:
                metrics["Previous Value"] = str(alert.previous_value)
            if alert.threshold_value:
                metrics["Threshold"] = str(alert.threshold_value)

            success = self.slack_client.send_alert(
                alert_type=alert.alert_type,
                severity=alert.severity,
                message=alert.message,
                campaign_id=alert.campaign_id,
                campaign_name=alert.campaign_name,
                metrics=metrics if metrics else None,
            )

            if success:
                alert.sent = True
                alert.sent_at = datetime.utcnow()
                self.db.commit()
                logger.info(f"Sent alert {alert.id} to Slack")
            else:
                logger.warning(f"Failed to send alert {alert.id} to Slack")

        except Exception as e:
            logger.error(f"Error sending alert {alert.id}: {e}", exc_info=True)

