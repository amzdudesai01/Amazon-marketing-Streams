"""View and decode messages from Marketing Stream SQS queue."""
import boto3
import json
from datetime import datetime

# Configuration
QUEUE_NAME = "amazon-marketing-stream-cf"
REGION = "us-east-1"
AWS_ACCOUNT_ID = "946926531822"

def view_messages():
    """View messages from the SQS queue."""
    sqs = boto3.client('sqs', region_name=REGION)
    queue_url = f"https://sqs.{REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{QUEUE_NAME}"
    
    print("=" * 60)
    print("Viewing Marketing Stream Messages")
    print("=" * 60)
    print(f"Queue: {QUEUE_NAME}")
    print(f"Region: {REGION}\n")
    
    try:
        # Get queue attributes to see message count
        attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
        )
        
        visible = attrs['Attributes'].get('ApproximateNumberOfMessages', '0')
        not_visible = attrs['Attributes'].get('ApproximateNumberOfMessagesNotVisible', '0')
        
        print(f"📊 Queue Status:")
        print(f"   Visible messages: {visible}")
        print(f"   In-flight messages: {not_visible}\n")
        
        # Receive messages
        print("📥 Receiving messages...")
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2,
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        
        if not messages:
            print("⚠️  No messages available to view.")
            print("   (Messages may have been processed or are in-flight)")
            return
        
        print(f"✅ Found {len(messages)} message(s)\n")
        print("=" * 60)
        
        for i, message in enumerate(messages, 1):
            print(f"\n{'='*60}")
            print(f"Message {i} of {len(messages)}")
            print(f"{'='*60}")
            print(f"Message ID: {message.get('MessageId')}")
            print(f"Receipt Handle: {message.get('ReceiptHandle')[:50]}...")
            
            # Parse the message body
            try:
                body = json.loads(message['Body'])
                
                # Check message type
                msg_type = body.get('Type', 'Unknown')
                print(f"\n📋 Message Type: {msg_type}")
                
                if msg_type == 'Notification':
                    # This is a Marketing Stream data message
                    print("\n✅ This is a Marketing Stream data message!")
                    
                    # Parse the actual message content
                    if 'Message' in body:
                        try:
                            stream_data = json.loads(body['Message'])
                            print("\n📊 Marketing Stream Data:")
                            print(json.dumps(stream_data, indent=2))
                        except json.JSONDecodeError:
                            print("\n📄 Message Content (raw):")
                            print(body['Message'][:500] + "..." if len(body['Message']) > 500 else body['Message'])
                    
                    # Show metadata
                    if 'Timestamp' in body:
                        timestamp = body['Timestamp']
                        print(f"\n⏰ Timestamp: {timestamp}")
                    
                    if 'TopicArn' in body:
                        print(f"📡 Topic ARN: {body['TopicArn']}")
                
                elif msg_type == 'SubscriptionConfirmation':
                    print("\n⚠️  This is a subscription confirmation message")
                    print("   (Should have been confirmed already)")
                
                else:
                    # Show full body for unknown types
                    print("\n📄 Full Message Body:")
                    print(json.dumps(body, indent=2))
                
                # Show attributes if any
                if message.get('MessageAttributes'):
                    print("\n🏷️  Message Attributes:")
                    for key, value in message['MessageAttributes'].items():
                        print(f"   {key}: {value.get('StringValue', 'N/A')}")
                
            except json.JSONDecodeError:
                print("\n⚠️  Could not parse message body as JSON")
                print(f"Raw body: {message['Body'][:200]}...")
            
            print(f"\n{'='*60}")
        
        print(f"\n💡 Note: These messages are still in the queue.")
        print(f"   They will be processed by your FastAPI worker when enabled.")
        print(f"   Or you can delete them manually in the AWS Console.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    view_messages()

