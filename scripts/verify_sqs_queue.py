"""Verify SQS queue exists and check its configuration."""
import boto3
import json

# Configuration
QUEUE_NAME = "amazon-marketing-stream-v2"
REGION = "us-east-1"
AWS_ACCOUNT_ID = "946926531822"

def verify_queue():
    """Verify SQS queue exists and show its configuration."""
    sqs = boto3.client('sqs', region_name=REGION)
    queue_url = f"https://sqs.{REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{QUEUE_NAME}"
    queue_arn = f"arn:aws:sqs:{REGION}:{AWS_ACCOUNT_ID}:{QUEUE_NAME}"
    
    print("=" * 60)
    print("SQS Queue Verification")
    print("=" * 60)
    print(f"Queue Name: {QUEUE_NAME}")
    print(f"Region: {REGION}")
    print(f"Queue URL: {queue_url}")
    print(f"Queue ARN: {queue_arn}\n")
    
    try:
        # Get queue attributes
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        
        attributes = response['Attributes']
        
        print("✅ Queue exists and is accessible!")
        print("\n" + "=" * 60)
        print("Queue Attributes:")
        print("=" * 60)
        print(f"Queue ARN: {attributes.get('QueueArn', 'N/A')}")
        print(f"Created: {attributes.get('CreatedTimestamp', 'N/A')}")
        print(f"Visibility Timeout: {attributes.get('VisibilityTimeout', 'N/A')} seconds")
        print(f"Message Retention: {attributes.get('MessageRetentionPeriod', 'N/A')} seconds")
        
        # Check policy
        policy = attributes.get('Policy')
        if policy:
            print("\n" + "=" * 60)
            print("Current Queue Policy:")
            print("=" * 60)
            policy_json = json.loads(policy)
            print(json.dumps(policy_json, indent=2))
            
            # Check if Amazon Advertising is allowed
            statements = policy_json.get('Statement', [])
            has_amazon_advertising = False
            for stmt in statements:
                principal = stmt.get('Principal', {})
                if isinstance(principal, dict):
                    if 'AWS' in principal:
                        aws_principal = principal['AWS']
                        if isinstance(aws_principal, str) and '394103597723' in aws_principal:
                            has_amazon_advertising = True
                            print(f"\n✅ Found Amazon Advertising principal: {aws_principal}")
                    elif 'Service' in principal:
                        service = principal['Service']
                        if 'advertising.amazonaws.com' in service:
                            has_amazon_advertising = True
                            print(f"\n✅ Found Amazon Advertising service: {service}")
            
            if not has_amazon_advertising:
                print("\n⚠️  WARNING: No Amazon Advertising principal found in policy!")
                print("   This is likely why subscriptions are failing.")
        else:
            print("\n⚠️  WARNING: No policy found on queue!")
            print("   You need to add an IAM policy to allow Amazon Advertising to send messages.")
        
        # Check encryption
        kms_master_key_id = attributes.get('KmsMasterKeyId')
        if kms_master_key_id:
            print(f"\n⚠️  WARNING: Queue has encryption enabled (KMS Key: {kms_master_key_id})")
            print("   Marketing Stream may require encryption to be disabled.")
        else:
            print("\n✅ Queue encryption: Disabled (good for Marketing Stream)")
        
        return True
        
    except sqs.exceptions.QueueDoesNotExist:
        print(f"❌ Queue does not exist: {queue_url}")
        print("   Please create the queue first.")
        return False
    except Exception as e:
        print(f"❌ Error accessing queue: {e}")
        return False

if __name__ == "__main__":
    verify_queue()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. If policy is missing/incorrect, you need to add the correct IAM policy")
    print("2. The guide recommends using CloudFormation template to avoid errors")
    print("3. Each dataset+region requires a specific IAM policy")
    print("4. See: https://advertising.amazon.com/API/docs/v2/guides/marketing-stream")

