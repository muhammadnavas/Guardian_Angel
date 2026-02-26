"""
Rule-Based Scam Detector

Analyses call transcripts for scam indicators using curated English,
Hindi, and Kannada (transliterated) keyword lists. Returns a structured
result with individual indicator categories and a 0-100 threat score.

Changelog:
- Fixed false positive: removed standalone 'ed' and 'officer' from authority
  list (triggered on non-scam words like 'Desk', 'verification officer').
  Replaced with longer phrase matches only.
- Added digital-arrest specific keywords: 'digital arrest', 'aadhaar',
  'remain on this call', 'legal action', 'escalated'.
- Added Kannada transliteration support.
- Added high-severity keyword bonus for digital-arrest phrases.
"""

import re
from typing import List


# ---------------------------------------------------------------------------
# Keyword lists (English + Hindi + Kannada transliterated)
# ---------------------------------------------------------------------------

FEAR_KEYWORDS_EN = [
    "arrest", "arrested", "digital arrest", "under arrest",
    "police", "crime", "criminal", "illegal",
    "fraud", "warrant", "jail", "prison", "sued", "lawsuit",
    "investigation", "fir", "case filed", "cybercrime",
    "court order", "government action", "seized", "detained",
    "legal action", "escalated for", "escalate the matter",
    "remain on this call", "remain available on this call",
    "do not disconnect", "cannot leave",
]

FEAR_KEYWORDS_HI = [
    "giraftari", "giraftar", "police", "fir", "kejar", "jail",
    "qanoon", "adalat", "criminal", "pakad", "case",
    "saza", "kaid", "warrant", "aarop",
    "kanoon", "cybercrime", "digital giraftari",
]

# Kannada transliteration (Roman script approximation of common Kannada scam phrases)
FEAR_KEYWORDS_KN = [
    "digital bandana", "digital bandhanada", "digtal arrest",
    "sajjana", "keisi", "arrest madutteve", "bandana",
    "cyber crime", "takshanadha", "takshana", "takshanave",
    "suchane anusarisabeku", "kayida kriya",
]

# Kannada Unicode script keywords (for direct Kannada text or Whisper-transcribed Kannada)
FEAR_KEYWORDS_KN_UNICODE = [
    "ಡಿಜಿಟಲ್ ಬಂಧನ",  # digital arrest
    "ಬಂಧನ",            # arrest/detention
    "ಸೈಬರ್ ಕ್ರೈಮ್",   # cybercrime
    "ಕ್ರಿಮಿನಲ್",       # criminal
    "ಕಾನೂನು ಕ್ರಮ",    # legal action
    "ಡಿಜಿಟಲ್",         # digital
    "ಆರೋಪ",            # accusation
    "ತಕ್ಷಣ",           # immediately
]

# Authority: PHRASE-BASED only (no single short tokens like 'ed' or 'officer')
AUTHORITY_KEYWORDS_EN = [
    "central bureau of investigation", "cbi officer", "cbi unit",
    "cyber crime unit", "cybercrime unit", "cyber crime cell",
    "enforcement directorate", "income tax department", "income tax officer",
    "customs department", "customs officer", "narcotics control",
    "trai", "telecom regulatory", "supreme court", "high court",
    "government of india", "rbi", "sebi", "interpol",
    "commissioner of police", "national security", "cyber police",
    "compliance review", "verification officer",  # common scam phrases
    "inspector", "ips officer", "ias officer",
    "ministry of", "home ministry",
]

AUTHORITY_KEYWORDS_HI = [
    "cbi", "trai", "sarkar", "mantri",
    "collector", "commissioner", "adhikari", "enforcement directorate",
    "income tax", "customs vibhag",
    "supreme court", "high court", "cyber police",
]

AUTHORITY_KEYWORDS_KN = [
    "cyber crime vibhaga", "takshanadha",
    "cbi adhikari", "police adhikari",
    "sarkar", "nyayalaya",
    "commissioner", "inspector",
]

# Kannada Unicode authority keywords
AUTHORITY_KEYWORDS_KN_UNICODE = [
    "ಸೈಬರ್ ಕ್ರೈಮ್ ಘಟಕ",  # Cyber Crime Unit
    "ಇನ್ಸ್ ಪೆಕ್ಟರ್",      # Inspector
    "ಸರ್ಕಾರ",              # Government
    "ನ್ಯಾಯಾಲಯ",           # Court
    "ಆಧಾರ್",               # Aadhaar
]

