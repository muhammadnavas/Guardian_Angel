"""
Test script to verify Gemini API key against all free models.
"""

import os
import time
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY not found in .env file.")
    exit(1)

masked = API_KEY[:6] + "..." + API_KEY[-4:]
print(f"✅ API key found: {masked}\n")

import google.generativeai as genai
genai.configure(api_key=API_KEY)

# All free-tier Gemini models
free_models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

print("=" * 55)
print("   Testing All Free Gemini Models")
print("=" * 55)

results = {}

for model_name in free_models:
    print(f"\n🔄 Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'hello' in one word.")
        reply = response.text.strip()
        print(f"   ✅ PASS — Response: \"{reply}\"")
        results[model_name] = True
    except Exception as e:
        error_msg = str(e).split('\n')[0][:80]
        print(f"   ❌ FAIL — {error_msg}")
        results[model_name] = False
    time.sleep(2)  # small delay to avoid rate limits

# Summary
print("\n" + "=" * 55)
print("   Results Summary")
print("=" * 55)
for model, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status}  —  {model}")

working = [m for m, p in results.items() if p]
print(f"\n{'🎉 ' + str(len(working)) + ' model(s) working!' if working else '⚠️ No models working — check your API key.'}")
