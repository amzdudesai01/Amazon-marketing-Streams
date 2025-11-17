"""Set IAM policy for Marketing Stream on SQS queue using Service principal."""
import boto3
import json

# Configuration
QUEUE_NAME = "amazon-marketing-stream-v2"
REGION = "us-east-1"
AWS_ACCOUNT_ID = "946926531822"
QUEUE_ARN = f"arn:aws:sqs:{REGION}:{AWS_ACCOUNT_ID}:{QUEUE_NAME}"

def set_policy():
    """Set IAM policy for Marketing Stream."""
    sqs = boto3.client('sqs', region_name=REGION)
    queue_url = f"https://sqs.{REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{QUEUE_NAME}"
    
    print("=" * 60)
    print("Setting Marketing Stream IAM Policy")
    print("=" * 60)
    print(f"Queue: {QUEUE_NAME}")
    print(f"Region: {REGION} (NA)\n")
    
    # Policy format using Service principal (recommended approach)
    # This allows Amazon Advertising service to send messages
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "QueueOwnerOnlyAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{AWS_ACCOUNT_ID}:root"
                },
                "Action": "SQS:*",
                "Resource": QUEUE_ARN
            },
            {
                "Sid": "AllowAmazonMarketingStream",
                "Effect": "Allow",
                "Principal": {
                    "Service": "advertising.amazonaws.com"
                },
                "Action": [
                    "sqs:SendMessage",
                    "sqs:GetQueueAttributes"
                ],
                "Resource": QUEUE_ARN,
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "true"
                    }
                }
            }
        ]
    }
    
    policy_json = json.dumps(policy, indent=2)
    print("Policy to apply:")
    print("=" * 60)
    print(policy_json)
    print("=" * 60)
    
    try:
        response = sqs.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={
                'Policy': policy_json
            }
        )
        
        print("\n✅ Policy applied successfully!")
        
        # Verify the policy was set
        verify_response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['Policy']
        )
        
        print("\n✅ Verification: Policy is now set on the queue")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting policy: {e}")
        print("\n💡 Alternative: Try using AWS CloudFormation template")
        print("   The guide recommends CloudFormation to avoid manual errors")
        return False

if __name__ == "__main__":
    success = set_policy()
    
    if success:
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Try creating the subscription again:")
        print("   python scripts/create_marketing_stream_subscription.py")
        print("\n2. Note: The guide says each dataset+region needs a specific policy")
        print("   This is a general policy - if it still fails, you may need")
        print("   the dataset-specific policy from the data guide")
    else:
        print("\n" + "=" * 60)
        print("Recommendation:")
        print("=" * 60)
        print("Use the CloudFormation template from the guide:")
        print("https://advertising.amazon.com/API/docs/v2/guides/marketing-stream")
        print("\nThe CloudFormation template automatically sets the correct policies")