URGENCY_KEYWORDS_EN = [
    "immediately", "right now", "within 24 hours", "urgent",
    "do not delay", "last warning", "final notice", "today only",
    "in the next hour", "within minutes", "before it's too late",
    "deadline", "no time left", "act now", "emergency",
    "do not hang up", "stay on the line", "remain on this call",
    "remain available on this call", "avoid automated",
    "automated system escalation", "must follow instructions",
    "otherwise the matter will be escalated",
    "cannot be delayed", "must not disconnect",
]

URGENCY_KEYWORDS_HI = [
    "abhi", "turant", "jaldi", "der mat karo", "aaj hi",
    "kal tak", "call mat kaatna", "ruko mat", "baad mein nahi",
    "aakhri mauka", "warning", "emergency", "sirf aaj",
    "fauran", "der karne par",
]

URGENCY_KEYWORDS_KN = [
    "takshana", "takshanadha", "ippude", "bega",
    "delay madabeda", "call kaiyodu", "takshanave",
]

# Kannada Unicode urgency keywords
URGENCY_KEYWORDS_KN_UNICODE = [
    "ತಕ್ಷಣ",                           # immediately
    "ಸೂಚನೆಗಳನ್ನು ಅನುಸರಿಸಬೇಕು",      # must follow instructions
    "ಕರೆಯಲ್ಲಿ ಉಳಿದು",                # remain on the call
    "ವಿಷಯವನ್ನು ಹೆಚ್ಚಿಸಲಾಗುವುದು",    # matter will be escalated
]

FINANCIAL_KEYWORDS_EN = [
    "send money", "transfer money", "wire transfer", "pay fine",
    "bank account", "bitcoin", "gift card", "amazon card",
    "cash deposit", "clear your dues", "upfront payment",
    "advance payment", "security deposit", "freeze your account",
    "account will be frozen", "account will be blocked",
    "pay immediately", "rupees", "dollars", "lakh", "crore",
    "payment required", "fine to be paid",
]

FINANCIAL_KEYWORDS_HI = [
    "paise bhejo", "transfer karo", "account mein dalo",
    "fine bharo", "jama karo", "bank account band",
    "froze", "rupaye", "lakh", "crore", "paisa",
    "payment", "advance", "guarantee deposit",
]

FINANCIAL_KEYWORDS_KN = [
    "hortu madabeku", "paise", "account freeze",
    "dakshina", "harishavanu",
]

# Kannada Unicode financial keywords
FINANCIAL_KEYWORDS_KN_UNICODE = [
    "ಹಣ",          # money
    "ಪಾವತಿ",       # payment
    "ಖಾತೆ",        # account
    "ರೂಪಾಯಿ",      # rupee
]

# High-severity phrases — any single match gives a major score boost
HIGH_SEVERITY_PHRASES = [
    "digital arrest",
    "under digital arrest",
    "you are under arrest",
    "warrant has been issued",
    "arrested for money laundering",
    "drug trafficking",
    "aadhaar has been used",
    "aadhaar linked to",
    "illegal use of aadhaar",
    "remain on this call",
    "do not disconnect",
    "do not hang up",
    "immediate legal action",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_matches(text: str, keywords: List[str]) -> List[str]:
    """Return keyword matches found in text (case-insensitive, phrase-aware)."""
    text_lower = text.lower()
    # Use word boundary matching for short tokens (<=6 chars) to avoid false positives
    results = []
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower) <= 5:
            # Require word boundaries to prevent 'ed' matching inside 'needed'
            if re.search(r'\b' + re.escape(kw_lower) + r'\b', text_lower):
                results.append(kw)
        else:
            if kw_lower in text_lower:
                results.append(kw)
    return results


