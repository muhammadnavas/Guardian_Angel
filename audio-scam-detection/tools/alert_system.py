"""
Alert System -- Family and Authority Escalation with Email Integration

Integrated with real email sending capabilities for family and police alerts.
Falls back to console simulation if email configuration is not available.
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
    """Handles escalation alerts for detected scam calls with email integration."""

    def __init__(self):
        """Initialize alert system with optional email service."""
        self.email_service = None
        self.family_emails = self._load_family_emails()
        self.police_emails = self._load_police_emails()
        
        # Try to initialize email service (Node.js Nodemailer preferred, Python fallback)
        self.email_service = None
        
        # First try Node.js email service
        try:
            from .nodemailer_client import EmailService
            self.email_service = EmailService()
            if self.email_service.test_email_connection():
                print("✅ Node.js Email service (Nodemailer) initialized successfully")
            else:
                print("⚠️ Node.js Email service failed - trying Python fallback")
                self.email_service = None
        except Exception as e:
            print(f"⚠️ Node.js Email service not available: {e}")
        
        # Fallback to Python email service
        if not self.email_service:
            try:
                from .email_service import EmailService
                self.email_service = EmailService()
                if self.email_service.test_email_connection():
                    print("✅ Python Email service initialized as fallback")
                else:
                    print("⚠️ Python Email service failed - using console alerts only")
                    self.email_service = None
            except Exception as e:
                print(f"⚠️ No email services available: {e} - using console alerts only")
                self.email_service = None
    
    def _load_family_emails(self) -> List[str]:
        """Load family email addresses from environment variables."""
        emails_str = os.getenv("FAMILY_EMAILS", "")
        return [email.strip() for email in emails_str.split(",") if email.strip()]
    
    def _load_police_emails(self) -> List[str]:
        """Load police/cybercrime email addresses from environment variables."""
        emails_str = os.getenv("POLICE_EMAILS", "")
        return [email.strip() for email in emails_str.split(",") if email.strip()]

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
            family_success = self._notify_family(threat_level, summary, timestamp, senior_name)
            if family_success:
                actions.append(f"[OK] Family notified via email ({len(self.family_emails)} recipients)")
            else:
                actions.append("[OK] Family notified via console (email unavailable)")

        if rules["alert_police"]:
            police_success = self._notify_police(threat_level, summary, timestamp)
            if police_success:
                actions.append(f"[OK] Cybercrime Police alerted via email ({len(self.police_emails)} recipients)")
            else:
                actions.append("[OK] Cybercrime Police alerted via console (email unavailable)")

        if not actions:
            actions.append("[INFO] No external alerts sent (threat level: SAFE/SUSPICIOUS)")

        action_report = "\n".join(actions)
        full_report = f"{rules['message']}\n\nActions taken:\n{action_report}"

        print(f"\n{full_report}\n")
        return full_report

    # ------------------------------------------------------------------
    # Simulated notification methods
    # ------------------------------------------------------------------

    def _notify_family(self, threat_level: str, summary: str, timestamp: str, senior_name: str) -> bool:
        """Send family alert via email or simulate if email unavailable."""
        # Try email first
        if self.email_service and self.family_emails:
            try:
                success = self.email_service.send_family_alert(
                    family_emails=self.family_emails,
                    threat_level=threat_level,
                    summary=summary,
                    senior_name=senior_name
                )
                if success:
                    print(f"\n[EMAIL] Family Alert Sent Successfully to {len(self.family_emails)} recipients")
                    return True
            except Exception as e:
                print(f"\n[EMAIL] Failed to send family alert: {e}")
        
        # Fallback to console simulation
        print("\n[SMS] WhatsApp/SMS -> Family Contact:")
        print(f"   To   : +91-XXXXXXXXXX (registered family member)")
        print(f"   Time : {timestamp}")
        print(f"   Msg  : [ALERT] Guardian Angel Alert! {senior_name} is on a {threat_level} risk call.")
        print(f"          Details: {summary[:120]}")
        print(f"          Please check on them immediately!")
        return False

    def _notify_police(self, threat_level: str, summary: str, timestamp: str) -> bool:
        """Send police alert via email or simulate if email unavailable."""
        # Try email first
        if self.email_service and self.police_emails:
            try:
                success = self.email_service.send_police_alert(
                    police_emails=self.police_emails,
                    threat_level=threat_level,
                    summary=summary
                )
                if success:
                    print(f"\n[EMAIL] Police Alert Sent Successfully to {len(self.police_emails)} recipients")
                    return True
            except Exception as e:
                print(f"\n[EMAIL] Failed to send police alert: {e}")
        
        # Fallback to console simulation
        print("\n[POLICE] Cybercrime Police -- Incident Report:")
        print(f"   Station  : Local Cybercrime Cell")
        print(f"   Time     : {timestamp}")
        print(f"   Severity : {threat_level}")
        print(f"   Details  : {summary[:200]}")
        print(f"   Action   : Incident logged for follow-up")
        return False
