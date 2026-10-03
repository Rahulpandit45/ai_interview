"""
email_service.py
Enterprise-grade email dispatch service for AI-Powered Video Interview Assessment System.
Supports real-time delivery via Resend API (HTTP REST) and authenticated SMTP.
Candidates register with ANY email address (Gmail, Yahoo, Outlook, university, etc.)
without needing any sender passwords, app passwords, or 2FA setup.
"""

import os
import ssl
import time
import socket
import smtplib
import logging
import requests
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import Config

logger = logging.getLogger("EmailService")


class EmailDispatchResult:
    """
    Structured dispatch result that supports boolean checks (if result:),
    tuple unpacking (success, msg, details = result), and attribute access.
    """
    def __init__(self, success: bool, message: str, error_code: str = None, details: dict = None):
        self.success = bool(success)
        self.message = str(message)
        self.error_code = error_code
        self.details = details or {}

    def __bool__(self):
        return self.success

    def __iter__(self):
        return iter((self.success, self.message, self.details))

    def __repr__(self):
        return f"<EmailDispatchResult success={self.success} code={self.error_code} msg='{self.message}'>"

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class EmailService:
    @classmethod
    def send_verification_email(
        cls,
        to_email: str,
        candidate_name: str,
        otp_code: str = None,
        verification_link: str = None
    ) -> EmailDispatchResult:
        """
        Dispatches a professional, responsive HTML verification email containing:
        1. A one-click 'Verify Email Address' button (if verification_link provided)
        2. A 6-digit verification code (if otp_code provided)
        Uses Resend API as the primary modern provider, with SMTP fallback.
        """
        clean_email = to_email.strip().lower()
        display_name = candidate_name.strip() if candidate_name and candidate_name.strip() else "Candidate"

        # Automated test harness mock check
        try:
            from flask import current_app
            if current_app and current_app.config.get("TESTING", False):
                return EmailDispatchResult(
                    success=True,
                    message=f"[TEST MOCK] Verification email sent to {clean_email}.",
                    details={"provider": "test_mock"}
                )
        except Exception:
            pass

        subject = "AI Interview - Verify Your Email Address"
        expire_minutes = getattr(Config, "VERIFICATION_LINK_EXPIRE_MINUTES", 15)

        # Build Plain Text Content
        text_lines = [
            f"Hello {display_name},",
            "",
            "Thank you for registering on the AI-Powered Intelligent Video Interview Assessment System.",
            ""
        ]

        if verification_link:
            text_lines.extend([
                "Click the link below to verify your email address and continue:",
                f"    {verification_link}",
                ""
            ])

        if otp_code:
            text_lines.extend([
                f"Alternatively, enter this 6-digit verification code:",
                f"    {otp_code}",
                ""
            ])

        text_lines.extend([
            f"This link and code will expire in {expire_minutes} minutes.",
            "",
            "SECURITY NOTICE:",
            "Never share this verification code or link with anyone.",
            "If you did not request this email, you can safely ignore it.",
            "",
            "---",
            "Department of Computer Engineering • Mid-West University, Surkhet, Nepal",
            "AI Video Interview Assessment Platform"
        ])
        text_content = "\n".join(text_lines)

        # Build Link Button HTML if provided
        link_html_block = ""
        if verification_link:
            link_html_block = f"""
              <!-- One-Click Verification Button -->
              <div style="text-align: center; margin: 28px 0 16px;">
                <a href="{verification_link}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 700; padding: 14px 38px; border-radius: 10px; box-shadow: 0 4px 20px rgba(79, 70, 229, 0.45); letter-spacing: 0.3px;">
                  Verify Email Address &rarr;
                </a>
              </div>
              <p style="color: #64748b; font-size: 12px; text-align: center; margin: 0 0 24px; word-break: break-all; line-height: 1.5;">
                Or copy and paste this link into your browser:<br>
                <a href="{verification_link}" style="color: #818cf8; text-decoration: underline;">{verification_link}</a>
              </p>
            """

        # Build OTP Box HTML if provided
        otp_html_block = ""
        if otp_code:
            divider_text = "Alternatively, enter your 6-digit code:" if verification_link else "Your verification code:"
            otp_html_block = f"""
              <div style="text-align: center; margin: 18px 0 10px; border-top: 1px dashed rgba(255, 255, 255, 0.12); padding-top: 18px;">
                <span style="color: #94a3b8; font-size: 13px; font-weight: 500;">{divider_text}</span>
              </div>
              <!-- 6-Digit OTP Highlight Box -->
              <div style="background-color: #1e1e38; border: 1.5px solid #6366f1; border-radius: 12px; padding: 18px 16px; text-align: center; margin: 12px auto 20px; max-width: 320px;">
                <div style="font-size: 34px; font-weight: 800; letter-spacing: 10px; color: #ffffff; font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; margin-left: 10px;">
                  {otp_code}
                </div>
                <div style="font-size: 12px; color: #34d399; font-weight: 600; margin-top: 6px;">
                  ⏱️ Expires in {expire_minutes} minutes &bull; Single-use
                </div>
              </div>
            """

        # High-end responsive HTML email template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Interview - Email Verification</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b0f19; padding: 40px 15px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table role="presentation" width="100%" max-width="540" style="max-width: 540px; background-color: #111827; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; overflow: hidden; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);">
          
          <!-- Gradient Brand Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 28px 32px; text-align: center;">
              <div style="font-size: 32px; line-height: 1;">⚡</div>
              <h1 style="color: #ffffff; font-size: 21px; font-weight: 800; margin: 8px 0 2px; letter-spacing: -0.3px;">
                AI Video Interview System
              </h1>
              <div style="color: rgba(255, 255, 255, 0.88); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;">
                Talent Assessment &bull; Automated Interview Platform
              </div>
            </td>
          </tr>

          <!-- Email Content Body -->
          <tr>
            <td style="padding: 36px 32px 28px;">
              <h2 style="color: #f8fafc; font-size: 18px; font-weight: 700; margin: 0 0 14px;">
                Verify Your Email Address
              </h2>
              <p style="color: #94a3b8; font-size: 15px; line-height: 1.6; margin: 0 0 16px;">
                Hello <strong style="color: #f8fafc;">{display_name}</strong>,<br>
                Please verify your email address to complete your registration for the AI Video Interview platform.
              </p>

              {link_html_block}
              {otp_html_block}

              <!-- Security Information -->
              <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid #6366f1; border-radius: 6px; padding: 12px 16px; margin: 24px 0 20px;">
                <div style="color: #cbd5e1; font-size: 13px; line-height: 1.5;">
                  🔒 <strong>Security Notice:</strong> Never share your verification link or code with anyone. System administrators will never ask for your verification credentials.
                </div>
              </div>

              <p style="color: #64748b; font-size: 13px; line-height: 1.5; margin: 20px 0 0;">
                If you did not create an account on AI Interview, you can safely ignore this email. No account will be activated without verification.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0b0f19; border-top: 1px solid rgba(255, 255, 255, 0.06); padding: 20px 32px; text-align: center;">
              <p style="color: #475569; font-size: 11.5px; margin: 0; line-height: 1.5;">
                AI-Powered Intelligent Video Interview Assessment System<br>
                Department of Computer Engineering &bull; Mid-West University, Surkhet, Nepal<br>
                This is an automated system message. Please do not reply to this email.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        provider = getattr(Config, "EMAIL_PROVIDER", "smtp").lower()

        # Build RFC 5322 MIME message container
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.get_formatted_sender()
        msg["To"] = clean_email
        msg["Reply-To"] = Config.get_envelope_sender()
        msg["Date"] = email.utils.formatdate(localtime=True)
        sender_domain = Config.get_envelope_sender().split("@")[-1] if "@" in Config.get_envelope_sender() else "interview.ai"
        msg["Message-ID"] = email.utils.make_msgid(domain=sender_domain)
        msg["X-Mailer"] = "AI-Interview-Assessment-Platform/2026.1"
        msg["Auto-Submitted"] = "auto-generated"
        msg["Precedence"] = "transactional"
        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        envelope_from = Config.get_envelope_sender()

        # Provider Branch 1: SMTP Delivery (Standard & Recommended)
        if provider == "smtp":
            if Config.is_smtp_configured():
                return cls._deliver_via_smtp(envelope_from, clean_email, msg, otp_code)
            elif Config.is_resend_configured():
                return cls._deliver_via_resend(clean_email, subject, html_content, text_content)
            else:
                if Config.is_production():
                    return EmailDispatchResult(
                        success=False,
                        message="SMTP email service is not configured. Please set MAIL_USERNAME and MAIL_PASSWORD (16-character Google App Password) in your .env file.",
                        error_code="SMTP_NOT_CONFIGURED"
                    )
                else:
                    print("=" * 72)
                    print(f"  [DEVELOPMENT NOTICE - SMTP CREDENTIALS NOT SET IN .env]")
                    print(f"  Candidate Email : {clean_email}")
                    if otp_code:
                        print(f"  Generated OTP   : {otp_code}")
                    if verification_link:
                        print(f"  Verification Link: {verification_link}")
                    print("  >> To send real emails via SMTP, set MAIL_USERNAME and MAIL_PASSWORD in .env")
                    print("=" * 72)
                    return EmailDispatchResult(
                        success=True,
                        message="Development mode active: OTP and verification link generated locally.",
                        error_code=None,
                        details={"dev_mode": True, "dev_code": otp_code, "verification_link": verification_link}
                    )

        # Provider Branch 2: Resend API Delivery
        elif provider == "resend":
            if Config.is_resend_configured():
                return cls._deliver_via_resend(clean_email, subject, html_content, text_content)
            elif Config.is_smtp_configured():
                return cls._deliver_via_smtp(envelope_from, clean_email, msg, otp_code)
            else:
                if Config.is_production():
                    return EmailDispatchResult(
                        success=False,
                        message="Email service is not configured. Please set RESEND_API_KEY in your .env file.",
                        error_code="EMAIL_PROVIDER_UNCONFIGURED"
                    )
                else:
                    print("=" * 72)
                    print(f"  [DEVELOPMENT NOTICE - RESEND_API_KEY NOT SET IN .env]")
                    print(f"  Candidate Email : {clean_email}")
                    if otp_code:
                        print(f"  Generated OTP   : {otp_code}")
                    if verification_link:
                        print(f"  Verification Link: {verification_link}")
                    print("  >> To send real emails, add RESEND_API_KEY or SMTP credentials to .env")
                    print("=" * 72)
                    return EmailDispatchResult(
                        success=True,
                        message="Development mode active: OTP generated locally.",
                        error_code=None,
                        details={"dev_mode": True, "dev_code": otp_code, "verification_link": verification_link}
                    )

        # Fallback if unconfigured
        if Config.is_production():
            return EmailDispatchResult(
                success=False,
                message="No email provider configured. Please set MAIL_USERNAME and MAIL_PASSWORD in .env.",
                error_code="EMAIL_PROVIDER_UNCONFIGURED"
            )
        else:
            return EmailDispatchResult(
                success=True,
                message="Development mode: OTP generated locally.",
                error_code=None,
                details={"dev_mode": True, "dev_code": otp_code, "verification_link": verification_link}
            )

    @classmethod
    def send_otp_email(
        cls,
        to_email: str,
        candidate_name: str,
        otp_code: str,
        verification_link: str = None
    ) -> EmailDispatchResult:
        """
        Dispatches a professional, responsive HTML verification email containing the 6-digit OTP
        and optional one-click verification link.
        """
        clean_email = to_email.strip().lower()
        display_name = candidate_name.strip() if candidate_name and candidate_name.strip() else "Candidate"
        return cls.send_verification_email(
            to_email=clean_email,
            candidate_name=display_name,
            otp_code=otp_code,
            verification_link=verification_link
        )

    @classmethod
    def _deliver_via_resend(cls, to_email: str, subject: str, html_content: str, text_content: str) -> EmailDispatchResult:
        """
        Transmits email via the Resend REST API (https://api.resend.com/emails).
        Authenticated using RESEND_API_KEY from .env.
        Supports sending to ANY email address.
        """
        api_key = getattr(Config, "RESEND_API_KEY", "").strip()
        if not api_key:
            return EmailDispatchResult(
                success=False,
                message="RESEND_API_KEY is empty in .env. Please configure your Resend API Key.",
                error_code="RESEND_API_KEY_MISSING"
            )

        sender_from = getattr(Config, "EMAIL_FROM", "AI Interview <onboarding@resend.dev>").strip()
        if not sender_from:
            sender_from = "AI Interview <onboarding@resend.dev>"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": sender_from,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }

        timeout = getattr(Config, "MAIL_TIMEOUT", 12)
        try:
            print(f"[Resend] Sending real-time verification email to {to_email} via Resend API (from: {sender_from})...")
            resp = requests.post(
                "https://api.resend.com/emails",
                json=payload,
                headers=headers,
                timeout=timeout
            )

            if resp.status_code in [200, 201]:
                res_data = resp.json()
                msg_id = res_data.get("id", "resend_ok")
                print(f"[Resend] Email successfully dispatched to {to_email}! (Message ID: {msg_id})")
                return EmailDispatchResult(
                    success=True,
                    message=f"Verification email successfully delivered to {to_email}.",
                    details={"provider": "resend", "id": msg_id}
                )
            else:
                err_detail = resp.text
                try:
                    err_json = resp.json()
                    err_detail = err_json.get("message", resp.text)
                except Exception:
                    pass

                if resp.status_code == 401:
                    user_msg = "Resend API authentication failed: Invalid RESEND_API_KEY in .env."
                    code = "AUTH_FAILED"
                elif resp.status_code in [403, 422]:
                    if "domain" in str(err_detail).lower() or "verify" in str(err_detail).lower():
                        user_msg = f"Resend notice: {err_detail}. To send without domain verification, set EMAIL_FROM=AI Interview <onboarding@resend.dev>."
                    else:
                        user_msg = f"Resend delivery error: {err_detail}"
                    code = "RESEND_REJECTED"
                else:
                    user_msg = f"Resend API error ({resp.status_code}): {err_detail}"
                    code = "RESEND_ERROR"

                print(f"[Resend Error] {user_msg}")
                return EmailDispatchResult(
                    success=False,
                    message=user_msg,
                    error_code=code,
                    details={"provider": "resend", "status_code": resp.status_code, "raw": err_detail}
                )

        except requests.exceptions.Timeout:
            err_msg = f"Resend API connection timed out after {timeout} seconds."
            print(f"[Resend Error] {err_msg}")
            return EmailDispatchResult(success=False, message=err_msg, error_code="TIMEOUT")
        except requests.exceptions.ConnectionError as e:
            err_msg = f"Could not connect to Resend API. Check your internet connection: {e}"
            print(f"[Resend Error] {err_msg}")
            return EmailDispatchResult(success=False, message=err_msg, error_code="CONNECTION_ERROR")
        except Exception as e:
            err_msg = f"Unexpected error dispatching via Resend: {e}"
            print(f"[Resend Error] {err_msg}")
            return EmailDispatchResult(success=False, message=err_msg, error_code="RESEND_ERROR")

    @classmethod
    def _deliver_via_smtp(cls, envelope_from: str, to_email: str, msg: MIMEMultipart, otp_code_for_fallback: str) -> EmailDispatchResult:
        """
        Executes SMTP transmission to dynamic candidate recipient with dual-port failover (587 STARTTLS <-> 465 SSL).
        Supports Gmail, Outlook, Yahoo, and university / corporate SMTP servers.
        """
        clean_recipient = to_email.strip().lower()
        recipients = [clean_recipient]  # Dynamic recipient list: NEVER hardcoded or restricted to sandbox

        primary_server = Config.MAIL_SERVER
        primary_port = Config.MAIL_PORT
        primary_use_ssl = Config.MAIL_USE_SSL
        primary_use_tls = Config.MAIL_USE_TLS
        timeout = getattr(Config, "MAIL_TIMEOUT", 12)
        auto_fallback = getattr(Config, "MAIL_AUTO_FALLBACK", True)

        attempts = [{
            "server": primary_server,
            "port": primary_port,
            "ssl": primary_use_ssl,
            "tls": primary_use_tls
        }]

        if auto_fallback:
            if primary_port == 587 or (not primary_use_ssl and primary_use_tls):
                attempts.append({"server": primary_server, "port": 465, "ssl": True, "tls": False})
            elif primary_port == 465 or primary_use_ssl:
                attempts.append({"server": primary_server, "port": 587, "ssl": False, "tls": True})

        last_error_message = ""
        last_error_code = ""
        last_details = {}

        for idx, cfg in enumerate(attempts):
            server_inst = None
            try:
                protocol_name = "SSL direct (port 465)" if cfg["ssl"] else "STARTTLS (port 587)"
                print(f"[SMTP] Sending verification email to {clean_recipient} via {cfg['server']}:{cfg['port']} ({protocol_name})...")

                if cfg["ssl"]:
                    context = ssl.create_default_context()
                    server_inst = smtplib.SMTP_SSL(cfg["server"], cfg["port"], context=context, timeout=timeout)
                else:
                    server_inst = smtplib.SMTP(cfg["server"], cfg["port"], timeout=timeout)
                    server_inst.ehlo()
                    if cfg["tls"]:
                        context = ssl.create_default_context()
                        server_inst.starttls(context=context)
                        server_inst.ehlo()

                server_inst.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server_inst.sendmail(envelope_from, recipients, msg.as_string())
                server_inst.quit()

                print(f"[SMTP] Successfully delivered verification email to {clean_recipient} via {cfg['server']}:{cfg['port']}!")
                return EmailDispatchResult(
                    success=True,
                    message=f"Verification email successfully dispatched to {clean_recipient}.",
                    details={"provider": "smtp", "server": cfg["server"], "port": cfg["port"], "recipient": clean_recipient}
                )

            except smtplib.SMTPAuthenticationError as e:
                is_gmail = "gmail.com" in cfg["server"].lower()
                if is_gmail:
                    last_error_message = (
                        "Gmail authentication failed. Please verify your MAIL_USERNAME and ensure you are using "
                        "a 16-character Google App Password (not your normal Google account password). "
                        "Generate one at https://myaccount.google.com/apppasswords."
                    )
                else:
                    last_error_message = f"SMTP Authentication failed for '{Config.MAIL_USERNAME}' on {cfg['server']}:{cfg['port']}. Please check your username and password."
                last_error_code = "AUTH_FAILED"
                last_details = {"error": str(e), "server": cfg["server"], "port": cfg["port"]}
                print(f"[SMTP Auth Error] {last_error_message}")
                break  # Auth error won't be resolved by changing port

            except (smtplib.SMTPConnectError, socket.timeout, TimeoutError, ConnectionRefusedError) as e:
                last_error_message = f"SMTP connection timed out or failed on {cfg['server']}:{cfg['port']}. Network or firewall may be blocking the port."
                last_error_code = "TIMEOUT"
                last_details = {"error": str(e), "server": cfg["server"], "port": cfg["port"]}
                print(f"[SMTP Connection Warning] Attempt {idx+1} failed ({cfg['server']}:{cfg['port']}): {e}")

            except smtplib.SMTPRecipientsRefused as e:
                last_error_message = f"The recipient address '{clean_recipient}' was rejected by the mail server ({cfg['server']})."
                last_error_code = "RECIPIENT_REFUSED"
                last_details = {"error": str(e), "recipient": clean_recipient}
                print(f"[SMTP Recipient Error] {last_error_message}")
                break

            except smtplib.SMTPSenderRefused as e:
                last_error_message = f"The sender address '{envelope_from}' was rejected by the mail server ({cfg['server']}). Ensure MAIL_USERNAME or MAIL_DEFAULT_SENDER matches your authenticated email."
                last_error_code = "SENDER_REFUSED"
                last_details = {"error": str(e), "sender": envelope_from}
                print(f"[SMTP Sender Error] {last_error_message}")
                break

            except (ssl.SSLError, ssl.CertificateError) as e:
                last_error_message = f"SSL/TLS handshake error while connecting to {cfg['server']}:{cfg['port']}: {e}"
                last_error_code = "SSL_ERROR"
                last_details = {"error": str(e), "server": cfg["server"], "port": cfg["port"]}
                print(f"[SMTP SSL Error] {last_error_message}")

            except smtplib.SMTPException as e:
                last_error_message = f"SMTP protocol error on {cfg['server']}:{cfg['port']}: {e}"
                last_error_code = "SMTP_ERROR"
                last_details = {"error": str(e), "server": cfg["server"], "port": cfg["port"]}
                print(f"[SMTP Protocol Error] {last_error_message}")

            except Exception as e:
                last_error_message = f"Unexpected error during SMTP email delivery: {e}"
                last_error_code = "DELIVERY_FAILED"
                last_details = {"error": str(e)}
                print(f"[SMTP Unexpected Error] {last_error_message}")

            finally:
                if server_inst:
                    try:
                        server_inst.close()
                    except Exception:
                        pass

        return EmailDispatchResult(
            success=False,
            message=last_error_message or "Failed to deliver email through SMTP server.",
            error_code=last_error_code or "DELIVERY_FAILED",
            details=last_details
        )

    @classmethod
    def test_email_connection(cls, test_recipient: str = None) -> EmailDispatchResult:
        """Diagnostic method to verify active email provider (SMTP or Resend)."""
        provider = getattr(Config, "EMAIL_PROVIDER", "smtp").lower()

        if provider == "smtp" or Config.is_smtp_configured():
            return cls._test_smtp_connection(test_recipient)
        elif provider == "resend" or Config.is_resend_configured():
            if not Config.is_resend_configured():
                return EmailDispatchResult(
                    success=False,
                    message="RESEND_API_KEY is not configured in .env.",
                    error_code="RESEND_API_KEY_MISSING"
                )
            if test_recipient:
                return cls.send_otp_email(test_recipient, "Diagnostic Test", "123456")

            # Validate API key via ping to Resend API
            try:
                headers = {"Authorization": f"Bearer {Config.RESEND_API_KEY}"}
                resp = requests.get("https://api.resend.com/api-keys", headers=headers, timeout=8)
                if resp.status_code == 200:
                    return EmailDispatchResult(
                        success=True,
                        message="Resend API key validated successfully. Ready for real-time email delivery.",
                        details={"provider": "resend", "status": "active"}
                    )
                else:
                    return EmailDispatchResult(
                        success=False,
                        message=f"Resend API key check failed: HTTP {resp.status_code} ({resp.text})",
                        error_code="AUTH_FAILED"
                    )
            except Exception as e:
                return EmailDispatchResult(success=False, message=f"Resend connection check failed: {e}", error_code="CONNECTION_ERROR")

        # Fallback to SMTP check
        return cls._test_smtp_connection(test_recipient)

    @classmethod
    def _test_smtp_connection(cls, test_recipient: str = None) -> EmailDispatchResult:
        if not Config.is_smtp_configured():
            return EmailDispatchResult(
                success=False,
                message="SMTP credentials are not configured in .env (MAIL_USERNAME / MAIL_PASSWORD).",
                error_code="SMTP_NOT_CONFIGURED"
            )
        if test_recipient:
            return cls.send_otp_email(test_recipient, "System Administrator", "123456")

        try:
            if Config.MAIL_USE_SSL:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT, context=context, timeout=Config.MAIL_TIMEOUT)
            else:
                server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT, timeout=Config.MAIL_TIMEOUT)
                server.ehlo()
                if Config.MAIL_USE_TLS:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                    server.ehlo()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.quit()
            return EmailDispatchResult(
                success=True,
                message=f"SMTP handshake succeeded on {Config.MAIL_SERVER}:{Config.MAIL_PORT} for {Config.MAIL_USERNAME}."
            )
        except smtplib.SMTPAuthenticationError as e:
            is_gmail = "gmail.com" in Config.MAIL_SERVER.lower()
            if is_gmail:
                msg = "Gmail authentication failed. Please verify your MAIL_USERNAME and ensure you are using a 16-character Google App Password (not your normal Google account password) from https://myaccount.google.com/apppasswords."
            else:
                msg = f"SMTP Authentication failed for '{Config.MAIL_USERNAME}'."
            return EmailDispatchResult(success=False, message=msg, error_code="AUTH_FAILED", details={"raw": str(e)})
        except Exception as e:
            return EmailDispatchResult(success=False, message=f"SMTP connection test failed: {e}", error_code="CONNECTION_FAILED", details={"raw": str(e)})

    @classmethod
    def send_password_reset_email(
        cls,
        to_email: str,
        user_name: str,
        reset_link: str,
        expires_in_minutes: int = 20
    ) -> EmailDispatchResult:
        """
        Dispatches a secure password reset email with responsive CTA button and fallback link.
        """
        clean_email = to_email.strip().lower()
        display_name = user_name.strip() if user_name and user_name.strip() else "Candidate"

        # Automated test harness mock check
        try:
            from flask import current_app
            if current_app and current_app.config.get("TESTING", False):
                return EmailDispatchResult(
                    success=True,
                    message=f"[TEST MOCK] Password reset email sent to {clean_email}.",
                    details={"provider": "test_mock", "reset_link": reset_link}
                )
        except Exception:
            pass

        subject = "AI Interview - Password Reset Request"

        text_content = f"""Hello {display_name},

We received a request to reset the password for your account on the AI-Powered Intelligent Video Interview Assessment System.

To choose a new password, click the link below:
    {reset_link}

This link is valid for {expires_in_minutes} minutes and can only be used once.

SECURITY NOTICE:
If you did not request a password reset, you can safely ignore this email. Your current password remains secure and unchanged.

---
Department of Computer Engineering • Mid-West University, Surkhet, Nepal
AI Video Interview Assessment Platform
"""

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Interview - Password Reset</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0b0f19; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" max-width="540" style="max-width: 540px; background-color: #111827; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; overflow: hidden; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);">
          
          <!-- Gradient Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); padding: 28px 32px; text-align: center;">
              <div style="font-size: 32px; line-height: 1;">🔑</div>
              <h1 style="color: #ffffff; font-size: 21px; font-weight: 800; margin: 8px 0 2px; letter-spacing: -0.3px;">
                Password Reset Request
              </h1>
              <div style="color: rgba(255, 255, 255, 0.88); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;">
                AI Video Interview Assessment System
              </div>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 36px 32px 28px;">
              <h2 style="color: #f8fafc; font-size: 18px; font-weight: 700; margin: 0 0 14px;">
                Hello {display_name},
              </h2>
              <p style="color: #94a3b8; font-size: 15px; line-height: 1.6; margin: 0 0 20px;">
                We received a request to reset your password. Click the button below to choose a new password:
              </p>

              <div style="text-align: center; margin: 28px 0 16px;">
                <a href="{reset_link}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); color: #ffffff; text-decoration: none; font-size: 16px; font-weight: 700; padding: 14px 38px; border-radius: 10px; box-shadow: 0 4px 20px rgba(79, 70, 229, 0.45); letter-spacing: 0.3px;">
                  Reset My Password &rarr;
                </a>
              </div>

              <p style="color: #64748b; font-size: 12px; text-align: center; margin: 0 0 24px; word-break: break-all; line-height: 1.5;">
                Or copy and paste this link into your browser:<br>
                <a href="{reset_link}" style="color: #818cf8; text-decoration: underline;">{reset_link}</a>
              </p>

              <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid #6366f1; border-radius: 6px; padding: 12px 16px; margin: 24px 0 20px;">
                <div style="color: #cbd5e1; font-size: 13px; line-height: 1.5;">
                  ⏱️ <strong>Note:</strong> This link is valid for {expires_in_minutes} minutes and can only be used once. If you did not make this request, you can safely ignore this email; your account remains secure.
                </div>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0b0f19; border-top: 1px solid rgba(255, 255, 255, 0.06); padding: 20px 32px; text-align: center;">
              <p style="color: #475569; font-size: 11.5px; margin: 0; line-height: 1.5;">
                AI-Powered Intelligent Video Interview Assessment System<br>
                Department of Computer Engineering &bull; Mid-West University, Surkhet, Nepal<br>
                This is an automated system message. Please do not reply.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        provider = getattr(Config, "EMAIL_PROVIDER", "smtp").lower()

        # Build MIME Message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = Config.get_formatted_sender()
        msg["To"] = clean_email
        msg["Reply-To"] = Config.get_envelope_sender()
        msg["Date"] = email.utils.formatdate(localtime=True)
        sender_domain = Config.get_envelope_sender().split("@")[-1] if "@" in Config.get_envelope_sender() else "interview.ai"
        msg["Message-ID"] = email.utils.make_msgid(domain=sender_domain)
        msg["X-Mailer"] = "AI-Interview-Assessment-Platform/2026.1"
        msg["Auto-Submitted"] = "auto-generated"
        msg["Precedence"] = "transactional"
        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        envelope_from = Config.get_envelope_sender()

        # 1. SMTP Delivery
        if provider == "smtp" and Config.is_smtp_configured():
            return cls._deliver_via_smtp(envelope_from, clean_email, msg, otp_code_for_fallback=None)
        elif provider == "resend" and Config.is_resend_configured():
            return cls._deliver_via_resend(clean_email, subject, html_content, text_content)
        elif Config.is_smtp_configured():
            return cls._deliver_via_smtp(envelope_from, clean_email, msg, otp_code_for_fallback=None)
        elif Config.is_resend_configured():
            return cls._deliver_via_resend(clean_email, subject, html_content, text_content)
        
        # Development fallback
        print("=" * 72)
        print(f"  [DEVELOPMENT - PASSWORD RESET LINK GENERATED]")
        print(f"  Recipient Email : {clean_email}")
        print(f"  Reset Link      : {reset_link}")
        print("  >> To send real emails, configure MAIL_USERNAME & MAIL_PASSWORD in .env")
        print("=" * 72)
        return EmailDispatchResult(
            success=True,
            message="Development mode active: Reset link generated locally.",
            error_code=None,
            details={"dev_mode": True, "reset_link": reset_link}
        )

    # Compatibility alias
    test_smtp_connection = test_email_connection
