"""Application configuration using Pydantic Settings."""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Amazon Marketing Stream Automation"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/amazon_marketing_streams"

    # AWS Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    sqs_queue_url: Optional[str] = None

    # Amazon Marketing Stream
    amazon_advertising_api_client_id: Optional[str] = None
    amazon_advertising_api_client_secret: Optional[str] = None
    amazon_advertising_api_refresh_token: Optional[str] = None
    amazon_advertising_profile_id: Optional[str] = None

    # Slack
    slack_webhook_url: Optional[str] = None

    # Worker Configuration
    sqs_poll_interval_seconds: int = 5
    max_messages_per_poll: int = 10
    worker_enabled: bool = True

    # Alert Thresholds
    alert_ctr_drop_threshold: float = 0.2  # 20% drop
    alert_spend_spike_threshold: float = 1.5  # 50% increase
    alert_acos_threshold: float = 0.3  # 30% ACOS
    alert_roas_threshold: float = 2.0  # Minimum ROAS

    @property
    def has_aws_credentials(self) -> bool:
        """Check if AWS credentials are configured."""
        return bool(self.aws_access_key_id and self.aws_secret_access_key)

    @property
    def has_sqs_queue(self) -> bool:
        """Check if SQS queue URL is configured."""
        return bool(self.sqs_queue_url)

    @property
    def has_slack_webhook(self) -> bool:
        """Check if Slack webhook is configured."""
        return bool(self.slack_webhook_url)

    @property
    def has_amazon_credentials(self) -> bool:
        """Check if Amazon Ads API credentials are configured."""
        return bool(
            self.amazon_advertising_api_client_id
            and self.amazon_advertising_api_client_secret
            and self.amazon_advertising_api_refresh_token
        )


# Global settings instance
settings = Settings()

