"""
test_admin_create_candidate.py
Automated test suite for Admin Candidate Creation:
- Automatic unique Candidate ID generation (CID-YYYY-XXXXXX)
- Duplicate Candidate ID prevention
- Admin setting candidate password
- Successful login of newly created candidate using Candidate ID and set password
- Duplicate email prevention and password validation
- RBAC enforcement (only admins can access)
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

class TestAdminCreateCandidate(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.ts = int(time.time())
        self.rand = uuid.uuid4().hex[:6]

        # 1. Ensure admin account exists
        self.admin = User.query.filter_by(admin_id="ADM-2026-001").first()
        if not self.admin:
            self.admin = User(
                admin_id="ADM-2026-001",
                full_name="System Administrator (Mid-West University)",
                email=f"admin_{self.ts}_{self.rand}@interview.ai",
                role="admin",
                institution="Mid-West University",
                target_role="Recruitment Lead"
            )
            self.admin.set_password("admin123")
            db.session.add(self.admin)
            db.session.commit()

        # Login as admin to get token
        res = self.client.post("/api/auth/login", json={
            "portal": "admin",
            "admin_id": "ADM-2026-001",
            "password": "admin123"
        })
        self.assertEqual(res.status_code, 200)
        self.admin_token = res.get_json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def tearDown(self):
        self.app_context.pop()

    def test_01_create_candidate_with_auto_generated_unique_id(self):
        """Test admin creating candidate auto-generates unique Candidate ID and sets password"""
        cand_email = f"auto_cand_{self.ts}_{self.rand}_1@interview.ai"
        cand_pwd = "CandidateSecret2026!"

        res = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
            "full_name": "Aayush Sharma",
            "email": cand_email,
            "password": cand_pwd,
            "target_role": "Full Stack Developer",
            "institution": "Mid-West University"
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")

        cand_info = data["candidate"]
        cid = cand_info["candidate_id"]
        self.assertTrue(cid.startswith("CID-2026-"))
        self.assertEqual(len(cid), 15)  # CID-2026-XXXXXX is 15 chars
        self.assertEqual(cand_info["email"], cand_email)
        print(f"[PASS] 1. Candidate created with auto-generated unique ID: {cid}")

        # Verify candidate can sign in using newly generated Candidate ID & set password
        login_res_cid = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "identifier": cid,
            "password": cand_pwd
        })
        self.assertEqual(login_res_cid.status_code, 200)
        self.assertIn("token", login_res_cid.get_json())
        print(f"[PASS] 1b. Candidate successfully logged in using Candidate ID {cid} and admin-set password.")

        # Verify candidate can also sign in using Email & set password
        login_res_email = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": cand_email,
            "password": cand_pwd
        })
        self.assertEqual(login_res_email.status_code, 200)
        print("[PASS] 1c. Candidate successfully logged in using Email.")

    def test_02_candidate_id_uniqueness_and_duplicate_prevention(self):
        """Test creating multiple candidates generates distinct, non-colliding IDs"""
        generated_cids = set()

        for i in range(5):
            email = f"multi_cand_{self.ts}_{self.rand}_{i}@interview.ai"
            res = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
                "full_name": f"Candidate Test {i}",
                "email": email,
                "password": f"Password{i}!1234",
                "target_role": "Software Engineer"
            })
            self.assertEqual(res.status_code, 201)
            cid = res.get_json()["candidate"]["candidate_id"]
            self.assertNotIn(cid, generated_cids, f"Collision detected for candidate ID {cid}")
            generated_cids.add(cid)

        self.assertEqual(len(generated_cids), 5)
        print(f"[PASS] 2. Verified 5 consecutive candidate IDs are strictly unique: {list(generated_cids)}")

    def test_03_validation_rules(self):
        """Test password length and duplicate email validation"""
        # 1. Short password (< 6 chars)
        res1 = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
            "full_name": "Short Pwd",
            "email": f"short_{self.ts}_{self.rand}@interview.ai",
            "password": "123"
        })
        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res1.get_json()["code"], "PASSWORD_TOO_SHORT")

        # 2. Duplicate email
        existing_email = f"dup_{self.ts}_{self.rand}@interview.ai"
        res2_a = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
            "full_name": "First User",
            "email": existing_email,
            "password": "ValidPassword123!"
        })
        self.assertEqual(res2_a.status_code, 201)

        res2_b = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
            "full_name": "Second User",
            "email": existing_email,
            "password": "AnotherValidPassword123!"
        })
        self.assertEqual(res2_b.status_code, 409)
        self.assertEqual(res2_b.get_json()["code"], "EMAIL_ALREADY_EXISTS")
        print("[PASS] 3. Validation rules enforced: password >= 6 and duplicate email rejected.")

    def test_04_candidate_appears_in_admin_list(self):
        """Test newly created candidate appears in /api/admin/candidates"""
        email = f"list_cand_{self.ts}_{self.rand}@interview.ai"
        res_create = self.client.post("/api/admin/candidates/create", headers=self.admin_headers, json={
            "full_name": "Listing Check Candidate",
            "email": email,
            "password": "ListCandidatePass123!",
            "target_role": "Data Scientist"
        })
        self.assertEqual(res_create.status_code, 201)
        created_cid = res_create.get_json()["candidate"]["candidate_id"]

        res_list = self.client.get("/api/admin/candidates", headers=self.admin_headers)
        self.assertEqual(res_list.status_code, 200)
        candidates = res_list.get_json()["candidates"]

        matching = [c for c in candidates if c["candidate_id"] == created_cid]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["full_name"], "Listing Check Candidate")
        self.assertEqual(matching[0]["target_role"], "Data Scientist")
        print(f"[PASS] 4. Created candidate {created_cid} properly listed in Admin Candidates API.")

    def test_05_unauthorized_access_prevented(self):
        """Test candidates and unauthenticated requests cannot create candidates"""
        # Unauthenticated request
        res1 = self.client.post("/api/admin/candidates/create", json={
            "full_name": "Hacker Attempt",
            "email": "hacker@interview.ai",
            "password": "HackerPassword123!"
        })
        self.assertEqual(res1.status_code, 401)

        # Candidate user trying to create candidates
        candidate = User(
            candidate_id=User.generate_candidate_id(),
            full_name="Regular Candidate",
            email=f"cand_user_{self.ts}_{self.rand}@interview.ai",
            role="candidate"
        )
        candidate.set_password("Candidate123!")
        db.session.add(candidate)
        db.session.commit()

        login_res = self.client.post("/api/auth/login", json={
            "portal": "candidate",
            "email": candidate.email,
            "password": "Candidate123!"
        })
        cand_token = login_res.get_json()["token"]

        res2 = self.client.post("/api/admin/candidates/create", headers={"Authorization": f"Bearer {cand_token}"}, json={
            "full_name": "Unauthorized Attempt",
            "email": "unauth@interview.ai",
            "password": "Password123!"
        })
        self.assertEqual(res2.status_code, 403)
        print("[PASS] 5. RBAC security strictly enforced: unauthenticated & candidate access rejected.")

if __name__ == "__main__":
    unittest.main()
