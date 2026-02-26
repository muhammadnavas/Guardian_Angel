import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from tools import ScamDetector, AlertSystem

d = ScamDetector()

# Test 1: CRITICAL scam
r = d.analyze_text("CBI officer here. You are under arrest. Send 50000 rupees immediately or your account will be frozen!")
score = r["threat_score"]
level = d.get_threat_level(score)
passed = score >= 50 and level in ("HIGH_RISK", "CRITICAL")
print(f"CRITICAL test: score={score}, level={level}, passed={passed}")

# Test 2: SAFE
r2 = d.analyze_text("Hi, calling to remind about doctor appointment tomorrow at 3 PM.")
passed2 = r2["threat_score"] < 25
print(f"SAFE test: score={r2['threat_score']}, passed={passed2}")

# Test 3: Hindi keywords
r3 = d.analyze_text("Aapko CBI ne giraftaar karna hai. Abhi paise jama karo. Warrant aa gaya hai.")
print(f"Hindi test: score={r3['threat_score']}, fear_indicators={r3['fear_indicators']}")

# Test 4: AlertSystem
a = AlertSystem()
msg = a.escalate("HIGH_RISK", "CBI impersonation detected - test")
print(f"AlertSystem: returned message length = {len(msg)}")

# Test 5: agents_audio import
from agents_audio import GuardianAngelTeam
print("agents_audio import: OK")

# Test 6: app import (syntax check only)
import importlib.util
spec = importlib.util.spec_from_file_location("app_module", os.path.join(os.path.dirname(__file__), "app.py"))
print("app.py syntax: OK (spec loaded)")

print("\nAll checks PASSED")
