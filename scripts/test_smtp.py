#!/usr/bin/env python
"""
test_smtp.py
Production Email Deliverability Diagnostic Tool (Resend API & SMTP).
Tests API authentication, connection, and real email dispatch to any recipient.

Usage:
    python scripts/test_smtp.py                     # Test credentials & provider status
    python scripts/test_smtp.py candidate@gmail.com # Send real test OTP email
"""

import os
import sys

# Ensure root workspace is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.config import Config
from backend.services.email_service import EmailService

def main():
    print("=" * 76)
    print("  AI INTERVIEW SYSTEM - PRODUCTION EMAIL DIAGNOSTIC SUITE")
    print("=" * 76)
    print(f"  Environment:       {Config.APP_ENV.upper()} (Production={Config.is_production()})")
    print(f"  Active Provider:   {Config.EMAIL_PROVIDER.upper()}")
    print(f"  Sender 'From':     {Config.EMAIL_FROM}")
    print(f"  Resend API Key:    {'SET (length=' + str(len(Config.RESEND_API_KEY)) + ')' if Config.is_resend_configured() else '<EMPTY / NOT SET>'}")
    print(f"  SMTP Fallback:     {Config.MAIL_SERVER}:{Config.MAIL_PORT} (User={Config.MAIL_USERNAME or '<EMPTY>'})")
    print(f"  OTP Expiration:    {Config.OTP_EXPIRE_MINUTES} minutes")
    print(f"  Resend Cooldown:   {Config.OTP_RESEND_COOLDOWN_SECONDS} seconds")
    print(f"  Max Attempts:      {Config.OTP_MAX_ATTEMPTS}")
    print("=" * 76)

    target_recipient = sys.argv[1] if len(sys.argv) > 1 else None

    # Provider verification
    if Config.EMAIL_PROVIDER == "resend":
        if not Config.is_resend_configured():
            print("\n[!] NOTICE: RESEND_API_KEY is not configured in .env!")
            print("    To send real emails to ANY candidate (Gmail, Outlook, Yahoo, etc.):")
            print("    1. Sign up for free at https://resend.com")
            print("    2. Create an API Key in the Resend dashboard (takes 10 seconds)")
            print("    3. Paste it in e:\\project\\.env:")
            print("       RESEND_API_KEY=re_your_api_key_here\n")
            return 1
        
        print("\n[Step 1/2] Verifying Resend API Key...")
        check_res = EmailService.test_email_connection()
        if not check_res.success:
            print(f"  [FAIL] {check_res.message}")
            return 1
        print(f"  [OK] Resend API key is active and ready!")

    else:
        # SMTP Provider check
        if not Config.is_smtp_configured():
            print("\n[!] NOTICE: SMTP is not configured in .env!")
            print("    Set MAIL_USERNAME and MAIL_PASSWORD in .env or switch to EMAIL_PROVIDER=resend\n")
            return 1

    # Send test email if recipient passed
    if target_recipient:
        from backend.utils.security import generate_email_verification_link
        link_token, link_url = generate_email_verification_link(target_recipient, base_url=Config.APP_BASE_URL)
        print(f"\n[Step 2/2] Sending Live Verification Email to: {target_recipient}...")
        print(f"  Generated Verification Link: {link_url}")
        dispatch_res = EmailService.send_verification_email(
            to_email=target_recipient,
            candidate_name="System Diagnostic Test",
            otp_code=None,
            verification_link=link_url
        )
        print("\n" + "=" * 76)
        if dispatch_res.success:
            print(f"  [SUCCESS] {dispatch_res.message}")
            print(f"  >> Verification link sent to {target_recipient}!")
            print(f"  >> Direct Click Link: {link_url}")
        else:
            print(f"  [ERROR] {dispatch_res.message}")
            if dispatch_res.error_code:
                print(f"  Error Code: {dispatch_res.error_code}")
        print("=" * 76 + "\n")
        return 0 if dispatch_res.success else 1
    else:
        print("\n[Step 2/2] Ready to test dispatch.")
        print("  >> Run with a recipient to send an actual email:")
        print(f"     python scripts/test_smtp.py your_email@example.com\n")
        return 0

if __name__ == "__main__":
    sys.exit(main())
