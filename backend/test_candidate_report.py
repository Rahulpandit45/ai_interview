"""
test_candidate_report.py
Validation script for Candidate Search and Complete Candidate Report API.
"""

import os
import sys
import unittest
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.utils.security import generate_token

class TestCandidateReportAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            # Get admin and candidate
            self.admin = User.query.filter_by(email="admin@interview.ai").first()
            self.candidate = User.query.filter_by(email="rahul@interview.ai").first()
            self.admin_token = generate_token(self.admin.id, self.admin.role)
            self.cand_token = generate_token(self.candidate.id, self.candidate.role)

    def test_unauthorized_access(self):
        """Test that requests without admin token are rejected"""
        # No token
        res = self.client.get("/api/admin/candidates/search-by-id?id=TEST")
        self.assertEqual(res.status_code, 401)

        # Candidate token trying to access admin report
        headers = {"Authorization": f"Bearer {self.cand_token}"}
        res2 = self.client.get(f"/api/admin/candidates/{self.candidate.candidate_id}/report", headers=headers)
        self.assertEqual(res2.status_code, 403)
        print("[PASS] Test passed: Unauthorized access properly blocked (401/403)")

    def test_search_nonexistent_candidate(self):
        """Test searching for non-existent candidate returns 404"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        res = self.client.get("/api/admin/candidates/search-by-id?id=NON_EXISTENT_ID_9999", headers=headers)
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertEqual(data["status"], "error")
        print("[PASS] Test passed: Non-existent candidate ID returns 404")

    def test_search_valid_candidate_id(self):
        """Test searching with valid Candidate ID"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        cid = self.candidate.candidate_id
        res = self.client.get(f"/api/admin/candidates/search-by-id?id={cid}", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["candidate"]["candidate_id"], cid)
        print(f"[PASS] Test passed: Valid search for {cid} returned 200")

    def test_complete_candidate_report(self):
        """Test complete candidate report payload structure and forensic integrity"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        cid = self.candidate.candidate_id
        res = self.client.get(f"/api/admin/candidates/{cid}/report", headers=headers)
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(payload["status"], "success")
        data = payload["data"]

        # Verify all required sections
        expected_sections = [
            "candidate", "registration", "photos", "interview",
            "qa_history", "adaptive_history", "video",
            "face_verification", "security_events", "timeline"
        ]
        for sec in expected_sections:
            self.assertIn(sec, data, f"Missing required section: {sec}")

        # Verify Candidate Info
        cand = data["candidate"]
        self.assertEqual(cand["candidate_id"], cid)
        self.assertEqual(cand["full_name"], self.candidate.full_name)
        self.assertEqual(cand["email"], self.candidate.email)
        self.assertIn("registration_date", cand)
        self.assertIn("registration_time", cand)

        # Verify Photos (Side-by-side)
        photos = data["photos"]
        self.assertIn("registration_photo", photos)
        self.assertIn("interview_photo", photos)
        self.assertEqual(photos["registration_photo"]["label"], "Registration Photo")
        self.assertEqual(photos["interview_photo"]["label"], "Interview Photo")

        # Verify Registration / CV Info
        reg = data["registration"]
        self.assertIn("extracted_cv_name", reg)
        self.assertIn("registered_candidate_name", reg)
        self.assertIn("name_matching_result", reg)
        self.assertIn("verification_status", reg)

        # Verify Interview Info
        intv = data["interview"]
        self.assertIn("interview_id", intv)
        self.assertIn("status", intv)
        self.assertIn("duration", intv)
        self.assertIn("overall_score", intv)

        # Verify Timeline
        timeline = data["timeline"]
        self.assertIsInstance(timeline, list)

        print(f"[PASS] Test passed: Complete Candidate Report validated for {cid} with all 10 forensic sections.")

if __name__ == "__main__":
    unittest.main()
