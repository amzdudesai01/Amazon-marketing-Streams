"""Create a new SQS queue and set the policy."""
import boto3
import json

sqs = boto3.client('sqs', region_name='us-east-1')

# Create a new queue
new_queue_name = 'amazon-marketing-stream-v2'
print(f"Creating new queue: {new_queue_name}...")

try:
    response = sqs.create_queue(QueueName=new_queue_name)
    new_queue_url = response['QueueUrl']
    print(f"✅ Queue created: {new_queue_url}")
    
    # Get queue ARN
    attrs = sqs.get_queue_attributes(
        QueueUrl=new_queue_url,
        AttributeNames=['QueueArn']
    )
    queue_arn = attrs['Attributes']['QueueArn']
    print(f"Queue ARN: {queue_arn}")
    
    # Wait a moment for queue to be ready
    import time
    time.sleep(2)
    
    # Try setting the policy
    print("\nSetting policy on new queue...")
    policy = {
        "Version": "2012-10-17",
        "Id": "__default_policy_ID",
        "Statement": [
            {
                "Sid": "__owner_statement",
                "Effect": "Allow",
                "Principal": {"AWS": "arn:aws:iam::946926531822:root"},
                "Action": "SQS:*",
                "Resource": queue_arn
            },
            {
                "Sid": "AllowAmazonAdvertising",
                "Effect": "Allow",
                "Principal": {
                    "Service": "advertising.amazonaws.com"
                },
                "Action": ["SQS:SendMessage", "SQS:GetQueueAttributes"],
                "Resource": queue_arn
            }
        ]
    }
    
    sqs.set_queue_attributes(
        QueueUrl=new_queue_url,
        Attributes={'Policy': json.dumps(policy)}
    )
    print("✅ Policy set successfully on new queue!")
    
    # Verify
    verify_attrs = sqs.get_queue_attributes(
        QueueUrl=new_queue_url,
        AttributeNames=['Policy']
    )
    print("\n✅ Verified policy:")
    print(json.dumps(json.loads(verify_attrs['Attributes']['Policy']), indent=2))
    
    print(f"\n✅ SUCCESS! Use this queue URL for Marketing Stream:")
    print(f"   {new_queue_url}")
    print(f"\n   Queue ARN: {queue_arn}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

