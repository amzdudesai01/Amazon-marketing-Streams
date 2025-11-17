"""Create Marketing Stream subscription for eGrowth profile via API."""
import requests
import json
import time
import uuid

# Configuration
# Update ACCESS_TOKEN - get a fresh one using your refresh token
ACCESS_TOKEN = "Atza|gQD_Htx3AwEBAMGz3FoPx6csN0LF2yGWIb8J2M0x4l9FQwAiDsh5TAdSAg73whRdtw9F85y1-W2CcNOlEL55IbGp3lJ7IiIfh3eECttbLVPE0TJLmMYWRQxqEaEWiPvLJXagpfXEWY6iHHeDqDHBsYi7ZzuTipN81phriXEy9CS8F2XNSraF27NKh1hRpIHsODI53xrpcLarK9NoctYbk7ynaEsxsz1v843kdWRoSa0RsAnqteJ6YmOyI3eCfwa0344hguadLJvmEWn-QHEYj30is0PdiNALP_X8p6GmXUg03u3NQlWf6My5T9_iVIbtEG8hWtQHB47rqEFJKaWkRMHS4AM89Q7Y8k9jWB56lWW4zNsml6CMYH5iNYJTgADETcz5un2LAnDov8_I9T3_oruftombikKlpA_IlQ8eNemCOF-t09w1qxJnDD382I-Yt2RF75_J267pn_CtZ34ezWDSZPj9CaYouPRr291Ya28jCC5UB1LEmvp2ws9FtPahgbuGYEr6d2ldka88tvCVb2d54epkMBNPtg0tE2BMCjgW0LVc8lt3w9dHQB01pZCcH865mIO4wZcOfi8IQ5-VDqdByDVFpEuPpyKbfcRpO5QE_KyciKHdaglmVnSutNNGhdroI5xA8IYS1w0"  # Update this - tokens expire after 1 hour!
CLIENT_ID = "amzn1.application-oa2-client.f7c148c8a17344a5a878e3591b54e166"
PROFILE_ID = "2879633829283118"  # eGrowth
SQS_QUEUE_ARN = "arn:aws:sqs:us-east-1:946926531822:amazon-marketing-stream-cf"

# Base URL
BASE_URL = "https://advertising-api.amazon.com"

