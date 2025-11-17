"""Script to seed sample data for testing."""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.clients.mock_sqs import MockSQSClient
from app.services.message_processor import MessageProcessor
from app.services.alert_service import AlertService

def seed_sample_data():
    """Seed sample data into the system."""
    # Load sample message
    sample_file = Path(__file__).parent.parent / "sample_data" / "sample_stream_message.json"
    
    if not sample_file.exists():
        print(f"Sample file not found: {sample_file}")
        return
    
    with open(sample_file, "r") as f:
        sample_message = json.load(f)
    
    # Add to mock SQS
    mock_sqs = MockSQSClient()
    mock_sqs.add_sample_message(sample_message)
    
    print(f"Added sample message to mock SQS queue")
    print(f"Message ID: {sample_message.get('messageId')}")
    print(f"Campaign: {sample_message.get('data', {}).get('campaignName')}")
    
    # Process the message
    db = SessionLocal()
    try:
        processor = MessageProcessor(db)
        performance_data = processor.process_message(sample_message)
        
        if performance_data:
            print(f"\n✓ Processed message successfully")
            print(f"  Campaign ID: {performance_data.campaign_id}")
            print(f"  Impressions: {performance_data.impressions}")
            print(f"  Clicks: {performance_data.clicks}")
            print(f"  Cost: ${performance_data.cost}")
            print(f"  Sales: ${performance_data.sales}")
            print(f"  CTR: {performance_data.ctr:.2%}" if performance_data.ctr else "  CTR: N/A")
            print(f"  ACOS: {performance_data.acos:.2%}" if performance_data.acos else "  ACOS: N/A")
            print(f"  ROAS: {performance_data.roas:.2f}" if performance_data.roas else "  ROAS: N/A")
            
            # Check for alerts
            alert_service = AlertService(db)
            alerts = alert_service.check_and_create_alerts(performance_data)
            
            if alerts:
                print(f"\n✓ Created {len(alerts)} alert(s)")
                for alert in alerts:
                    print(f"  - {alert.alert_type}: {alert.message}")
        else:
            print("\n✗ Failed to process message")
            
    except Exception as e:
        print(f"\n✗ Error processing message: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()

