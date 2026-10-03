#!/usr/bin/env python
"""
test_admin_access.py
Comprehensive automated test suite verifying:
1. Public Administrator registration is disabled (HTTP 403).
2. Admin accounts are provisioned exclusively by company/university.
3. Admins can log in ONLY using official Admin ID and password (email login rejected).
4. Frontend registration & login templates have Admin Register option removed.
5. Role-based access control (RBAC) strictly prevents candidates from accessing admin features.
"""

import sys
import os
import time
import uuid

# Ensure root workspace is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.services.database import db
from backend.models.user import User
from backend.utils.security import generate_verification_token

def run_tests():
    print("=" * 80)
    print("  RUNNING SECURE ADMINISTRATOR ACCESS & RBAC VERIFICATION SUITE")
    print("=" * 80)

    app = create_app()
    client = app.test_client()
    passed = 0
    total = 0

    ts = int(time.time())
    rand_id = uuid.uuid4().hex[:6]

    def check(test_id, description, condition, extra=""):
        nonlocal passed, total
        total += 1
        status = "PASSED" if condition else "FAILED"
        if condition:
            passed += 1
        print(f"[{test_id}] {description.ljust(56)}: [{status}] {extra}")
        assert condition, f"Test {test_id} failed! {extra}"

    # -------------------------------------------------------------------------
    # PART 1: PUBLIC REGISTRATION RESTRICTIONS
    # -------------------------------------------------------------------------
    # 1.1 Reject registration with role="admin"
    res = client.post("/api/auth/register", json={
        "full_name": "Attacker Admin",
        "email": f"hacker_admin_{ts}_{rand_id}@test.com",
        "password": "Password123!",
        "role": "admin"
    })
    check("RBAC-01", "Public Registration with role='admin' Blocked (403)", res.status_code == 403 and "restricted" in res.json.get("message", "").lower())

    # 1.2 Reject registration with role="recruiter"
    res = client.post("/api/auth/register", json={
        "full_name": "Attacker Recruiter",
        "email": f"hacker_rec_{ts}_{rand_id}@test.com",
        "password": "Password123!",
        "role": "recruiter"
    })
    check("RBAC-02", "Public Registration with role='recruiter' Blocked (403)", res.status_code == 403 and "restricted" in res.json.get("message", "").lower())

    # 1.3 Candidate registration succeeds and gets candidate_id
    cand_email = f"candidate_rbac_{ts}_{rand_id}@interview.ai"
    cand_token_v = generate_verification_token(cand_email)
    res = client.post("/api/auth/register", json={
        "full_name": "Candidate Jane",
        "email": cand_email,
        "password": "Password123!",
        "target_role": "Software Engineer",
        "verification_token": cand_token_v
    })
    check("RBAC-03", "Public Registration creates Candidate Account (201)", res.status_code == 201 and res.json["user"]["role"] == "candidate" and res.json.get("candidate_id") is not None)
    cand_cid = res.json["candidate_id"]
    cand_token = res.json["token"]
    cand_headers = {"Authorization": f"Bearer {cand_token}"}

    # -------------------------------------------------------------------------
    # PART 2: ADMIN LOGIN ONLY USING OFFICIAL ADMIN ID
    # -------------------------------------------------------------------------
    # 2.1 Admin trying to log in via Admin Portal with email -> Rejected (400)
    res = client.post("/api/auth/login", json={
        "portal": "admin",
        "email": "admin@interview.ai",
        "password": "admin123"
    })
    check("RBAC-04", "Admin Portal Email Login Rejected (400)", res.status_code == 400 and "official admin id" in res.json.get("message", "").lower())

    # 2.2 Admin trying to log in via Candidate Portal with email -> Rejected (403)
    res = client.post("/api/auth/login", json={
        "portal": "candidate",
        "email": "admin@interview.ai",
        "password": "admin123"
    })
    check("RBAC-05", "Admin Account in Candidate Portal Blocked (403)", res.status_code == 403 and "administrator portal" in res.json.get("message", "").lower())

    # 2.3 Direct API login with admin email -> Rejected (403)
    res = client.post("/api/auth/login", json={
        "email": "admin@interview.ai",
        "password": "admin123"
    })
    check("RBAC-06", "Direct API Email Login for Admin Blocked (403)", res.status_code == 403 and "official admin id" in res.json.get("message", "").lower())

    # 2.4 Admin login with official Admin ID -> Success (200)
    res = client.post("/api/auth/login", json={
        "portal": "admin",
        "admin_id": "ADM-2026-001",
        "password": "admin123"
    })
    check("RBAC-07", "Admin Login with Official Admin ID (200)", res.status_code == 200 and res.json["user"]["role"] == "admin" and res.json["user"]["admin_id"] == "ADM-2026-001")
    admin_token = res.json["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2.5 Candidate trying to log in to Administrator Portal using Candidate ID -> Blocked (403)
    res = client.post("/api/auth/login", json={
        "portal": "admin",
        "admin_id": cand_cid,
        "password": "Password123!"
    })
    check("RBAC-08", "Candidate ID in Administrator Portal Blocked (403)", res.status_code == 403 and "candidate accounts cannot access" in res.json.get("message", "").lower())

    # -------------------------------------------------------------------------
    # PART 3: RBAC ENFORCEMENT ON ADMIN FEATURES
    # -------------------------------------------------------------------------
    # 3.1 Candidate cannot access /api/admin/stats
    res = client.get("/api/admin/stats", headers=cand_headers)
    check("RBAC-09", "Candidate Access to /api/admin/stats Denied (403)", res.status_code == 403)

    # 3.2 Candidate cannot access /api/admin/candidates
    res = client.get("/api/admin/candidates", headers=cand_headers)
    check("RBAC-10", "Candidate Access to /api/admin/candidates Denied (403)", res.status_code == 403)

    # 3.3 Candidate cannot access /api/admin/raw-db
    res = client.get("/api/admin/raw-db", headers=cand_headers)
    check("RBAC-11", "Candidate Access to /api/admin/raw-db Denied (403)", res.status_code == 403)

    # 3.4 Unauthenticated access to /api/admin/raw-db -> 401
    res = client.get("/api/admin/raw-db")
    check("RBAC-12", "Unauthenticated Access to /api/admin/raw-db Denied (401)", res.status_code == 401)

    # 3.5 Admin successfully accesses /api/admin/stats
    res = client.get("/api/admin/stats", headers=admin_headers)
    check("RBAC-13", "Admin Access to /api/admin/stats Allowed (200)", res.status_code == 200 and "total_candidates" in res.json.get("data", {}))

    # 3.6 Admin successfully accesses /api/admin/raw-db
    res = client.get("/api/admin/raw-db", headers=admin_headers)
    check("RBAC-14", "Admin Access to /api/admin/raw-db Allowed (200)", res.status_code == 200 and "tables" in res.json)

    # -------------------------------------------------------------------------
    # PART 4: INSTITUTIONAL PROVISIONING OF NEW ADMIN ACCOUNTS
    # -------------------------------------------------------------------------
    # 4.1 Candidate cannot provision an admin account
    res = client.post("/api/admin/provision", json={
        "full_name": "Rogue Admin",
        "email": f"rogue_{ts}_{rand_id}@test.com",
        "password": "Password123!"
    }, headers=cand_headers)
    check("RBAC-15", "Candidate Provision Admin Forbidden (403)", res.status_code == 403)

    # 4.2 Authorized Admin provisions a new University / Company Admin
    new_admin_email = f"dean_engineering_{ts}_{rand_id}@mwu.edu.np"
    res = client.post("/api/admin/provision", json={
        "full_name": "Prof. Engineering Dean",
        "email": new_admin_email,
        "password": "DeanPassword123!",
        "institution": "Mid-West University",
        "target_role": "Academic Dean"
    }, headers=admin_headers)
    check("RBAC-16", "Institutional Admin Provisioning (201)", res.status_code == 201 and "admin" in res.json)
    new_admin_id = res.json["admin"]["admin_id"]
    check("RBAC-16b", "Auto-generated Admin ID Format (ADM-YYYY-XXX)", new_admin_id.startswith("ADM-") and len(new_admin_id.split("-")) == 3, f"Issued: {new_admin_id}")

    # 4.3 Newly provisioned Admin logs in using the issued Admin ID
    res = client.post("/api/auth/login", json={
        "portal": "admin",
        "admin_id": new_admin_id,
        "password": "DeanPassword123!"
    })
    check("RBAC-17", "Newly Provisioned Admin Logs in with Issued Admin ID (200)", res.status_code == 200 and res.json["user"]["admin_id"] == new_admin_id)

    # -------------------------------------------------------------------------
    # PART 5: FRONTEND TEMPLATE SECURITY AUDIT
    # -------------------------------------------------------------------------
    with open(os.path.join(PROJECT_ROOT, "frontend", "register.html"), "r", encoding="utf-8") as f:
        reg_html = f.read()
    check("RBAC-18", "register.html has no recruiter/admin option", 'value="recruiter"' not in reg_html and 'value="admin"' not in reg_html)

    with open(os.path.join(PROJECT_ROOT, "frontend", "login.html"), "r", encoding="utf-8") as f:
        login_html = f.read()
    check("RBAC-19", "login.html prompts for Official Admin ID", "Official Admin ID" in login_html and "ADM-2026-001" in login_html)

    check("RBAC-20", "register.html file upload input removed (camera only)", 'type="file"' not in reg_html and "photo-file-input" not in reg_html and "btn-open-camera" in reg_html)

    print("=" * 80)
    print(f"  ALL RBAC & ADMIN ACCESS TESTS PASSED: {passed}/{total} ({(passed/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