def get_headers(subscription=True):
    """Get request headers."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Amazon-Advertising-API-ClientId": CLIENT_ID,
        "Amazon-Advertising-API-Scope": PROFILE_ID,
    }
    # Use correct Content-Type for subscription API (per guide)
    if subscription:
        headers["Content-Type"] = "application/vnd.MarketingStreamSubscriptions.StreamSubscriptionResource.v1.0+json"
    else:
        headers["Content-Type"] = "application/json"
    return headers

def list_datasets():
    """List available Marketing Stream datasets."""
    url = f"{BASE_URL}/streams/datasets"
    headers = get_headers(subscription=False)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error listing datasets: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_subscription(dataset_id, client_request_token, notes=None):
    """Create a Marketing Stream subscription."""
    url = f"{BASE_URL}/streams/subscriptions"
    headers = get_headers(subscription=True)
    
    payload = {
        "dataSetId": dataset_id,
        "clientRequestToken": client_request_token,
        "destinationArn": SQS_QUEUE_ARN
    }
    if notes:
        payload["notes"] = notes
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error creating subscription: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_subscriptions():
    """List existing subscriptions."""
    url = f"{BASE_URL}/streams/subscriptions"
    headers = get_headers(subscription=False)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error listing subscriptions: {e}")
        return None

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("Marketing Stream Subscription Setup for eGrowth")
    print("=" * 60)
    print(f"Profile ID: {PROFILE_ID}")
    print(f"SQS Queue ARN: {SQS_QUEUE_ARN}\n")
    print("⚠️  IMPORTANT: Before creating subscriptions, ensure you have:")
    print("   1. Applied the correct IAM policy to your SQS queue")
    print("   2. Each dataset+region combination requires a specific IAM policy")
    print("   3. See: https://advertising.amazon.com/API/docs/v2/guides/marketing-stream\n")
    
    # Step 1: Try to list datasets (optional - may fail due to API issues)
    print("📊 Step 1: Attempting to fetch available datasets...")
    datasets = list_datasets()
    
    dataset_list = []
    if datasets:
        print(f"\n✅ Found datasets:")
        if isinstance(datasets, dict) and 'datasets' in datasets:
            dataset_list = datasets['datasets']
        elif isinstance(datasets, list):
            dataset_list = datasets
        
        for dataset in dataset_list:
            dataset_id = dataset.get('dataSetId') or dataset.get('id') or dataset.get('name')
            print(f"  - {dataset_id}")
    else:
        print("⚠️  Could not fetch datasets via API (this is okay, we'll use common dataset names)")
    
    # Step 2: Check existing subscriptions
    print("\n📋 Step 2: Checking existing subscriptions...")
    existing = list_subscriptions()
    if existing:
        subs = existing.get('subscriptions', [])
        print(f"Found {len(subs)} existing subscription(s)")
        for sub in subs:
            print(f"  - {sub.get('dataSetId')} - Status: {sub.get('status')}")
    
    # Step 3: Create subscriptions for common datasets
    print("\n🚀 Step 3: Creating subscriptions...")
    
    # Common dataset IDs based on guide example (sp-conversion format)
    # Note: Guide shows "sp-conversion" format (lowercase with hyphens)
    # See data guide for complete list: https://advertising.amazon.com/API/docs/v2/guides/marketing-stream
    common_datasets = [
        "sp-conversion",  # Sponsored Products conversion data
        "sp-traffic",     # Sponsored Products traffic data
        "sb-conversion",  # Sponsored Brands conversion data
        "sb-traffic",     # Sponsored Brands traffic data
        "sd-conversion",  # Sponsored Display conversion data
        "sd-traffic",     # Sponsored Display traffic data
    ]
    
    # Use datasets from API if available, otherwise try common ones
    datasets_to_subscribe = []
    if dataset_list:
        for dataset in dataset_list:
            dataset_id = dataset.get('dataSetId') or dataset.get('id') or dataset.get('name')
            if dataset_id:
                datasets_to_subscribe.append(dataset_id)
    else:
        print("📝 Using common dataset names for North America region")
        datasets_to_subscribe = common_datasets
    
    # Create subscriptions
    # Try just one dataset first to see the exact error
    for dataset_id in datasets_to_subscribe[:1]:  # Try just the first one
        print(f"\n📝 Creating subscription for: {dataset_id}")
        # Generate token: 22-36 chars (use GUID format as recommended in guide)
        # Guide recommends using GUID for clientRequestToken
        token = str(uuid.uuid4()).replace('-', '')[:36]  # Remove hyphens, max 36 chars
        if len(token) < 22:
            # Pad to meet minimum 22 chars (shouldn't happen with UUID, but just in case)
            token = token + "0" * (22 - len(token))
        print(f"  Using token: {token} (length: {len(token)})")
        notes = f"eGrowth {dataset_id} subscription"
        result = create_subscription(dataset_id, token, notes=notes)
        
        if result:
            print(f"✅ Success! Subscription created:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Failed to create subscription")
    
    # Step 4: Verify subscriptions
    print("\n✅ Step 4: Verifying subscriptions...")
    time.sleep(2)  # Wait a moment
    final_subs = list_subscriptions()
    if final_subs:
        subs = final_subs.get('subscriptions', [])
        print(f"\n📊 Total subscriptions: {len(subs)}")
        for sub in subs:
            print(f"\n  Dataset: {sub.get('dataSetId')}")
            print(f"  Status: {sub.get('status')}")
            print(f"  Subscription ID: {sub.get('subscriptionId')}")
            if sub.get('sqsEndpoint'):
                print(f"  SQS Endpoint: {sub.get('sqsEndpoint')}")

