"""Check SQS queue for subscription confirmation message and confirm it."""
import boto3
import json
import requests

# Configuration
QUEUE_NAME = "amazon-marketing-stream-cf"
REGION = "us-east-1"
AWS_ACCOUNT_ID = "946926531822"

def check_and_confirm_subscription():
    """Check SQS queue for subscription confirmation and confirm it."""
    sqs = boto3.client('sqs', region_name=REGION)
    queue_url = f"https://sqs.{REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{QUEUE_NAME}"
    
    print("=" * 60)
    print("Checking SQS Queue for Subscription Confirmation")
    print("=" * 60)
    print(f"Queue: {QUEUE_NAME}")
    print(f"Region: {REGION}\n")
    
    try:
        # Receive messages from the queue
        print("📥 Checking for messages in queue...")
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5,  # Short polling
            MessageAttributeNames=['All']
        )
        
        messages = response.get('Messages', [])
        
        if not messages:
            print("⚠️  No messages found in queue yet.")
            print("   Amazon may still be sending the confirmation message.")
            print("   Try again in a few moments.")
            return False
        
        print(f"✅ Found {len(messages)} message(s) in queue\n")
        
        # Look for subscription confirmation messages
        for i, message in enumerate(messages, 1):
            body = json.loads(message['Body'])
            
            print(f"Message {i}:")
            print(f"  Message ID: {message.get('MessageId')}")
            
            # Check if it's a subscription confirmation
            if body.get('Type') == 'SubscriptionConfirmation':
                print("  ✅ This is a SubscriptionConfirmation message!")
                
                token = body.get('Token')
                subscribe_url = body.get('SubscribeURL')
                topic_arn = body.get('TopicArn')
                
                print(f"\n  Topic ARN: {topic_arn}")
                print(f"  Subscribe URL: {subscribe_url}")
                
                # Confirm the subscription
                print("\n🔗 Confirming subscription...")
                try:
                    confirm_response = requests.get(subscribe_url, timeout=10)
                    confirm_response.raise_for_status()
                    
                    print("✅ Subscription confirmed successfully!")
                    print(f"   Response: {confirm_response.text[:200]}...")
                    
                    # Delete the message from queue after confirmation
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    print("   Message deleted from queue.")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error confirming subscription: {e}")
                    print(f"   You can manually visit: {subscribe_url}")
                    return False
            else:
                print(f"  Type: {body.get('Type', 'Unknown')}")
                print(f"  (This is not a subscription confirmation message)")
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking queue: {e}")
        return False

if __name__ == "__main__":
    success = check_and_confirm_subscription()
    
    if success:
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Check subscription status:")
        print("   python scripts/create_marketing_stream_subscription.py")
        print("   (Status should change from PENDING_CONFIRMATION to ACTIVE)")
        print("\n2. Once ACTIVE, Amazon will start sending data to your queue")
        print("3. Your FastAPI worker will process the messages automatically")
    else:
        print("\n" + "=" * 60)
        print("If no confirmation message found:")
        print("=" * 60)
        print("1. Wait a few minutes and try again")
        print("2. Check the SQS queue in AWS Console manually")
        print("3. Look for messages with Type: 'SubscriptionConfirmation'")

