"""Script to test mock SQS client."""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.clients.mock_sqs import MockSQSClient

def test_mock_sqs():
    """Test the mock SQS client."""
    client = MockSQSClient()
    
    # Add a test message
    test_message = {
        "messageId": "test_msg_001",
        "datasetType": "SP",
        "profileId": "test_profile",
        "data": {
            "campaignId": "test_campaign",
            "campaignName": "Test Campaign",
            "impressions": 100,
            "clicks": 5,
            "cost": 10.00,
            "sales": 50.00,
            "orders": 2,
            "startDate": "2024-01-15T10:00:00Z",
            "endDate": "2024-01-15T11:00:00Z"
        }
    }
    
    client.add_sample_message(test_message)
    print("✓ Added test message to mock queue")
    
    # Receive messages
    messages = client.receive_messages(max_messages=10)
    print(f"✓ Received {len(messages)} message(s)")
    
    for msg in messages:
        print(f"\nMessage ID: {msg['message_id']}")
        print(f"Body: {json.dumps(msg['body'], indent=2)}")
        
        # Delete message
        client.delete_message(msg['receipt_handle'])
        print("✓ Deleted message")
    
    # Try to receive again (should be empty)
    messages = client.receive_messages(max_messages=10)
    print(f"\n✓ Queue is now empty ({len(messages)} messages)")

if __name__ == "__main__":
    test_mock_sqs()

