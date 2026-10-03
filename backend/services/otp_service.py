"""
otp_service.py
Core business service for cryptographically secure Email OTP generation,
hashing, validation, rate limiting, and verification token issuance.
"""

import re
import secrets
from datetime import datetime, timedelta
from backend.services.database import db
from backend.models.user import User
from backend.models.otp import EmailOTP
from backend.services.email_service import EmailService
from backend.utils.security import (
    generate_verification_token,
    generate_email_verification_link,
    verify_email_link_token
)
from backend.utils.helpers import utc_now
from backend.config import Config

class OTPService:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def generate_secure_otp() -> str:
        """Generates a secure 6-digit numeric OTP."""
        return f"{secrets.randbelow(900000) + 100000:06d}"

    @classmethod
    def send_registration_otp(cls, email: str, full_name: str):
        """
        Validates email, checks existing users and cooldown, generates and hashes
        a 6-digit OTP, dispatches the email, and stores only the hash in the database.
        Never returns or logs the plaintext OTP.
        """
        clean_email = email.strip().lower()
        clean_name = full_name.strip() if full_name else "Candidate"

        if not clean_email or not cls.is_valid_email(clean_email):
            return {"status": "error", "message": "Please provide a valid email address.", "code": "INVALID_EMAIL"}, 400

        # Check if email is already registered
        if User.query.filter_by(email=clean_email).first():
            return {
                "status": "error",
                "message": "An account with this email address already exists. Please sign in instead.",
                "code": "EMAIL_EXISTS"
            }, 409

        # Check resend rate limit / cooldown
        cooldown_secs = getattr(Config, "OTP_RESEND_COOLDOWN_SECONDS", 60)
        recent_active = EmailOTP.query.filter_by(
            email=clean_email, is_used=False
        ).order_by(EmailOTP.id.desc()).first()

        if recent_active and recent_active.created_at:
            elapsed = (utc_now() - recent_active.created_at).total_seconds()
            if elapsed < cooldown_secs:
                remaining = int(cooldown_secs - elapsed)
                return {
                    "status": "error",
                    "message": f"Please wait {remaining} seconds before requesting a new verification code.",
                    "cooldown_seconds": remaining,
                    "code": "COOLDOWN_ACTIVE"
                }, 429

        # Require email provider to be configured in production
        if Config.is_production() and not Config.is_email_configured():
            from flask import current_app
            is_testing = current_app and current_app.config.get("TESTING", False)
            if not is_testing:
                return {
                    "status": "error",
                    "message": "Real-time email verification is not configured. Please set RESEND_API_KEY in your .env file to dispatch verification emails.",
                    "code": "EMAIL_PROVIDER_UNCONFIGURED"
                }, 503

        # Invalidate any existing unused OTPs for this candidate email
        EmailOTP.query.filter_by(email=clean_email, is_used=False).update({"is_used": True})

        # Generate fresh 6-digit OTP
        otp_plain = cls.generate_secure_otp()
        expiry_minutes = getattr(Config, "OTP_EXPIRE_MINUTES", getattr(Config, "OTP_EXPIRY_MINUTES", 5))
        now = utc_now()
        expires_at = now + timedelta(minutes=expiry_minutes)

        # Create record with hashed OTP
        otp_record = EmailOTP(
            email=clean_email,
            expires_at=expires_at,
            created_at=now,
            last_sent_at=now,
            attempts=0,
            is_used=False,
            purpose="candidate_registration"
        )
        otp_record.set_otp(otp_plain)
        db.session.add(otp_record)
        db.session.commit()

        # Generate verification link
        link_expire = getattr(Config, "VERIFICATION_LINK_EXPIRE_MINUTES", 15)
        link_token, verification_url = generate_email_verification_link(
            clean_email,
            base_url=getattr(Config, "APP_BASE_URL", "http://localhost:5000"),
            expires_in_minutes=link_expire
        )

        # Dispatch email with one-click verification link ONLY (no OTP code sent)
        dispatch_result = EmailService.send_verification_email(
            to_email=clean_email,
            candidate_name=clean_name,
            otp_code=None,
            verification_link=verification_url
        )

        # Handle delivery failure
        if not dispatch_result.success:
            if Config.is_production():
                # Rollback OTP record on delivery failure so candidate is not locked by cooldown
                db.session.delete(otp_record)
                db.session.commit()
                return {
                    "status": "error",
                    "message": f"Failed to deliver verification email to {clean_email}: {dispatch_result.message}",
                    "code": dispatch_result.error_code or "EMAIL_DELIVERY_FAILED",
                    "details": dispatch_result.details
                }, 502

        # Success response construction
        resp = {
            "status": "success",
            "message": f"A verification link has been sent to {clean_email}. Please check your inbox.",
            "email": clean_email,
            "expires_in_seconds": link_expire * 60,
            "cooldown_seconds": cooldown_secs
        }

        if not Config.is_production():
            resp["verification_link"] = verification_url

        return resp, 200

    @classmethod
    def verify_registration_otp(cls, email: str, otp_code: str):
        """
        Validates candidate-submitted 6-digit OTP against the stored cryptographic hash.
        Enforces 5-minute expiry, single-use invalidation, and maximum 5 incorrect attempts.
        Returns a signed verification token on success.
        """
        clean_email = email.strip().lower()
        clean_otp = str(otp_code).strip()

        if not clean_email or not cls.is_valid_email(clean_email):
            return {"status": "error", "message": "Invalid email address format.", "code": "INVALID_EMAIL"}, 400

        if not clean_otp or len(clean_otp) != 6 or not clean_otp.isdigit():
            return {"status": "error", "message": "Please enter a valid 6-digit verification code.", "code": "INVALID_FORMAT"}, 400

        # Retrieve latest active OTP record
        record = EmailOTP.query.filter_by(
            email=clean_email, is_used=False
        ).order_by(EmailOTP.id.desc()).first()

        if not record:
            return {
                "status": "error",
                "message": "No active verification code found for this email. Please request a new code.",
                "code": "OTP_NOT_FOUND"
            }, 400

        # Check if expired
        if record.is_expired():
            record.is_used = True
            db.session.commit()
            return {
                "status": "error",
                "message": "Your verification code has expired. Please request a new code.",
                "code": "OTP_EXPIRED"
            }, 400

        # Check attempts limit
        max_attempts = getattr(Config, "OTP_MAX_ATTEMPTS", 5)
        if record.attempts >= max_attempts:
            record.is_used = True
            db.session.commit()
            return {
                "status": "error",
                "message": "Too many incorrect attempts. For your security, this code has been invalidated. Please request a new code.",
                "code": "MAX_ATTEMPTS_EXCEEDED"
            }, 400

        # Verify hash match
        if not record.verify_otp(clean_otp):
            record.attempts += 1
            db.session.commit()
            remaining = max(0, max_attempts - record.attempts)
            if remaining == 0:
                record.is_used = True
                db.session.commit()
                return {
                    "status": "error",
                    "message": "Too many incorrect attempts. This code has been invalidated. Please request a new code.",
                    "code": "MAX_ATTEMPTS_EXCEEDED"
                }, 400

            return {
                "status": "error",
                "message": f"Invalid OTP. Please check the code and try again ({remaining} attempts remaining).",
                "remaining_attempts": remaining,
                "code": "INVALID_OTP"
            }, 400

        # Mark OTP as successfully used
        record.is_used = True

        # If user account already exists, update email_verified flag
        existing_user = User.query.filter_by(email=clean_email).first()
        if existing_user:
            existing_user.email_verified = True

        db.session.commit()

        # Issue cryptographically signed email verification token (valid for 15 minutes)
        verification_token = generate_verification_token(email=clean_email, purpose="email_verified", expires_in_minutes=15)

        return {
            "status": "success",
            "message": "Your email address has been successfully verified.",
            "verification_token": verification_token,
            "email": clean_email
        }, 200

    @classmethod
    def resend_registration_otp(cls, email: str, full_name: str = None):
        """
        Resends verification OTP to candidate email with rate limit cooldown check.
        """
        clean_email = email.strip().lower()
        if not clean_email or not cls.is_valid_email(clean_email):
            return {"status": "error", "message": "Please provide a valid email address.", "code": "INVALID_EMAIL"}, 400

        # Preserve candidate name if provided or default
        name = full_name.strip() if full_name else "Candidate"
        return cls.send_registration_otp(clean_email, name)

    @classmethod
    def verify_email_link(cls, token: str):
        """
        Validates token from candidate's email verification link.
        If valid:
        - Marks latest active EmailOTP as verified/used
        - If User account already exists, marks User.email_verified = True
        - Issues an authorized verification_token (JWT with purpose='email_verified') so
          the candidate can immediately complete registration or log in.
        """
        data = verify_email_link_token(token)
        if not data:
            return {
                "status": "error",
                "message": "Invalid or expired verification link. Please request a new link.",
                "code": "INVALID_OR_EXPIRED_LINK"
            }, 400

        clean_email = data.get("email", "").strip().lower()
        if not clean_email or not cls.is_valid_email(clean_email):
            return {"status": "error", "message": "Invalid email address in verification link.", "code": "INVALID_EMAIL"}, 400

        # Mark any pending OTPs for this email as verified
        EmailOTP.query.filter_by(email=clean_email, is_used=False).update({"is_used": True})

        # If user account exists in DB, activate it
        existing_user = User.query.filter_by(email=clean_email).first()
        is_existing_account = False
        user_info = None
        if existing_user:
            existing_user.email_verified = True
            is_existing_account = True
            user_info = existing_user.to_dict()

        db.session.commit()

        # Generate a signed verification token (valid for completing registration or auto-login)
        verification_token = generate_verification_token(email=clean_email, purpose="email_verified", expires_in_minutes=30)

        return {
            "status": "success",
            "message": "Email address verified successfully!",
            "email": clean_email,
            "verification_token": verification_token,
            "is_registered": is_existing_account,
            "user": user_info
        }, 200

    @classmethod
    def check_verification_status(cls, email: str):
        """
        Checks whether the candidate's email has already been verified via link.
        Used by the registration page to auto-advance if the candidate clicks the link
        in their email on mobile or another browser tab.
        """
        clean_email = email.strip().lower()
        if not clean_email or not cls.is_valid_email(clean_email):
            return {"status": "error", "message": "Invalid email format.", "code": "INVALID_EMAIL"}, 400

        existing_user = User.query.filter_by(email=clean_email).first()
        if existing_user and existing_user.email_verified:
            token = generate_verification_token(email=clean_email, purpose="email_verified", expires_in_minutes=30)
            return {
                "status": "success",
                "verified": True,
                "email": clean_email,
                "verification_token": token,
                "is_registered": True
            }, 200

        # Check if the latest OTP has been marked used (e.g. by link verification before user creation)
        latest_otp = EmailOTP.query.filter_by(email=clean_email).order_by(EmailOTP.id.desc()).first()
        if latest_otp and latest_otp.is_used:
            token = generate_verification_token(email=clean_email, purpose="email_verified", expires_in_minutes=30)
            return {
                "status": "success",
                "verified": True,
                "email": clean_email,
                "verification_token": token,
                "is_registered": False
            }, 200

        return {
            "status": "success",
            "verified": False,
            "email": clean_email
        }, 200

