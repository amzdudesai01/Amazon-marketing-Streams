"""Utility for calculating performance metrics."""
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional

from app.models.stream_data import PerformanceData

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculates performance metrics from raw data."""

    def calculate_metrics(self, performance_data: PerformanceData) -> Dict[str, Optional[Decimal]]:
        """Calculate all metrics for performance data."""
        return {
            "ctr": self.calculate_ctr(performance_data),
            "cpc": self.calculate_cpc(performance_data),
            "acos": self.calculate_acos(performance_data),
            "roas": self.calculate_roas(performance_data),
            "conversion_rate": self.calculate_conversion_rate(performance_data),
        }

    def calculate_ctr(self, performance_data: PerformanceData) -> Optional[Decimal]:
        """Calculate Click-Through Rate (CTR)."""
        if performance_data.impressions == 0:
            return None

        ctr = Decimal(performance_data.clicks) / Decimal(performance_data.impressions)
        return ctr.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def calculate_cpc(self, performance_data: PerformanceData) -> Optional[Decimal]:
        """Calculate Cost Per Click (CPC)."""
        if performance_data.clicks == 0:
            return None

        cpc = performance_data.cost / Decimal(performance_data.clicks)
        return cpc.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def calculate_acos(self, performance_data: PerformanceData) -> Optional[Decimal]:
        """Calculate Advertising Cost of Sales (ACOS)."""
        if performance_data.sales == 0:
            return None

        acos = performance_data.cost / performance_data.sales
        return acos.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def calculate_roas(self, performance_data: PerformanceData) -> Optional[Decimal]:
        """Calculate Return on Ad Spend (ROAS)."""
        if performance_data.cost == 0:
            return None

        roas = performance_data.sales / performance_data.cost
        return roas.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    def calculate_conversion_rate(
        self, performance_data: PerformanceData
    ) -> Optional[Decimal]:
        """Calculate Conversion Rate."""
        if performance_data.clicks == 0:
            return None

        conversion_rate = Decimal(performance_data.orders) / Decimal(performance_data.clicks)
        return conversion_rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

