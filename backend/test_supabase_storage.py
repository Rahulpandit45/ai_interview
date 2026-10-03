"""
test_supabase_storage.py - Supabase Storage & PostgreSQL File Reference Integration Tests
Validates canonical Candidate-ID folder structure, Supabase client operations,
PostgreSQL candidate_files persistence, secure access control, and API streaming parity.
"""

import os
import sys
import unittest
import io
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.models.stored_file import CandidateFile
from backend.services.supabase_storage import SupabaseStorageClient
from backend.services.storage_service import StorageService
from backend.config import Config


class SupabaseStorageTests(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Seed or fetch test users
        self.candidate = User.query.filter_by(email="rahul@interview.ai").first()
        if not self.candidate:
            self.candidate = User(
                candidate_id="CID-2026-HDP62N",
                full_name="Rahul Kumar Pandit",
                email="rahul@interview.ai",
                role="candidate",
                target_role="Software Engineer"
            )
            self.candidate.set_password("candidate123")
            db.session.add(self.candidate)
        else:
            self.candidate.candidate_id = "CID-2026-HDP62N"
            self.candidate.set_password("candidate123")
        db.session.commit()

        self.other_cand = User.query.filter_by(email="other_cand@interview.ai").first()
        if not self.other_cand:
            self.other_cand = User(
                candidate_id="CID-2026-OTHER99",
                full_name="Other Candidate",
                email="other_cand@interview.ai",
                role="candidate"
            )
            self.other_cand.set_password("candidate123")
            db.session.add(self.other_cand)
        else:
            self.other_cand.candidate_id = "CID-2026-OTHER99"
            self.other_cand.set_password("candidate123")
        db.session.commit()

        self.admin = User.query.filter_by(role="admin").first()
        if not self.admin:
            self.admin = User(
                admin_id="ADM-2026-001",
                full_name="System Administrator",
                email="admin@interview.ai",
                role="admin"
            )
            self.admin.set_password("admin123")
            db.session.add(self.admin)
            db.session.commit()
        else:
            self.admin.set_password("admin123")
            if not self.admin.admin_id:
                self.admin.admin_id = "ADM-2026-001"
            db.session.commit()

        # Get JWT tokens
        res_c = self.client.post("/api/auth/login", json={"email": "rahul@interview.ai", "password": "candidate123"})
        self.cand_token = res_c.json.get("token") if res_c.json else ""
        self.cand_headers = {"Authorization": f"Bearer {self.cand_token}"}

        res_other = self.client.post("/api/auth/login", json={"email": "other_cand@interview.ai", "password": "candidate123"})
        self.other_token = res_other.json.get("token") if res_other.json else ""
        self.other_headers = {"Authorization": f"Bearer {self.other_token}"}

        res_a = self.client.post("/api/auth/login", json={"portal": "admin", "admin_id": self.admin.admin_id or "ADM-2026-001", "password": "admin123"})
        self.admin_token = res_a.json.get("token") if res_a.json else ""
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def tearDown(self):
        self.ctx.pop()

    # -------------------------------------------------------------------------
    # 1. Canonical Candidate-ID Key Generation
    # -------------------------------------------------------------------------
    def test_canonical_object_keys(self):
        cid = "CID-2026-HDP62N"

        # Resume
        k_resume = SupabaseStorageClient.build_object_key(cid, "resume", ext="pdf")
        self.assertEqual(k_resume, "CID-2026-HDP62N/resume/CID-2026-HDP62N.pdf")

        # Registration Photo
        k_photo = SupabaseStorageClient.build_object_key(cid, "registration_photo", ext="jpg")
        self.assertEqual(k_photo, "CID-2026-HDP62N/registration-photo/CID-2026-HDP62N.jpg")

        # Interview Video
        k_video = SupabaseStorageClient.build_object_key(cid, "interview_video", ext="mp4")
        self.assertEqual(k_video, "CID-2026-HDP62N/interview/video/CID-2026-HDP62N.mp4")

        # Question Video
        k_qvideo = SupabaseStorageClient.build_object_key(cid, "interview_video", ext="webm", index=2)
        self.assertEqual(k_qvideo, "CID-2026-HDP62N/interview/video/CID-2026-HDP62N_q2.webm")

        # Interview Snapshot
        k_snap = SupabaseStorageClient.build_object_key(cid, "interview_photo", index=1, ext="jpg")
        self.assertEqual(k_snap, "CID-2026-HDP62N/interview/photos/001.jpg")

        # Assessment Report
        k_report = SupabaseStorageClient.build_object_key(cid, "report", ext="pdf")
        self.assertEqual(k_report, "CID-2026-HDP62N/report/CID-2026-HDP62N-report.pdf")

    # -------------------------------------------------------------------------
    # 2. PostgreSQL candidate_files Storage Coordinator
    # -------------------------------------------------------------------------
    def test_save_candidate_file_and_postgres_tracking(self):
        cid = "CID-2026-HDP62N"
        sample_cv_content = b"%PDF-1.4 Mock CV Content for Rahul Kumar Pandit"

        file_rec, err = StorageService.save_candidate_file(
            candidate_id=cid,
            file_type="resume",
            file_input=sample_cv_content,
            filename="CID-2026-HDP62N.pdf",
            user_id=self.candidate.id,
            content_type="application/pdf"
        )
        self.assertIsNone(err)
        self.assertIsNotNone(file_rec)
        self.assertEqual(file_rec.candidate_id, cid)
        self.assertEqual(file_rec.file_type, "resume")
        self.assertEqual(file_rec.object_key, "CID-2026-HDP62N/resume/CID-2026-HDP62N.pdf")
        self.assertGreater(file_rec.file_size, 0)

        # Verify DB query
        db_rec = CandidateFile.query.filter_by(object_key="CID-2026-HDP62N/resume/CID-2026-HDP62N.pdf").first()
        self.assertIsNotNone(db_rec)
        self.assertEqual(db_rec.user_id, self.candidate.id)

    # -------------------------------------------------------------------------
    # 3. File Retrieval Stream / Bytes
    # -------------------------------------------------------------------------
    def test_file_stream_retrieval(self):
        cid = "CID-2026-HDP62N"
        test_photo_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01Mock JPEG Data"

        file_rec, err = StorageService.save_candidate_file(
            candidate_id=cid,
            file_type="registration_photo",
            file_input=test_photo_bytes,
            filename="CID-2026-HDP62N.jpg",
            user_id=self.candidate.id,
            content_type="image/jpeg"
        )
        self.assertIsNone(err)

        key = "CID-2026-HDP62N/registration-photo/CID-2026-HDP62N.jpg"
        retrieved_bytes, mime, fname = StorageService.get_file_stream_or_bytes(key)
        self.assertIsNotNone(retrieved_bytes)
        self.assertEqual(mime, "image/jpeg")

    # -------------------------------------------------------------------------
    # 4. Access Authorization & Candidate Isolation
    # -------------------------------------------------------------------------
    def test_security_authorization_checks(self):
        cand_key = "CID-2026-HDP62N/resume/CID-2026-HDP62N.pdf"

        # Owner candidate can access
        self.assertTrue(StorageService.check_authorization(self.candidate, cand_key))

        # Admin can access
        self.assertTrue(StorageService.check_authorization(self.admin, cand_key))

        # Other candidate CANNOT access
        self.assertFalse(StorageService.check_authorization(self.other_cand, cand_key))

        # Anonymous user CANNOT access
        self.assertFalse(StorageService.check_authorization(None, cand_key))

    # -------------------------------------------------------------------------
    # 5. REST API Storage Endpoints
    # -------------------------------------------------------------------------
    def test_api_storage_health(self):
        res = self.client.get("/api/storage/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get("status"), "online")
        self.assertEqual(res.json.get("storage_provider"), "supabase")
        self.assertIn("bucket_name", res.json)

    def test_api_get_file_authenticated(self):
        cid = "CID-2026-HDP62N"
        StorageService.save_candidate_file(
            candidate_id=cid,
            file_type="report",
            file_input=b"%PDF-1.4 Mock Report",
            filename="CID-2026-HDP62N-report.pdf",
            user_id=self.candidate.id,
            content_type="application/pdf"
        )

        key = "CID-2026-HDP62N/report/CID-2026-HDP62N-report.pdf"

        # Candidate accessing own report -> 200
        res = self.client.get(f"/api/storage/file/{key}", headers=self.cand_headers)
        self.assertEqual(res.status_code, 200)

        # Other candidate accessing report -> 403 Forbidden
        res_blocked = self.client.get(f"/api/storage/file/{key}", headers=self.other_headers)
        self.assertEqual(res_blocked.status_code, 403)

        # Unauthenticated access -> 401 Unauthorized
        res_unauth = self.client.get(f"/api/storage/file/{key}")
        self.assertEqual(res_unauth.status_code, 401)

    def test_api_signed_url(self):
        key = "CID-2026-HDP62N/resume/CID-2026-HDP62N.pdf"
        res = self.client.get(f"/api/storage/signed-url?key={key}", headers=self.cand_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get("status"), "success")

    def test_api_candidate_files_list(self):
        cid = "CID-2026-HDP62N"
        StorageService.save_candidate_file(
            candidate_id=cid,
            file_type="resume",
            file_input=b"%PDF-1.4 Mock CV",
            filename="CID-2026-HDP62N.pdf",
            user_id=self.candidate.id,
            content_type="application/pdf"
        )
        res = self.client.get(f"/api/storage/candidate/{cid}/files", headers=self.cand_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json.get("status"), "success")
        self.assertGreaterEqual(res.json.get("total_files", 0), 1)


def run_all():
    suite = unittest.TestLoader().loadTestsFromTestCase(SupabaseStorageTests)
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    print("=" * 72)
    print(f"  SUPABASE STORAGE TEST SUITE: {res.testsRun} run, {len(res.failures)} failed, {len(res.errors)} errors")
    print("=" * 72)
    assert res.wasSuccessful(), "Supabase Storage Tests Failed"


if __name__ == "__main__":
    run_all()
