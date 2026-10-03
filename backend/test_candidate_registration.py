"""
test_candidate_registration.py - Automated test suite for Candidate Registration,
Photo Upload/Webcam Snapshot handling, and Permanent Unique Candidate ID Generation.
"""

import os
import sys
import io
import base64
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.config import Config
from backend.utils.security import generate_verification_token

def create_mock_image(color=(70, 130, 180), size=(300, 300), format="JPEG"):
    """Creates an in-memory test image."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    buf.seek(0)
    return buf

def run_tests():
    print("=" * 75)
    print("  RUNNING CANDIDATE REGISTRATION & UNIQUE CANDIDATE ID TESTS")
    print("=" * 75)

    import time
    import uuid
    ts = int(time.time())
    rand_suffix = uuid.uuid4().hex[:6]

    client = app.test_client()
    passed = 0
    total = 0

    def check(test_id, name, condition, details=""):
        nonlocal passed, total
        total += 1
        status = "PASSED" if condition else "FAILED"
        if condition:
            passed += 1
        print(f"[{test_id}] {name.ljust(44)}: [{status}] {details}")
        assert condition, f"Test {test_id} failed: {details}"

    # TC-CR-01: Register candidate with Profile Photo (File Upload)
    cand_email_1 = f"aarav_{ts}_{rand_suffix}@interview.ai"
    mock_file = create_mock_image(color=(255, 99, 71))
    token_1 = generate_verification_token(cand_email_1)
    res = client.post("/api/auth/register", data={
        "full_name": "Aarav Sharma",
        "email": cand_email_1,
        "password": "Password123!",
        "role": "candidate",
        "target_role": "AI/ML Engineer",
        "phone": "+977-9841234567",
        "verification_token": token_1,
        "profile_photo": (mock_file, "aarav_avatar.jpg")
    }, content_type="multipart/form-data")

    check("TC-CR-01", "Register Candidate with File Photo", res.status_code == 201 and "candidate_id" in res.json)
    cid_1 = res.json.get("candidate_id")
    check("TC-CR-01b", "Candidate ID Format (CID-YYYY-XXXXXX)", cid_1.startswith("CID-") and len(cid_1.split("-")) == 3, f"ID: {cid_1}")
    
    photo_rel_path = res.json["user"]["profile_photo"]
    check("TC-CR-01c", "Profile Photo Stored on Disk", photo_rel_path and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, photo_rel_path)), f"Path: {photo_rel_path}")

    # TC-CR-02: Register candidate with Webcam Snapshot (Base64)
    cand_email_2 = f"pooja_{ts}_{rand_suffix}@interview.ai"
    mock_webcam_buf = create_mock_image(color=(34, 139, 34))
    b64_str = "data:image/jpeg;base64," + base64.b64encode(mock_webcam_buf.read()).decode("utf-8")
    token_2 = generate_verification_token(cand_email_2)
    
    res = client.post("/api/auth/register", json={
        "full_name": "Pooja Thapa",
        "email": cand_email_2,
        "password": "Password123!",
        "role": "candidate",
        "target_role": "Full Stack Developer",
        "verification_token": token_2,
        "profile_photo": b64_str
    })

    check("TC-CR-02", "Register Candidate with Webcam Snapshot", res.status_code == 201 and "candidate_id" in res.json)
    cid_2 = res.json.get("candidate_id")
    check("TC-CR-02b", "Candidate ID Format for Webcam Registration", cid_2.startswith("CID-"), f"ID: {cid_2}")
    check("TC-CR-02c", "Webcam Photo Stored on Disk", os.path.exists(os.path.join(Config.UPLOAD_FOLDER, res.json["user"]["profile_photo"])))

    # TC-CR-03: Candidate ID Uniqueness across multiple registrations
    registered_ids = [cid_1, cid_2]
    for i in range(5):
        img_buf = create_mock_image()
        b_email = f"batch_{i}_{ts}_{rand_suffix}@interview.ai"
        b_token = generate_verification_token(b_email)
        r = client.post("/api/auth/register", data={
            "full_name": f"Batch Candidate {i}",
            "email": b_email,
            "password": "Password123!",
            "role": "candidate",
            "target_role": "Software Engineer",
            "verification_token": b_token,
            "profile_photo": (img_buf, f"batch_{i}.png")
        }, content_type="multipart/form-data")
        assert r.status_code == 201
        registered_ids.append(r.json["candidate_id"])

    unique_ids_set = set(registered_ids)
    check("TC-CR-03", "Candidate ID Uniqueness (0 collisions)", len(unique_ids_set) == len(registered_ids), f"{len(unique_ids_set)} distinct IDs generated")


    # TC-CR-04: Candidate ID Permanence (Unchanged upon login & profile retrieval)
    login_res = client.post("/api/auth/login", json={
        "portal": "candidate",
        "email": cand_email_1,
        "password": "Password123!"
    })
    check("TC-CR-04", "Candidate ID Permanence on Login", login_res.status_code == 200 and login_res.json["user"]["candidate_id"] == cid_1, f"Expected {cid_1}")

    token = login_res.json["token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    check("TC-CR-04b", "Candidate ID & Photo URL in /api/auth/me", me_res.status_code == 200 and me_res.json["user"]["candidate_id"] == cid_1 and me_res.json["user"]["profile_photo_url"] is not None)

    # TC-CR-05: Public Administrator registration is restricted (HTTP 403)
    admin_reg = client.post("/api/auth/register", json={
        "full_name": "Unauthorized Admin Attempt",
        "email": f"unauthorized_admin_{ts}_{rand_suffix}@interview.ai",
        "password": "Password123!",
        "role": "admin",
        "target_role": "Recruitment Lead"
    })
    check("TC-CR-05", "Public Admin Registration Forbidden (HTTP 403)", admin_reg.status_code == 403)

    # TC-CR-06: Recruiter/Admin View Candidate List & Profile via Official Admin ID Login
    admin_login = client.post("/api/auth/login", json={
        "portal": "admin",
        "admin_id": "ADM-2026-001",
        "password": "admin123"
    })
    admin_token = admin_login.json["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    cand_list_res = client.get("/api/admin/candidates", headers=admin_headers)
    candidates = cand_list_res.json.get("candidates", [])
    has_cid_and_photo = any(c.get("candidate_id") == cid_1 and c.get("profile_photo_url") for c in candidates)
    check("TC-CR-06", "Admin Candidates List contains Candidate ID & Photo", cand_list_res.status_code == 200 and has_cid_and_photo)

    # TC-CR-07: Error Handling - Corrupted Image Upload
    corrupted_stream = io.BytesIO(b"NOT_A_VALID_IMAGE_DATA_BYTES")
    bad_email = f"bad_image_{ts}_{rand_suffix}@interview.ai"
    bad_token = generate_verification_token(bad_email)
    bad_res = client.post("/api/auth/register", data={
        "full_name": "Bad Image Candidate",
        "email": bad_email,
        "password": "Password123!",
        "role": "candidate",
        "verification_token": bad_token,
        "profile_photo": (corrupted_stream, "corrupted.jpg")
    }, content_type="multipart/form-data")
    check("TC-CR-07", "Error Handling on Corrupted Photo Upload", bad_res.status_code == 400 and "failed" in bad_res.json["message"].lower())

    print("=" * 75)
    print(f"  TEST SUMMARY: {passed}/{total} TESTS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
