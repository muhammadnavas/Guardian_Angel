"""Test ScamDetector against TrainingData text samples."""
import sys, os
# Force UTF-8 output on Windows so non-ASCII indicators print cleanly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
from tools import ScamDetector

d = ScamDetector()
TRAINING_DIR = os.path.join(os.path.dirname(__file__), "TrainingData")

txt_files = [f for f in os.listdir(TRAINING_DIR) if f.endswith(".txt")]

print("\nScamDetector Test Against TrainingData")
print("=" * 60)

for fname in sorted(txt_files):
    path = os.path.join(TRAINING_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    result = d.analyze_text(text)
    score = result["threat_score"]
    level = d.get_threat_level(score)
    is_positive = "false_negative" not in fname  # expect positive detection

    print(f"\nFile   : {fname}")
    print(f"Score  : {score}/100")
    print(f"Level  : {level}")
    print(f"Expect : {'SCAM (positive)' if is_positive else 'SAFE (negative)'}")
    print(f"Result : {'PASS' if (is_positive and score >= 25) or (not is_positive and score < 25) else 'FAIL -- NEEDS FIX'}")
    print(f"  Fear       : {result['fear_indicators']}")
    print(f"  Authority  : {result['authority_impersonation']}")
    print(f"  Urgency    : {result['urgency_signals']}")
    print(f"  Financial  : {result['financial_pressure']}")
