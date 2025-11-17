"""Set SQS queue policy using Service principal for Amazon Advertising."""
import boto3
import json

sqs = boto3.client('sqs', region_name='us-east-1')
queue_url = 'https://sqs.us-east-1.amazonaws.com/946926531822/amazon-marketing-stream'

# Get current policy to preserve owner statement
current_attrs = sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['Policy']
)
current_policy = json.loads(current_attrs['Attributes']['Policy'])

# Policy with Service principal
policy = {
    "Version": "2012-10-17",
    "Id": "__default_policy_ID",
    "Statement": [
        {
            "Sid": "__owner_statement",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::946926531822:root"},
            "Action": "SQS:*",
            "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
        },
        {
            "Sid": "AllowAmazonAdvertising",
            "Effect": "Allow",
            "Principal": {
                "Service": "advertising.amazonaws.com"
            },
            "Action": [
                "SQS:SendMessage",
                "SQS:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
        }
    ]
}

try:
    response = sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={'Policy': json.dumps(policy)}
    )
    print("✅ Policy set successfully with Service principal!")
    
    # Verify
    queue_attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['Policy']
    )
    print("\n✅ Verified - Current policy:")
    print(json.dumps(json.loads(queue_attrs['Attributes']['Policy']), indent=2))
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

