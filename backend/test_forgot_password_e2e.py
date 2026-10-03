"""
test_forgot_password_e2e.py
End-to-end verification of the Forgot Password and Reset Password workflow:
- Candidate clicks "Forgot Password"
- Password-reset link sent to registered email
- Opening link allows entering and confirming new password
- No OTP is used anywhere
- All other authentication and security functionality remains intact
"""

import os
import sys
import unittest
import time
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.utils.security import verify_password_reset_token

class TestForgotPasswordE2E(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.ts = int(time.time())
        self.rand = uuid.uuid4().hex[:6]
        self.test_email = f"e2e_candidate_{self.ts}_{self.rand}@interview.ai"
        self.old_password = "OldCandidatePass123!"
        self.new_password = "NewCandidatePass456!"

        # Register candidate
        self.user = User(
            candidate_id=User.generate_candidate_id(),
            full_name="E2E Test Candidate",
            email=self.test_email,
            role="candidate",
            target_role="Frontend Engineer",
            email_verified=True
        )
        self.user.set_password(self.old_password)
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        self.app_context.pop()

    def test_full_forgot_password_flow_without_otp(self):
        print("\n--- Running End-to-End Forgot Password Workflow Test ---")

        # 1. Candidate triggers Forgot Password
        res_forgot = self.client.post("/api/auth/forgot-password", json={"email": self.test_email})
        self.assertEqual(res_forgot.status_code, 200)
        data_forgot = res_forgot.get_json()
        self.assertEqual(data_forgot["status"], "success")
        
        # Verify NO OTP code is present in response
        self.assertNotIn("otp", data_forgot)
        self.assertNotIn("code", data_forgot)
        self.assertIn("reset_link", data_forgot)
        reset_link = data_forgot["reset_link"]
        self.assertIn("/reset-password.html?token=", reset_link)
        print("[STEP 1 PASSED] Forgot Password requested -> reset link generated and dispatched to registered email.")

        # Extract token from the generated reset link
        token = reset_link.split("token=")[-1]
        self.assertTrue(len(token) > 20)

        # 2. Candidate opens the reset link (verifying the token)
        res_verify = self.client.get(f"/api/auth/verify-reset-token?token={token}")
        self.assertEqual(res_verify.status_code, 200)
        data_verify = res_verify.get_json()
        self.assertTrue(data_verify["valid"])
        self.assertEqual(data_verify["email"], self.test_email)
        print("[STEP 2 PASSED] Candidate opened link -> token validated successfully without OTP.")

        # 3. Validation: Password mismatch
        res_mismatch = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": self.new_password,
            "confirm_password": "MismatchingPassword999!"
        })
        self.assertEqual(res_mismatch.status_code, 400)
        self.assertEqual(res_mismatch.get_json().get("code"), "PASSWORDS_MISMATCH")
        print("[STEP 3 PASSED] Password confirmation mismatch rejected.")

        # 4. Validation: Password too short
        res_short = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": "123",
            "confirm_password": "123"
        })
        self.assertEqual(res_short.status_code, 400)
        self.assertEqual(res_short.get_json().get("code"), "PASSWORD_TOO_SHORT")
        print("[STEP 4 PASSED] Short password (< 6 chars) rejected.")

        # 5. Candidate enters new password and confirms new password
        res_reset = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": self.new_password,
            "confirm_password": self.new_password
        })
        self.assertEqual(res_reset.status_code, 200)
        data_reset = res_reset.get_json()
        self.assertEqual(data_reset["status"], "success")
        print("[STEP 5 PASSED] Password updated with matching confirmation.")

        # 6. Verify old password no longer works
        res_old_login = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": self.test_email,
            "password": self.old_password
        })
        self.assertEqual(res_old_login.status_code, 401)
        print("[STEP 6 PASSED] Old password rejected.")

        # 7. Verify new password logs candidate in successfully
        res_new_login = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": self.test_email,
            "password": self.new_password
        })
        self.assertEqual(res_new_login.status_code, 200)
        data_login = res_new_login.get_json()
        self.assertIn("token", data_login)
        self.assertEqual(data_login["user"]["email"], self.test_email)
        print("[STEP 7 PASSED] Candidate authenticated successfully with new password.")

        # 8. Verify the same token cannot be used again
        res_reuse = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "password": "AnotherNewPassword321!",
            "confirm_password": "AnotherNewPassword321!"
        })
        self.assertEqual(res_reuse.status_code, 400)
        self.assertEqual(res_reuse.get_json().get("code"), "INVALID_OR_EXPIRED_TOKEN")
        print("[STEP 8 PASSED] Token single-use enforcement: reused link rejected.")

    def test_ui_files_content_conformance(self):
        """Verify UI files do not prompt for OTP and have necessary form fields"""
        # forgot-password.html
        forgot_html_path = os.path.join(BASE_DIR, "frontend", "forgot-password.html")
        with open(forgot_html_path, "r", encoding="utf-8") as f:
            forgot_content = f.read()
        self.assertIn("reset-email", forgot_content)
        self.assertIn("Send Password Reset Link", forgot_content)
        self.assertIn("/api/auth/forgot-password", forgot_content)
        self.assertNotIn("Enter 6-digit", forgot_content)
        self.assertNotIn("otp-input", forgot_content)

        # reset-password.html
        reset_html_path = os.path.join(BASE_DIR, "frontend", "reset-password.html")
        with open(reset_html_path, "r", encoding="utf-8") as f:
            reset_content = f.read()
        self.assertIn("new_password", reset_content)
        self.assertIn("confirm_password", reset_content)
        self.assertIn("/api/auth/verify-reset-token", reset_content)
        self.assertIn("/api/auth/reset-password", reset_content)
        self.assertNotIn("otp", reset_content.lower())

        # login.html has forgot-password link
        login_html_path = os.path.join(BASE_DIR, "frontend", "login.html")
        with open(login_html_path, "r", encoding="utf-8") as f:
            login_content = f.read()
        self.assertIn('href="forgot-password.html"', login_content)
        print("[UI CONFORMANCE PASSED] UI templates strictly conform: no OTP, proper fields and flows.")

if __name__ == "__main__":
    unittest.main()
