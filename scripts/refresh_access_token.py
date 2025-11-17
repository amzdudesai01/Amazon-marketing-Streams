"""Refresh Amazon Ads API access token using refresh token."""
import requests
import json

# Configuration - UPDATE THESE
REFRESH_TOKEN = "YOUR_REFRESH_TOKEN_HERE"
CLIENT_ID = "amzn1.application-oa2-client.f7c148c8a17344a5a878e3591b54e166"
CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"

def refresh_token():
    """Get a new access token using refresh token."""
    url = "https://api.amazon.com/auth/o2/token"
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        print("✅ Successfully refreshed access token!")
        print("\n" + "=" * 60)
        print("NEW ACCESS TOKEN:")
        print("=" * 60)
        print(result.get('access_token'))
        print("\n" + "=" * 60)
        print("Token expires in:", result.get('expires_in'), "seconds")
        print("=" * 60)
        
        return result.get('access_token')
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error refreshing token: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("Refreshing Amazon Ads API access token...")
    print("=" * 60)
    token = refresh_token()
    
    if token:
        print("\n💡 Copy the access token above and update it in:")
        print("   scripts/create_marketing_stream_subscription.py")
        print("   (Line 9: ACCESS_TOKEN = \"...\")")