def _count_high_severity(text: str) -> int:
    """Count how many high-severity phrases appear in the text."""
    text_lower = text.lower()
    return sum(1 for phrase in HIGH_SEVERITY_PHRASES if phrase.lower() in text_lower)


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class ScamDetector:
    """
    Rule-based scam detector for phone call transcripts.

    Supports: English, Hindi (transliterated), Kannada (transliterated).
    Analyses four indicator categories and aggregates into a 0-100 threat score.
    """

    # Score weights per category
    _WEIGHTS = {
        "fear": 25,
        "authority": 25,
        "urgency": 25,
        "financial": 25,
    }

    def analyze_text(self, text: str) -> dict:
        """Analyse transcript text for scam indicators.

        Args:
            text: Call transcript (English, Hindi, Kannada transliterated, or Kannada Unicode).

        Returns:
            dict with keys:
                fear_indicators        - list of matched fear keywords
                authority_impersonation - list of matched authority keywords
                urgency_signals        - list of matched urgency keywords
                financial_pressure     - list of matched financial keywords
                threat_score           - int 0-100
                high_severity_count    - int, count of critical phrase hits
        """
        if not text or not isinstance(text, str):
            return self._empty_result()

        # Strip language tag if present
        clean_text = re.sub(r"\[Language:.*?\]", "", text).strip()

        all_fear = (FEAR_KEYWORDS_EN + FEAR_KEYWORDS_HI
                    + FEAR_KEYWORDS_KN + FEAR_KEYWORDS_KN_UNICODE)
        all_authority = (AUTHORITY_KEYWORDS_EN + AUTHORITY_KEYWORDS_HI
                         + AUTHORITY_KEYWORDS_KN + AUTHORITY_KEYWORDS_KN_UNICODE)
        all_urgency = (URGENCY_KEYWORDS_EN + URGENCY_KEYWORDS_HI
                       + URGENCY_KEYWORDS_KN + URGENCY_KEYWORDS_KN_UNICODE)
        all_financial = (FINANCIAL_KEYWORDS_EN + FINANCIAL_KEYWORDS_HI
                         + FINANCIAL_KEYWORDS_KN + FINANCIAL_KEYWORDS_KN_UNICODE)

        fear = _find_matches(clean_text, all_fear)
        authority = _find_matches(clean_text, all_authority)
        urgency = _find_matches(clean_text, all_urgency)
        financial = _find_matches(clean_text, all_financial)
        high_sev = _count_high_severity(clean_text)

        threat_score = self._compute_score(fear, authority, urgency, financial, high_sev)

        return {
            "fear_indicators": list(set(fear)),
            "authority_impersonation": list(set(authority)),
            "urgency_signals": list(set(urgency)),
            "financial_pressure": list(set(financial)),
            "threat_score": threat_score,
            "high_severity_count": high_sev,
        }

    def get_threat_level(self, threat_score: int) -> str:
        """Map a numeric threat score to a threat level label.

        Returns:
            One of: SAFE, SUSPICIOUS, HIGH_RISK, CRITICAL
        """
        if threat_score >= 75:
            return "CRITICAL"
        elif threat_score >= 50:
            return "HIGH_RISK"
        elif threat_score >= 25:
            return "SUSPICIOUS"
        else:
            return "SAFE"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_score(
        self,
        fear: list,
        authority: list,
        urgency: list,
        financial: list,
        high_sev: int = 0,
    ) -> int:
        """Compute a 0-100 threat score from the four indicator lists."""
        score = 0

        # Each category contributes up to its weight (capped at 2 matches)
        def _contribution(matches: list, weight: int) -> float:
            hits = min(len(matches), 2)
            return (hits / 2) * weight

        score += _contribution(fear, self._WEIGHTS["fear"])
        score += _contribution(authority, self._WEIGHTS["authority"])
        score += _contribution(urgency, self._WEIGHTS["urgency"])
        score += _contribution(financial, self._WEIGHTS["financial"])

        # Multi-category bonus: 2+ categories triggered → +10
        triggered = sum(bool(lst) for lst in [fear, authority, urgency, financial])
        if triggered >= 2:
            score += 10

        # High-severity phrase bonus: each match adds 15 points (capped at 2)
        score += min(high_sev, 2) * 15

        return min(int(score), 100)

    @staticmethod
    def _empty_result() -> dict:
        return {
            "fear_indicators": [],
            "authority_impersonation": [],
            "urgency_signals": [],
            "financial_pressure": [],
            "threat_score": 0,
            "high_severity_count": 0,
        }
