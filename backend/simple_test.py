"""
Simple API Testing for Minerva
Quick validation of OpenAI and SafeBrowsing APIs
"""

import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

print("=" * 50)
print("SIMPLE API TEST")
print("=" * 50)

# Test 1: Check API Keys
print("\n1. Checking API Keys...")
openai_key = os.getenv("OPENAI_API_KEY")
safebrowsing_key = os.getenv("SAFEBROWSING_API_KEY")

if openai_key and openai_key.startswith("sk-"):
    print("   ✓ OPENAI_API_KEY: Found")
else:
    print("   ✗ OPENAI_API_KEY: Missing or invalid")

if safebrowsing_key and safebrowsing_key != "your_safebrowsing_api_key_here":
    print("   ✓ SAFEBROWSING_API_KEY: Found")
else:
    print("   ✗ SAFEBROWSING_API_KEY: Missing or invalid")

# Test 2: OpenAI Connection
print("\n2. Testing OpenAI API...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, test connection."}],
        max_tokens=20
    )
    print("   ✓ OpenAI API: Connected")
    print(f"   Message: {response.choices[0].message.content}")
except Exception as e:
    print(f"   ✗ OpenAI API: {str(e)}")

# Test 3: SafeBrowsing Connection
print("\n3. Testing SafeBrowsing API...")
if safebrowsing_key and safebrowsing_key != "your_safebrowsing_api_key_here":
    try:
        import requests
        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={safebrowsing_key}",
            json={
                "client": {"clientId": "test", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE"],
                    "platformTypes": ["WINDOWS"],
                    "threatEntries": [{"url": "https://www.google.com"}]
                }
            },
            timeout=5
        )
        if response.status_code == 200:
            print("   ✓ SafeBrowsing API: Connected")
        else:
            print(f"   ✗ SafeBrowsing API: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ✗ SafeBrowsing API: {str(e)}")
else:
    print("   ⚠ SafeBrowsing API: Key not configured")

# Test 4: Required Libraries
print("\n4. Testing Required Libraries...")
libraries = {
    "PIL": "Pillow",
    "autogen_agentchat": "AutoGen AgentChat",
    "pytesseract": "pytesseract",
    "gradio": "Gradio",
    "sqlite3": "SQLite3"
}

for lib, name in libraries.items():
    try:
        __import__(lib)
        print(f"   ✓ {name}: Installed")
    except ImportError:
        print(f"   ✗ {name}: Not installed")

print("\n" + "=" * 50)
print("TEST COMPLETE")
print("=" * 50)
