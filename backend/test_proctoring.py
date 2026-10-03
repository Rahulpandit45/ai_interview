"""
test_proctoring.py
Comprehensive test suite for AI Interview System Proctoring and Multi-Person Detection.

Covers:
1. Normal condition (1 face = registered candidate)
2. Brief glitch filtering (faces >= 2 for < 2.5s ignored)
3. First violation after confirmation window -> Warning 1
4. Face leaves -> Warning cleared
5. Second violation after confirmation window -> Final Warning with 10s countdown
6. Face leaves during Final Warning within 10s -> Warning cleared, no termination
7. Persistent second violation after 10s -> Interview Terminated & locked
8. Database persistence & violation history logging
9. FastAPI Proctoring endpoints & OpenAPI compliance
10. Post-termination route guarding (403 Forbidden on response & finish)
11. Configurable thresholds validation
"""

import os
import sys
import time
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.services.proctoring_service import (
    InterviewProctoringSession,
    ProctoringConfig,
    ProctoringManager
)
from backend.app import app
from backend.services.database import db
from backend.models.interview import Interview, ProctoringViolation
from backend.models.user import User


class ProctoringUnitTests(unittest.TestCase):
    def setUp(self):
        self.config = ProctoringConfig(
            confirmation_seconds=2.5,
            final_warning_timeout_seconds=10.0,
            allowed_candidate_faces=1
        )
        self.session = InterviewProctoringSession(interview_id=999, config=self.config)
        self.base_time = 1000.0

    def test_single_face_normal(self):
        """1 face = registered candidate -> continue normally with clean status."""
        res = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time)
        self.assertEqual(res["status"], "clean")
        self.assertEqual(res["warning_count"], 0)
        self.assertFalse(res["is_terminated"])
        self.assertEqual(res["additional_faces"], 0)

    def test_brief_glitch_ignored(self):
        """Additional face detected for < 2.5s confirmation period is ignored (brief/momentary glitch)."""
        # t = 0.0s: 2 faces appear
        res1 = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        self.assertEqual(res1["status"], "clean")
        self.assertEqual(res1["warning_count"], 0)
        self.assertFalse(res1["is_terminated"])

        # t = 1.0s: 2 faces still present (1.0s < 2.5s)
        res2 = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 1.0)
        self.assertEqual(res2["status"], "clean")
        self.assertEqual(res2["warning_count"], 0)
        self.assertFalse(res2["is_terminated"])

        # t = 2.0s: 2 faces still present (2.0s < 2.5s)
        res3 = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.0)
        self.assertEqual(res3["status"], "clean")
        self.assertEqual(res3["warning_count"], 0)

        # t = 2.2s: other face leaves before 2.5s
        res4 = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 2.2)
        self.assertEqual(res4["status"], "clean")
        self.assertEqual(res4["warning_count"], 0)

    def test_first_violation_warning_1(self):
        """Continuous presence >= 2.5s triggers Warning 1 with exact required message."""
        # Start detection
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        # Reach confirmation time (t = 2.5s)
        res = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.5)
        
        self.assertEqual(res["status"], "warning_1")
        self.assertEqual(res["warning_count"], 1)
        self.assertFalse(res["is_terminated"])
        self.assertEqual(
            res["message"],
            "⚠️ Warning 1: Another person has been detected. Please ensure you are alone during the interview."
        )

    def test_face_leaves_clears_warning_1(self):
        """When other face leaves after Warning 1, warning is cleared and interview continues."""
        # Trigger Warning 1
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.5)
        self.assertEqual(self.session.status, "warning_1")

        # Other person leaves (faces = 1)
        res = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 5.0)
        self.assertEqual(res["status"], "warning_cleared")
        self.assertEqual(res["warning_count"], 1)  # History retained
        self.assertFalse(res["is_terminated"])
        self.assertIn("The other person has left", res["message"])

    def test_second_violation_final_warning(self):
        """Second violation after confirmation window triggers Final Warning and starts 10s countdown."""
        # Violation 1
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.5)
        # Cleared
        self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 5.0)
        
        # Second violation begins at t = 10.0s
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 10.0)
        # Briefly before confirmation (t = 11.5s -> 1.5s continuous)
        res_mid = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 11.5)
        self.assertEqual(res_mid["warning_count"], 1)

        # Confirmed at t = 12.5s (2.5s continuous)
        res_final = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 12.5)
        self.assertEqual(res_final["status"], "final_warning")
        self.assertEqual(res_final["warning_count"], 2)
        self.assertFalse(res_final["is_terminated"])
        self.assertEqual(
            res_final["message"],
            "⚠️ Final Warning: Another person has been detected again. Please ensure you are alone."
        )
        self.assertEqual(res_final["remaining_seconds"], 10.0)

    def test_face_leaves_during_final_warning(self):
        """If other face leaves within 10s of Final Warning, warning clears and no termination occurs."""
        # Reach final warning at t = 12.5s
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.5)
        self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 5.0)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 10.0)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 12.5)
        self.assertEqual(self.session.status, "final_warning")

        # 5 seconds into final warning (remaining = 5.0s)
        res_during = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 17.5)
        self.assertEqual(res_during["status"], "final_warning")
        self.assertEqual(res_during["remaining_seconds"], 5.0)

        # At t = 18.0s, other person leaves
        res_cleared = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 18.0)
        self.assertEqual(res_cleared["status"], "warning_cleared")
        self.assertFalse(res_cleared["is_terminated"])

        # Advance another 15 seconds alone -> Still not terminated
        res_after = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 33.0)
        self.assertFalse(res_after["is_terminated"])
        self.assertEqual(res_after["status"], "clean")

    def test_persistent_second_violation_terminates(self):
        """If other face does NOT leave within 10s of Final Warning, interview terminates automatically."""
        # Reach final warning at t = 12.5s
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 2.5)
        self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 5.0)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 10.0)
        self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 12.5)

        # 10.1 seconds after final warning issued (t = 12.5 + 10.1 = 22.6s)
        res_term = self.session.evaluate_faces(faces_detected=2, current_time=self.base_time + 22.6)
        self.assertEqual(res_term["status"], "terminated")
        self.assertTrue(res_term["is_terminated"])
        self.assertEqual(res_term["remaining_seconds"], 0.0)
        self.assertEqual(
            res_term["message"],
            "❌ Interview Terminated: Another person remained present after the final warning."
        )

        # Even if face subsequently leaves, status remains locked as terminated
        res_locked = self.session.evaluate_faces(faces_detected=1, current_time=self.base_time + 30.0)
        self.assertEqual(res_locked["status"], "terminated")
        self.assertTrue(res_locked["is_terminated"])

    def test_configurable_thresholds(self):
        """Configurable confirmation time and timeout values are respected."""
        custom_cfg = ProctoringConfig(
            confirmation_seconds=1.0,
            final_warning_timeout_seconds=4.0
        )
        custom_session = InterviewProctoringSession(interview_id=888, config=custom_cfg)
        
        # 1.0s triggers Warning 1
        custom_session.evaluate_faces(faces_detected=2, current_time=100.0)
        res1 = custom_session.evaluate_faces(faces_detected=2, current_time=101.0)
        self.assertEqual(res1["status"], "warning_1")

        # Clear
        custom_session.evaluate_faces(faces_detected=1, current_time=102.0)

        # 1.0s triggers Final Warning
        custom_session.evaluate_faces(faces_detected=2, current_time=105.0)
        res_final = custom_session.evaluate_faces(faces_detected=2, current_time=106.0)
        self.assertEqual(res_final["status"], "final_warning")
        self.assertEqual(res_final["remaining_seconds"], 4.0)

        # 4.0s timeout terminates
        res_term = custom_session.evaluate_faces(faces_detected=2, current_time=110.1)
        self.assertTrue(res_term["is_terminated"])


class ProctoringIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            # Create a test candidate and interview
            test_user = User.query.filter_by(email="proctor_test@example.com").first()
            if not test_user:
                test_user = User(
                    full_name="Proctor Candidate",
                    email="proctor_test@example.com",
                    role="candidate"
                )
                test_user.set_password("SecurePass123!")
                db.session.add(test_user)
                db.session.commit()
            cls.test_user_id = test_user.id

            test_interview = Interview(
                user_id=test_user.id,
                target_role="Python Developer",
                status="in_progress"
            )
            db.session.add(test_interview)
            db.session.commit()
            cls.test_interview_id = test_interview.id

    def test_database_persistence_and_termination_lock(self):
        """Verifies that violations and termination are written to the database."""
        interview_id = self.test_interview_id
        t0 = 5000.0

        # Trigger Warning 1 via ProctoringManager
        ProctoringManager.reset_session(interview_id)
        ProctoringManager.process_check(interview_id, faces_detected=2, current_time=t0)
        res1 = ProctoringManager.process_check(interview_id, faces_detected=2, current_time=t0 + 2.5)
        self.assertEqual(res1["status"], "warning_1")

        with app.app_context():
            interview = db.session.get(Interview, interview_id)
            self.assertEqual(interview.warning_count, 1)
            self.assertEqual(interview.proctoring_status, "warning_1")
            violations = ProctoringViolation.query.filter_by(interview_id=interview_id).all()
            self.assertTrue(len(violations) >= 1)

        # Clear
        ProctoringManager.process_check(interview_id, faces_detected=1, current_time=t0 + 4.0)

        # Trigger Final Warning
        ProctoringManager.process_check(interview_id, faces_detected=2, current_time=t0 + 6.0)
        ProctoringManager.process_check(interview_id, faces_detected=2, current_time=t0 + 8.5)

        # Terminate after 10s
        res_term = ProctoringManager.process_check(interview_id, faces_detected=2, current_time=t0 + 19.0)
        self.assertTrue(res_term["is_terminated"])

        with app.app_context():
            interview = db.session.get(Interview, interview_id)
            self.assertEqual(interview.status, "terminated")
            self.assertIn("Another person remained present", interview.termination_reason)
            self.assertEqual(interview.warning_count, 2)

    def test_post_termination_blocks_candidate_submission(self):
        """Verifies candidate is strictly blocked from submitting responses or finishing once terminated."""
        flask_client = app.test_client()

        # Login as candidate to obtain valid token
        login_res = flask_client.post("/api/auth/login", json={
            "email": "proctor_test@example.com",
            "password": "SecurePass123!"
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.json["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Attempt to submit response on terminated interview
        res_resp = flask_client.post(
            f"/api/interview/{self.test_interview_id}/response",
            data={"question_id": "q1", "question_text": "What is Python?"},
            headers=headers
        )
        self.assertEqual(res_resp.status_code, 403)
        self.assertIn("Interview Terminated", res_resp.json.get("message", ""))

        # Attempt to finish terminated interview
        res_fin = flask_client.post(
            f"/api/interview/{self.test_interview_id}/finish",
            headers=headers
        )
        self.assertEqual(res_fin.status_code, 403)
        self.assertIn("Interview Terminated", res_fin.json.get("message", ""))


class FastAPIProctoringApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi.testclient import TestClient
        from backend.fastapi_app import app as fastapi_app
        cls.client = TestClient(fastapi_app)

    def test_config_endpoint(self):
        """GET /api/proctoring/config returns active thresholds."""
        resp = self.client.get("/api/proctoring/config")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("confirmation_seconds", data)
        self.assertIn("final_warning_timeout_seconds", data)
        self.assertEqual(data["allowed_candidate_faces"], 1)

    def test_check_and_status_endpoints(self):
        """POST /api/proctoring/check and GET /api/proctoring/status/{id} work synchronously."""
        interview_id = 9999
        self.client.post(f"/api/proctoring/reset/{interview_id}")

        # 1 face check
        resp = self.client.post("/api/proctoring/check", json={
            "interview_id": interview_id,
            "faces_detected": 1,
            "timestamp": 2000.0
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "clean")

        # Check status endpoint
        resp_status = self.client.get(f"/api/proctoring/status/{interview_id}")
        self.assertEqual(resp_status.status_code, 200)
        self.assertEqual(resp_status.json()["warning_count"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
