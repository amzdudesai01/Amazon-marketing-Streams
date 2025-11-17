"""List Amazon Ads profiles and campaigns using the API."""
import requests
import json

# Configuration - UPDATE THESE
ACCESS_TOKEN = "Atza|gQDTTMnNAwEBAI3jndI3AThcxrQPLiEXIuwTYHWmmXP7aqIPtYM8Ut1WOzZa7TFC4su9NLGUlPWCcfRUgRo5njLe1NNENuCQ-tS9AO5oT2hZGwHS-5C1jFvYNgRfwmPj6JCgtzMBexPV9l8WKPTeBJuSyKPuO9HCdJAZqSTh55I-F45ueYYLbqHxjJhdQUhehXv2FRpl4cFzjfkS4HJ3zy6E205HVwP69pdLgYByQQVBoX4ZByCwqK7tuc-YA61K6AE5j2X4C74LQ2RbHRJrRIOw-y1dPPwi5-0Gak-fBy_MRwqWhkKCwe8_f5tPTQkJSqmxjw_H4XdPmqvmbh35_9-KXyISRfWQs632yn6OcDzdbSZjnFIvj8AMGisnWqmQARLeg27-jr1KLgy6A4pC7vcSanZbvD9fMDjiJePFSFSNySZ9USfgHzNeBuq1oB-KNSat37G8JnqbjxzZ5xDG11XSU_woWUGXgzU-Kj1VkMMo1GQsEyclAPTlcd7kI9Cr325ZHfpPIJQ61gdeyje16NyLO63RoJjCUoGWwtkP5Dh2DwfDGu4KPZRgl0C81B7s0HlCfxGzSGIbE39VlYsa-eYZyf6iXZte4IHzn_lj8ZYw0EZc2ZRYKdWlBWg75cajQWQ_kEDVoTezKcyy"
CLIENT_ID = "amzn1.application-oa2-client.f7c148c8a17344a5a878e3591b54e166"

def get_profiles():
    """Get all advertiser profiles."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Amazon-Advertising-API-ClientId": CLIENT_ID,
        "Content-Type": "application/json"
    }
    
    url = "https://advertising-api.amazon.com/v2/profiles"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting profiles: {e}")
        return None

def get_campaigns(profile_id):
    """Get campaigns for a specific profile."""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Amazon-Advertising-API-ClientId": CLIENT_ID,
        "Amazon-Advertising-API-Scope": profile_id,
        "Content-Type": "application/json"
    }
    
    url = "https://advertising-api.amazon.com/v2/sp/campaigns"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting campaigns for profile {profile_id}: {e}")
        return None

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("Amazon Ads Profiles and Campaigns")
    print("=" * 60)
    
    # Get profiles
    print("\n📊 Fetching Profiles...")
    profiles = get_profiles()
    
    if profiles:
        print(f"\n✅ Found {len(profiles)} profile(s):\n")
        for profile in profiles:
            print(f"Profile ID: {profile.get('profileId')}")
            print(f"  Name: {profile.get('accountInfo', {}).get('name', 'N/A')}")
            print(f"  Type: {profile.get('accountInfo', {}).get('type', 'N/A')}")
            print(f"  Country: {profile.get('countryCode', 'N/A')}")
            print(f"  Currency: {profile.get('currencyCode', 'N/A')}")
            print()
        
        # Get campaigns for eGrowth profile (or you can specify one)
        if profiles:
            # Find eGrowth profile
            egrowth_profile = None
            for profile in profiles:
                if profile.get('profileId') == 2879633829283118 or profile.get('accountInfo', {}).get('name') == 'eGrowth':
                    egrowth_profile = profile
                    break
            
            if egrowth_profile:
                profile_id = str(egrowth_profile.get('profileId'))
                print(f"\n📈 Fetching Campaigns for eGrowth Profile {profile_id}...")
                campaigns = get_campaigns(profile_id)
            else:
                # Fallback to first profile
                first_profile_id = str(profiles[0].get('profileId'))
                print(f"\n📈 Fetching Campaigns for Profile {first_profile_id}...")
                campaigns = get_campaigns(first_profile_id)
            
            if campaigns:
                campaign_list = campaigns.get('campaigns', [])
                print(f"\n✅ Found {len(campaign_list)} campaign(s):\n")
                for campaign in campaign_list[:10]:  # Show first 10
                    print(f"Campaign ID: {campaign.get('campaignId')}")
                    print(f"  Name: {campaign.get('name', 'N/A')}")
                    print(f"  State: {campaign.get('state', 'N/A')}")
                    print(f"  Budget: {campaign.get('budget', {}).get('amount', 'N/A')}")
                    print()
                
                if len(campaign_list) > 10:
                    print(f"... and {len(campaign_list) - 10} more campaigns")
    else:
        print("❌ Could not fetch profiles. Check your access token.")

