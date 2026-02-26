"""
Alert System -- Family and Authority Escalation

Integrated alert system for family and police notifications via console simulation.
Provides escalation alerts for detected scam calls.
"""

import os
from datetime import datetime
from typing import List, Optional


# ---------------------------------------------------------------------------
# Escalation rules (all messages use ASCII to avoid Windows encoding issues)
# ---------------------------------------------------------------------------

_ESCALATION_RULES = {
    "SAFE": {
        "alert_family": False,
        "alert_police": False,
        "message": "[SAFE] Call appears SAFE. No action required.",
    },
    "SUSPICIOUS": {
        "alert_family": False,
        "alert_police": False,
        "message": (
            "[WARNING] SUSPICIOUS activity detected. "
            "Advise the senior NOT to share personal or financial details. "
            "Monitor the situation."
        ),
    },
    "HIGH_RISK": {
        "alert_family": True,
        "alert_police": False,
        "message": (
            "[HIGH RISK] HIGH RISK scam detected! "
            "Family members have been notified. "
            "Senior should end the call immediately and consult family."
        ),
    },
    "CRITICAL": {
        "alert_family": True,
        "alert_police": True,
        "message": (
            "[CRITICAL] CRITICAL THREAT -- SCAM CALL IN PROGRESS! "
            "Emergency alert sent to family AND local cybercrime police. "
            "Senior must HANG UP IMMEDIATELY. Do NOT share any information."
        ),
    },
}


class AlertSystem:
    """Handles escalation alerts for detected scam calls via console simulation."""

    def __init__(self):
        """Initialize alert system."""
        pass

    def escalate(self, threat_level: str, summary: str, senior_name: str = "the senior citizen") -> str:
        """Send appropriate alerts based on the detected threat level.

        Args:
            threat_level: One of SAFE / SUSPICIOUS / HIGH_RISK / CRITICAL
            summary: Brief description of the detected threat

        Returns:
            A string describing the actions taken.
        """
        rules = _ESCALATION_RULES.get(threat_level, _ESCALATION_RULES["SUSPICIOUS"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        actions: list[str] = []

        # Always log to console (simulates system logging)
        print(f"\n{'='*60}")
        print(f"[ALERT] GUARDIAN ANGEL ALERT [{timestamp}]")
        print(f"Threat Level : {threat_level}")
        print(f"Summary      : {summary}")
        print(f"{'='*60}")

        if rules["alert_family"]:
            self._notify_family(threat_level, summary, timestamp, senior_name)
            actions.append("[OK] Family notified via console simulation")

        if rules["alert_police"]:
            self._notify_police(threat_level, summary, timestamp)
            actions.append("[OK] Cybercrime Police alerted via console simulation")

        if not actions:
            actions.append("[INFO] No external alerts sent (threat level: SAFE/SUSPICIOUS)")

        action_report = "\n".join(actions)
        full_report = f"{rules['message']}\n\nActions taken:\n{action_report}"

        print(f"\n{full_report}\n")
        return full_report

    # ------------------------------------------------------------------
    # Simulated notification methods
    # ------------------------------------------------------------------

    def _notify_family(self, threat_level: str, summary: str, timestamp: str, senior_name: str) -> None:
        """Send family alert via console simulation."""
        print("\n[SMS] WhatsApp/SMS -> Family Contact:")
        print(f"   To   : +91-XXXXXXXXXX (registered family member)")
        print(f"   Time : {timestamp}")
        print(f"   Msg  : [ALERT] Guardian Angel Alert! {senior_name} is on a {threat_level} risk call.")
        print(f"          Details: {summary[:120]}")
        print(f"          Please check on them immediately!")

    def _notify_police(self, threat_level: str, summary: str, timestamp: str) -> None:
        """Send police alert via console simulation."""
        print("\n[POLICE] Cybercrime Police -- Incident Report:")
        print(f"   Station  : Local Cybercrime Cell")
        print(f"   Time     : {timestamp}")
        print(f"   Severity : {threat_level}")
        print(f"   Details  : {summary[:200]}")
        print(f"   Action   : Incident logged for follow-up")
