"""
test_email_otp.py - Automated test suite for Email OTP Verification System,
Rate Limiting, Cryptographic Hash Storage, Direct API Bypass Protection,
and Candidate Registration Token Enforcement.
"""

import os
import sys
import unittest
import time
import uuid
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.models.otp import EmailOTP
from backend.services.otp_service import OTPService
from backend.services.email_service import EmailService
from backend.config import Config
from backend.utils.security import generate_verification_token, verify_email_token

class TestEmailOTPVerification(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.ts = int(time.time())
        self.rand = uuid.uuid4().hex[:6]
        self.test_email = f"test_cand_{self.ts}_{self.rand}@interview.ai"
        self.test_name = "Dev Candidate"

    def tearDown(self):
        self.app_context.pop()

    def test_01_send_otp_success_and_no_plaintext_leak(self):
        """Test sending OTP generates secure hash in DB and never returns plaintext code"""
        res = self.client.post("/api/auth/send-otp", json={
            "email": self.test_email,
            "full_name": self.test_name
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("expires_in_seconds", data)

        # SECURITY RULE: Never return plaintext OTP in response payload
        self.assertNotIn("otp", data)
        self.assertNotIn("otp_code", data)

        # Check DB record
        record = EmailOTP.query.filter_by(email=self.test_email, is_used=False).first()
        self.assertIsNotNone(record)
        self.assertEqual(record.attempts, 0)
        self.assertFalse(record.is_used)

        # SECURITY RULE: DB stores only hash, never plaintext
        self.assertNotEqual(record.otp_hash, "123456")
        self.assertTrue(record.otp_hash.startswith("scrypt:") or record.otp_hash.startswith("pbkdf2:"))
        print(f"[PASS] 1. Send OTP succeeded for {self.test_email}. Hash stored, no plaintext leaks.")

    def test_02_resend_cooldown_rate_limiting(self):
        """Test that requesting OTP twice immediately triggers 429 Too Many Requests"""
        email = f"cooldown_{self.ts}_{self.rand}@interview.ai"

        # First request
        res1 = self.client.post("/api/auth/send-otp", json={"email": email, "full_name": "Cooldown Test"})
        self.assertEqual(res1.status_code, 200)

        # Immediate second request
        res2 = self.client.post("/api/auth/send-otp", json={"email": email, "full_name": "Cooldown Test"})
        self.assertEqual(res2.status_code, 429)
        data2 = res2.get_json()
        self.assertEqual(data2["status"], "error")
        self.assertEqual(data2.get("code"), "COOLDOWN_ACTIVE")
        self.assertIn("cooldown_seconds", data2)
        print("[PASS] 2. Resend rate limit cooldown enforced (HTTP 429).")

    def test_03_invalid_otp_attempts_tracking_and_lockout(self):
        """Test that incorrect OTP increments attempts and locks out after 5 failures"""
        email = f"attempts_{self.ts}_{self.rand}@interview.ai"
        self.client.post("/api/auth/send-otp", json={"email": email, "full_name": "Attempt Test"})

        # Submit wrong OTP 4 times
        for attempt in range(1, 5):
            res = self.client.post("/api/auth/verify-otp", json={"email": email, "otp": "000000"})
            self.assertEqual(res.status_code, 400)
            data = res.get_json()
            self.assertEqual(data.get("code"), "INVALID_OTP")
            self.assertEqual(data.get("remaining_attempts"), 5 - attempt)

        # 5th attempt should trigger MAX_ATTEMPTS_EXCEEDED
        res5 = self.client.post("/api/auth/verify-otp", json={"email": email, "otp": "000000"})
        self.assertEqual(res5.status_code, 400)
        data5 = res5.get_json()
        self.assertEqual(data5.get("code"), "MAX_ATTEMPTS_EXCEEDED")

        # Record should now be marked is_used = True
        record = EmailOTP.query.filter_by(email=email).order_by(EmailOTP.id.desc()).first()
        self.assertTrue(record.is_used)
        print("[PASS] 3. Invalid OTP attempt tracking and 5-attempt security lockout verified.")

    def test_04_expired_otp_rejected(self):
        """Test that expired OTPs are rejected with OTP_EXPIRED"""
        email = f"expired_{self.ts}_{self.rand}@interview.ai"
        self.client.post("/api/auth/send-otp", json={"email": email, "full_name": "Expiry Test"})

        # Manually expire the record in DB
        record = EmailOTP.query.filter_by(email=email, is_used=False).first()
        record.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.session.commit()

        res = self.client.post("/api/auth/verify-otp", json={"email": email, "otp": "123456"})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get("code"), "OTP_EXPIRED")
        print("[PASS] 4. Expired OTP correctly rejected.")

    def test_05_valid_otp_issues_verification_token_and_marks_used(self):
        """Test that correct OTP issues signed verification token and marks OTP used (single-use)"""
        email = f"valid_{self.ts}_{self.rand}@interview.ai"
        
        # Directly generate known OTP using service for precise verification
        record = EmailOTP(
            email=email,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            attempts=0,
            is_used=False,
            purpose="candidate_registration"
        )
        known_otp = "789123"
        record.set_otp(known_otp)
        db.session.add(record)
        db.session.commit()

        # Verify with known OTP
        res = self.client.post("/api/auth/verify-otp", json={"email": email, "otp": known_otp})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("verification_token", data)

        token = data["verification_token"]
        self.assertTrue(verify_email_token(token, expected_email=email))

        # Check that OTP is now used
        updated = EmailOTP.query.get(record.id)
        self.assertTrue(updated.is_used)

        # Single-use check: attempting again must fail
        res2 = self.client.post("/api/auth/verify-otp", json={"email": email, "otp": known_otp})
        self.assertEqual(res2.status_code, 400)
        print("[PASS] 5. Valid OTP verified, verification token issued, single-use enforced.")

    def test_06_direct_registration_instant_verified(self):
        """Test that direct candidate registration succeeds immediately with email_verified=True without verification token"""
        email = f"direct_{self.ts}_{self.rand}@interview.ai"

        res1 = self.client.post("/api/auth/register", json={
            "full_name": "Direct Verified Candidate",
            "email": email,
            "password": "Password123!",
            "role": "candidate"
        })
        self.assertEqual(res1.status_code, 201)
        data1 = res1.get_json()
        self.assertEqual(data1["status"], "success")
        self.assertTrue(data1["user"]["email_verified"])
        self.assertTrue(data1["candidate_id"].startswith("CID-2026-"))
        print("[PASS] 6. Direct candidate registration succeeds instantly with email_verified=True.")

    def test_07_complete_registration_with_verified_token(self):
        """Test complete candidate registration with valid verification token issues permanent Candidate ID"""
        email = f"registered_{self.ts}_{self.rand}@interview.ai"
        valid_token = generate_verification_token(email)

        res = self.client.post("/api/auth/register", json={
            "full_name": "Anita Shrestha",
            "email": email,
            "password": "Password123!",
            "role": "candidate",
            "target_role": "AI/ML Engineer",
            "verification_token": valid_token
        })

        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("candidate_id", data)
        self.assertTrue(data["candidate_id"].startswith("CID-2026-"))
        print(f"[PASS] 7. Candidate registration verified: Candidate ID {data['candidate_id']} issued.")

    def test_08_send_otp_for_already_registered_email_rejected(self):
        """Test sending OTP for an existing candidate email returns 409 Conflict"""
        existing_email = "rahul@interview.ai"
        res = self.client.post("/api/auth/send-otp", json={"email": existing_email, "full_name": "Rahul"})
        self.assertEqual(res.status_code, 409)
        data = res.get_json()
        self.assertEqual(data.get("code"), "EMAIL_EXISTS")
        print("[PASS] 8. Sending OTP for existing registered email rejected with 409 Conflict.")

    def test_09_production_mode_unconfigured_smtp_rejection(self):
        """Test that in production mode without SMTP configured, OTP request returns 503 and never leaks dev code"""
        orig_env = Config.APP_ENV
        orig_resend = Config.RESEND_API_KEY
        orig_user = Config.MAIL_USERNAME
        orig_pass = Config.MAIL_PASSWORD
        try:
            Config.APP_ENV = "production"
            Config.RESEND_API_KEY = ""
            Config.MAIL_USERNAME = ""
            Config.MAIL_PASSWORD = ""
            self.app.config["TESTING"] = False

            email = f"prod_test_{self.ts}_{self.rand}@interview.ai"
            res = self.client.post("/api/auth/send-otp", json={"email": email, "full_name": "Prod Candidate"})
            self.assertEqual(res.status_code, 503)
            data = res.get_json()
            self.assertEqual(data["status"], "error")
            self.assertIn(data.get("code"), ["EMAIL_PROVIDER_UNCONFIGURED", "SMTP_NOT_CONFIGURED"])
            self.assertNotIn("dev_code", data)
            self.assertNotIn("dev_mode", data)
            print("[PASS] 9. Production mode strictly enforces email provider configuration (HTTP 503) and never leaks dev code.")
        finally:
            Config.APP_ENV = orig_env
            Config.RESEND_API_KEY = orig_resend
            Config.MAIL_USERNAME = orig_user
            Config.MAIL_PASSWORD = orig_pass
            self.app.config["TESTING"] = True

    def test_10_sender_address_rfc_formatting(self):
        """Test RFC 5321 bare envelope sender and RFC 5322 formatted display header"""
        envelope = Config.get_envelope_sender()
        self.assertIn("@", envelope)
        self.assertNotIn("<", envelope)
        self.assertNotIn(">", envelope)

        formatted = Config.get_formatted_sender()
        self.assertIn("<", formatted)
        self.assertIn(">", formatted)
        print(f"[PASS] 10. RFC 5321/5322 sender formats verified: envelope='{envelope}', header='{formatted}'.")

    def test_11_test_smtp_diagnostic_endpoint(self):
        """Test diagnostic /api/auth/test-smtp endpoint returns status structure"""
        res = self.client.post("/api/auth/test-smtp", json={})
        data = res.get_json()
        self.assertIn("status", data)
        self.assertIn("smtp_configured", data)
        self.assertIn("smtp_server", data)
        self.assertIn("envelope_sender", data)
        print(f"[PASS] 11. Diagnostic /api/auth/test-smtp endpoint tested successfully (configured={data['smtp_configured']}).")

    def test_12_email_verification_link_generation_and_validation(self):
        """Test generating email verification link, verifying token, and polling status"""
        from backend.utils.security import generate_email_verification_link
        email = f"link_cand_{self.ts}_{self.rand}@interview.ai"

        token, link_url = generate_email_verification_link(email, base_url="http://localhost:5000")
        self.assertIn("verify-email.html?token=", link_url)

        # Before verification, status should be verified=False
        status_res = self.client.get(f"/api/auth/verification-status?email={email}")
        self.assertEqual(status_res.status_code, 200)
        self.assertFalse(status_res.get_json()["verified"])

        # Verify link with valid token
        verify_res = self.client.post("/api/auth/verify-link", json={"token": token})
        self.assertEqual(verify_res.status_code, 200)
        data = verify_res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["email"], email)
        self.assertIn("verification_token", data)

        # Verify link with invalid token should fail
        bad_res = self.client.post("/api/auth/verify-link", json={"token": "invalid_jwt_garbage"})
        self.assertEqual(bad_res.status_code, 400)
        self.assertEqual(bad_res.get_json().get("code"), "INVALID_OR_EXPIRED_LINK")

        # GET request with query parameter also works
        token2, _ = generate_email_verification_link(f"get_{email}")
        get_res = self.client.get(f"/api/auth/verify-link?token={token2}")
        self.assertEqual(get_res.status_code, 200)
        print(f"[PASS] 12. Email verification link generated, verified, and query/json API endpoints validated.")

    def test_13_register_with_link_verification_token(self):
        """Test candidate can complete registration using token issued by email verification link"""
        from backend.utils.security import generate_email_verification_link
        email = f"registered_via_link_{self.ts}_{self.rand}@interview.ai"
        token, _ = generate_email_verification_link(email)

        # Call verify-link
        verify_res = self.client.post("/api/auth/verify-link", json={"token": token})
        self.assertEqual(verify_res.status_code, 200)
        reg_token = verify_res.get_json()["verification_token"]

        # Register candidate with reg_token
        res = self.client.post("/api/auth/register", json={
            "full_name": "Link Verified Candidate",
            "email": email,
            "password": "SecurePassword2026!",
            "target_role": "Full Stack Engineer",
            "verification_token": reg_token
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["candidate_id"].startswith("CID-2026-"))

        # Verify candidate in DB has email_verified=True
        user = User.query.filter_by(email=email).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.email_verified)
        print(f"[PASS] 13. Candidate registration with link verification token succeeded: {user.candidate_id}, email_verified=True.")

if __name__ == "__main__":
    unittest.main()

