"""
test_forgot_password.py - Automated test suite for Forgot Password & Password Reset Flow,
Token Generation, Time-Limited Expiration, Single-Use Invalidation, and Password Updating.
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
from backend.utils.security import (
    generate_password_reset_token,
    verify_password_reset_token
)

class TestForgotPasswordAndReset(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.ts = int(time.time())
        self.rand = uuid.uuid4().hex[:6]
        self.test_email = f"reset_test_{self.ts}_{self.rand}@interview.ai"
        self.initial_password = "InitialPassword123!"

        # Create test candidate in DB
        self.user = User(
            candidate_id=User.generate_candidate_id(),
            full_name="Password Test Candidate",
            email=self.test_email,
            role="candidate",
            target_role="Software Engineer",
            email_verified=True
        )
        self.user.set_password(self.initial_password)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        self.app_context.pop()

    def test_01_forgot_password_generic_success_and_dev_link(self):
        """Test forgot password returns generic success message preventing email enumeration"""
        res = self.client.post("/api/auth/forgot-password", json={"email": self.test_email})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("If an account exists", data["message"])
        self.assertIn("reset_link", data)
        print("[PASS] 1. Forgot password request succeeded with generic message & dev link.")

    def test_02_forgot_password_nonexistent_email_enumeration_prevention(self):
        """Test non-existent email returns identical generic message (no enumeration)"""
        res = self.client.post("/api/auth/forgot-password", json={"email": "nonexistent_email_404@interview.ai"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("If an account exists", data["message"])
        print("[PASS] 2. Non-existent email request returns identical message (enumeration prevented).")

    def test_03_verify_reset_token_success(self):
        """Test verifying a valid reset token returns valid=True and candidate email"""
        token = generate_password_reset_token(self.user, expires_in_minutes=20)
        res = self.client.get(f"/api/auth/verify-reset-token?token={token}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["valid"])
        self.assertEqual(data["email"], self.test_email)
        print("[PASS] 3. Verify reset token succeeded for candidate.")

    def test_04_verify_reset_token_invalid_or_tampered(self):
        """Test tampered or invalid reset token is rejected with HTTP 400"""
        res = self.client.get("/api/auth/verify-reset-token?token=invalid_tampered_jwt_token")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data.get("code"), "INVALID_OR_EXPIRED_TOKEN")
        print("[PASS] 4. Tampered reset token correctly rejected.")

    def test_05_verify_reset_token_expired(self):
        """Test expired reset token is rejected"""
        expired_token = generate_password_reset_token(self.user, expires_in_minutes=-5)
        res = self.client.get(f"/api/auth/verify-reset-token?token={expired_token}")
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data["status"], "error")
        print("[PASS] 5. Expired reset token correctly rejected.")

    def test_06_reset_password_validation_rules(self):
        """Test validation rules: password length >= 6 and password match"""
        token = generate_password_reset_token(self.user, expires_in_minutes=20)

        # 1. Short password (< 6 chars)
        res1 = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": "123",
            "confirm_password": "123"
        })
        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res1.get_json().get("code"), "PASSWORD_TOO_SHORT")

        # 2. Mismatched passwords
        res2 = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": "NewSecretPassword123!",
            "confirm_password": "DifferentPassword456!"
        })
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.get_json().get("code"), "PASSWORDS_MISMATCH")
        print("[PASS] 6. Password complexity & match validation rules enforced.")

    def test_07_successful_password_reset_and_login_verification(self):
        """Test complete password reset, new password login, and old password rejection"""
        token = generate_password_reset_token(self.user, expires_in_minutes=20)
        new_pwd = "BrandNewSecurePassword2026!"

        res = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": new_pwd,
            "confirm_password": new_pwd
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "success")

        # Login with old password must fail (HTTP 401)
        old_login = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": self.test_email,
            "password": self.initial_password
        })
        self.assertEqual(old_login.status_code, 401)

        # Login with new password must succeed (HTTP 200)
        new_login = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": self.test_email,
            "password": new_pwd
        })
        self.assertEqual(new_login.status_code, 200)
        self.assertIn("token", new_login.get_json())
        print("[PASS] 7. Password reset succeeded; new credentials verified and old credentials revoked.")

    def test_08_single_use_token_invalidation(self):
        """Test security rule: reset token is invalidated immediately once used"""
        token = generate_password_reset_token(self.user, expires_in_minutes=20)
        new_pwd1 = "FirstResetPassword123!"

        # First use: succeeds
        res1 = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": new_pwd1,
            "confirm_password": new_pwd1
        })
        self.assertEqual(res1.status_code, 200)

        # Second use: MUST be rejected because token's password fingerprint changed
        res2 = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": "SecondResetAttempt456!",
            "confirm_password": "SecondResetAttempt456!"
        })
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.get_json().get("code"), "INVALID_OR_EXPIRED_TOKEN")
        print("[PASS] 8. Single-use token security verified: reused token strictly rejected.")

    def test_09_frontend_page_routes(self):
        """Test /forgot-password and /reset-password route serving"""
        res1 = self.client.get("/forgot-password")
        self.assertEqual(res1.status_code, 200)
        self.assertIn(b"Reset Your Password", res1.data)

        res2 = self.client.get("/reset-password")
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"Set New Password", res2.data)

        res3 = self.client.get("/reset-password/sample_test_token_123")
        self.assertEqual(res3.status_code, 200)
        self.assertIn(b"Set New Password", res3.data)
        print("[PASS] 9. Frontend page routes (/forgot-password, /reset-password/<token>) verified.")

if __name__ == "__main__":
    unittest.main()
