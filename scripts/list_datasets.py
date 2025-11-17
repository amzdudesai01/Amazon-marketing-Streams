"""List available Marketing Stream datasets using Python requests."""
import requests
import json

# Configuration
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
CLIENT_ID = "amzn1.application-oa2-client.f7c148c8a17344a5a878e3591b54e166"
PROFILE_ID = "2103765108426284"

# Headers
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Amazon-Advertising-API-ClientId": CLIENT_ID,
    "Amazon-Advertising-API-Scope": PROFILE_ID,
    "Content-Type": "application/json"
}

# Make request
url = "https://advertising-api.amazon.com/streams/datasets"

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    print("✅ Success! Available datasets:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

