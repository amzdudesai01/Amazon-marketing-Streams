"""Script to test Slack client."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.slack_client import SlackClient

def test_slack_client():
    """Test the Slack client."""
    client = SlackClient()
    
    # Test simple message
    print("Testing simple message...")
    result = client.send_message("Test message from Amazon Marketing Stream system")
    print(f"✓ Message sent: {result}")
    
    # Test alert
    print("\nTesting alert...")
    result = client.send_alert(
        alert_type="ctr_drop",
        severity="high",
        message="CTR dropped by 25% (from 2.5% to 1.9%)",
        campaign_id="camp_001",
        campaign_name="Test Campaign",
        metrics={
            "Current CTR": "1.9%",
            "Previous CTR": "2.5%",
            "Threshold": "20% drop"
        }
    )
    print(f"✓ Alert sent: {result}")

if __name__ == "__main__":
    test_slack_client()

