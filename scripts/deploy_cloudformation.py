"""Deploy CloudFormation stack for Marketing Stream SQS queue."""
import boto3
import sys
import os

# Configuration
STACK_NAME = "amazon-marketing-stream-queue"
TEMPLATE_FILE = "cloudformation/marketing-stream-queue.yaml"
REGION = "us-east-1"  # NA region

# Parameters - UPDATE THESE
STREAM_DATASET_ID = "sp-conversion"  # Change to your desired dataset
QUEUE_NAME = "amazon-marketing-stream-cf"  # New queue name (or use existing)
STREAM_REALM = "NA"  # NA, EU, or FE

def deploy_stack():
    """Deploy CloudFormation stack."""
    cloudformation = boto3.client('cloudformation', region_name=REGION)
    
    # Read the template file
    if not os.path.exists(TEMPLATE_FILE):
        print(f"❌ Template file not found: {TEMPLATE_FILE}")
        print("   Make sure you're running from the project root directory")
        return False
    
    with open(TEMPLATE_FILE, 'r') as f:
        template_body = f.read()
    
    print("=" * 60)
    print("Deploying CloudFormation Stack for Marketing Stream")
    print("=" * 60)
    print(f"Stack Name: {STACK_NAME}")
    print(f"Region: {REGION}")
    print(f"Dataset: {STREAM_DATASET_ID}")
    print(f"Queue Name: {QUEUE_NAME}")
    print(f"Realm: {STREAM_REALM}\n")
    
    parameters = [
        {
            'ParameterKey': 'StreamDatasetId',
            'ParameterValue': STREAM_DATASET_ID
        },
        {
            'ParameterKey': 'StreamDestinationQueueName',
            'ParameterValue': QUEUE_NAME
        },
        {
            'ParameterKey': 'StreamRealm',
            'ParameterValue': STREAM_REALM
        }
    ]
    
    try:
        print("📤 Creating CloudFormation stack...")
        response = cloudformation.create_stack(
            StackName=STACK_NAME,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM']  # May be needed for IAM resources
        )
        
        stack_id = response['StackId']
        print(f"✅ Stack creation initiated!")
        print(f"   Stack ID: {stack_id}")
        print("\n⏳ Waiting for stack creation to complete...")
        print("   (This may take a few minutes)")
        
        # Wait for stack creation
        waiter = cloudformation.get_waiter('stack_create_complete')
        waiter.wait(StackName=STACK_NAME)
        
        print("\n✅ Stack created successfully!")
        
        # Get stack outputs
        stack_info = cloudformation.describe_stacks(StackName=STACK_NAME)
        outputs = stack_info['Stacks'][0].get('Outputs', [])
        
        print("\n" + "=" * 60)
        print("Stack Outputs:")
        print("=" * 60)
        for output in outputs:
            print(f"{output['OutputKey']}: {output['OutputValue']}")
        
        # Find QueueArn
        queue_arn = None
        for output in outputs:
            if output['OutputKey'] == 'QueueArn':
                queue_arn = output['OutputValue']
                break
        
        if queue_arn:
            print("\n" + "=" * 60)
            print("Next Steps:")
            print("=" * 60)
            print(f"1. Update your subscription script with this Queue ARN:")
            print(f"   {queue_arn}")
            print("\n2. Run the subscription script:")
            print("   python scripts/create_marketing_stream_subscription.py")
            print("\n   (Make sure to update SQS_QUEUE_ARN in the script)")
        
        return True
        
    except cloudformation.exceptions.AlreadyExistsException:
        print(f"❌ Stack '{STACK_NAME}' already exists!")
        print("   Options:")
        print("   1. Delete the existing stack first")
        print("   2. Use a different stack name")
        print("   3. Update the existing stack")
        return False
    except Exception as e:
        print(f"❌ Error creating stack: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  Note: This creates a NEW queue with the correct IAM policy")
    print("   If you want to use an existing queue, you'll need to")
    print("   manually apply the IAM policy (which we've been struggling with)\n")
    
    response = input("Continue with CloudFormation deployment? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    deploy_stack()

