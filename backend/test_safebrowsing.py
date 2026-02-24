"""
Test script to verify that the Google Safe Browsing API key is working.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SAFEBROWSING_API_KEY")

if not API_KEY:
    print("❌ SAFEBROWSING_API_KEY not found in .env file.")
    exit(1)

masked = API_KEY[:6] + "..." + API_KEY[-4:]
print(f"✅ API key found: {masked}")

# Google Safe Browsing Lookup API v4 endpoint
url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"

# Test with a known malicious URL (Google's test URL) and a safe URL
payload = {
    "client": {
        "clientId": "eldershield-test",
        "clientVersion": "1.0.0"
    },
    "threatInfo": {
        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
        "platformTypes": ["ANY_PLATFORM"],
        "threatEntryTypes": ["URL"],
        "threatEntries": [
            {"url": "http://testsafebrowsing.appspot.com/s/malware.html"},
            {"url": "http://testsafebrowsing.appspot.com/s/phishing.html"},
            {"url": "https://www.google.com"},
        ]
    }
}

print("\n🔄 Sending request to Safe Browsing API...")
print(f"   Testing URLs:")
for entry in payload["threatInfo"]["threatEntries"]:
    print(f"     • {entry['url']}")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("matches"):
            print(f"\n✅ API is working! Found {len(data['matches'])} threat(s):\n")
            for match in data["matches"]:
                print(f"  ⚠️  {match['threat']['url']}")
                print(f"      Threat type: {match['threatType']}")
                print(f"      Platform:    {match['platformType']}\n")
        else:
            print("\n✅ API is working! No threats found (all URLs are clean).")
    elif response.status_code == 400:
        print(f"\n❌ Bad request: {response.json()}")
    elif response.status_code == 403:
        print(f"\n❌ API key is invalid or Safe Browsing API is not enabled.")
        print(f"   Enable it at: https://console.cloud.google.com/apis/library/safebrowsing.googleapis.com")
    else:
        print(f"\n❌ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("\n❌ Connection failed. Check your internet connection.")
except Exception as e:
    print(f"\n❌ Error: {e}")
