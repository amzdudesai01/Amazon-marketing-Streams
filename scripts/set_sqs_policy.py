"""Script to set SQS queue policy using boto3."""
import boto3
import json

# Initialize SQS client
sqs = boto3.client('sqs', region_name='us-east-1')

# Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/946926531822/amazon-marketing-stream'

# First, try to get the current policy to see its exact format
try:
    current_attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['Policy']
    )
    if 'Policy' in current_attrs.get('Attributes', {}):
        current_policy = json.loads(current_attrs['Attributes']['Policy'])
        print("Current policy structure:")
        print(json.dumps(current_policy, indent=2))
        print("\n" + "="*50 + "\n")
except Exception as e:
    print(f"Could not get current policy: {e}")
    current_policy = None

# Policy JSON - trying without Id field first
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "__owner_statement",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::946926531822:root"
            },
            "Action": "SQS:*",
            "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
        },
        {
            "Sid": "AllowAmazonAdvertising",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::394103597723:root"
            },
            "Action": [
                "SQS:SendMessage",
                "SQS:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
        }
    ]
}

# Try multiple policy formats
policy_formats = [
    # Format 1: Without Id
    {
        "Version": "2012-10-17",
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
                "Principal": {"AWS": "arn:aws:iam::394103597723:root"},
                "Action": ["SQS:SendMessage", "SQS:GetQueueAttributes"],
                "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
            }
        ]
    },
    # Format 2: With Id matching default
    {
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
                "Principal": {"AWS": "arn:aws:iam::394103597723:root"},
                "Action": ["SQS:SendMessage", "SQS:GetQueueAttributes"],
                "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
            }
        ]
    },
    # Format 3: Principal as account ID only (no :root)
    {
        "Version": "2012-10-17",
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
                "Principal": {"AWS": "394103597723"},
                "Action": ["SQS:SendMessage", "SQS:GetQueueAttributes"],
                "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
            }
        ]
    }
]

# Try using add_permission instead of setting full policy
print("\n" + "="*60)
print("Trying add_permission API instead...")
print("="*60)

try:
    # Try add_permission with account ID as ARN
    response = sqs.add_permission(
        QueueUrl=queue_url,
        Label='AllowAmazonAdvertising',
        AWSAccountIds=['394103597723'],
        Actions=['SendMessage', 'GetQueueAttributes']
    )
    print("✅ SUCCESS! add_permission worked!")
    print(f"Response: {response}")
    
    # Verify
    queue_attrs = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['Policy']
    )
    print("\n✅ Verified - Current policy:")
    print(json.dumps(json.loads(queue_attrs['Attributes']['Policy']), indent=2))
    
except Exception as e1:
    print(f"❌ add_permission with account ID failed: {e1}")
    
    # Try with full ARN
    try:
        print("\nTrying with Principal as full ARN...")
        # We can't use add_permission with ARN, so let's try modifying the existing policy
        # by getting it, adding the statement, and setting it back
        current_attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['Policy']
        )
        current_policy = json.loads(current_attrs['Attributes']['Policy'])
        
        # Add the new statement to existing policy
        new_statement = {
            "Sid": "AllowAmazonAdvertising",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::394103597723:root"},
            "Action": ["SQS:SendMessage", "SQS:GetQueueAttributes"],
            "Resource": "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream"
        }
        
        current_policy['Statement'].append(new_statement)
        
        # Try setting it back
        response = sqs.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={'Policy': json.dumps(current_policy)}
        )
        print("✅ SUCCESS! Modified existing policy worked!")
        
        # Verify
        queue_attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['Policy']
        )
        print("\n✅ Verified - Current policy:")
        print(json.dumps(json.loads(queue_attrs['Attributes']['Policy']), indent=2))
        
    except Exception as e2:
        print(f"❌ All methods failed.")
        print(f"Error 1 (add_permission): {e1}")
        print(f"Error 2 (modify existing): {e2}")
        print("\n💡 Recommendation: Create a NEW queue and try setting the policy there.")
        print("   The current queue may have some internal state issue.")

