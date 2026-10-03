"""
test_postgresql_integration.py - Automated test suite for PostgreSQL Schema & Alembic Migration Compatibility
Tests:
  - Database schema models metadata integrity
  - Alembic migration file structure & version consistency
  - Primary keys, foreign keys, unique constraints & indexes
  - Candidate ID centrality across all related tables (User, Resume, Interview, Report, CandidateFile)
  - Data integrity and relationship cascade behavior
"""

import os
import sys
import time
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.services.database import db
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.interview import Interview, InterviewResponse, ProctoringViolation
from backend.models.report import Report
from backend.models.otp import EmailOTP
from backend.models.stored_file import CandidateFile
from backend.config import Config

def run_tests():
    print("=" * 80)
    print("  RUNNING POSTGRESQL & SCHEMA INTEGRATION TESTS")
    print("=" * 80)

    passed = 0
    total = 0

    def check(test_id, name, condition, details=""):
        nonlocal passed, total
        total += 1
        status = "PASSED" if condition else "FAILED"
        if condition:
            passed += 1
        print(f"[{test_id}] {name.ljust(52)}: [{status}] {details}")
        assert condition, f"Test {test_id} failed: {details}"

    with app.app_context():
        # TC-PG-01: Metadata inspection
        tables = db.metadata.tables
        check("TC-PG-01a", "All Core Tables in SQLAlchemy Metadata", all(t in tables for t in [
            "users", "resumes", "questions", "interviews", "interview_responses",
            "interview_proctoring_violations", "reports", "email_otps", "candidate_files"
        ]))

        # TC-PG-02: Check Alembic Migration Revision
        from alembic.config import Config as AlembicConfig
        from alembic.script import ScriptDirectory
        alembic_cfg = AlembicConfig("alembic.ini")
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(script_dir.walk_revisions())
        check("TC-PG-02", "Alembic Initial Migration Available", len(revisions) >= 1 and revisions[0].revision in ["001_initial_supabase", "001_initial_schema"])

        # TC-PG-03: Candidate ID Centrality & Integrity
        ts = int(time.time())
        rand_s = uuid.uuid4().hex[:6]
        cid = f"CID-2026-PG{rand_s.upper()}"

        user = User(
            candidate_id=cid,
            full_name="PostgreSQL Test Candidate",
            email=f"pg_candidate_{ts}_{rand_s}@interview.ai",
            role="candidate",
            target_role="Cloud Engineer"
        )
        user.set_password("SecurePass123!")
        db.session.add(user)
        db.session.commit()

        check("TC-PG-03a", "Candidate Created with Permanent Candidate ID", user.id is not None and user.candidate_id == cid)

        # Create Resume linked to Candidate
        resume = Resume(
            user_id=user.id,
            filename=f"{cid}.pdf",
            file_path=f"resumes/{cid}.pdf",
            candidate_name=user.full_name,
            education="B.Sc. Computer Science",
            experience="3 years backend engineering",
            screening_score=85.0,
            is_verified=True,
            verification_status="verified"
        )
        resume.set_technical_skills(["PostgreSQL", "Cloudflare R2", "FastAPI", "Python"])
        db.session.add(resume)
        db.session.commit()

        check("TC-PG-03b", "Resume Linked via Foreign Key", resume.id is not None and resume.user.candidate_id == cid)

        # Create Interview linked to Candidate
        interview = Interview(
            user_id=user.id,
            target_role="Cloud Engineer",
            status="completed",
            overall_score=88.5,
            recording_path=f"{cid}/interview/video/{cid}.mp4"
        )
        db.session.add(interview)
        db.session.commit()

        # Add Responses & Violations
        resp = InterviewResponse(
            interview_id=interview.id,
            question_text="Explain ACID transactions in PostgreSQL.",
            transcript="ACID stands for Atomicity, Consistency, Isolation, and Durability.",
            relevance_score=92.0,
            technical_score=90.0,
            duration_seconds=30.0
        )
        db.session.add(resp)

        violation = ProctoringViolation(
            interview_id=interview.id,
            faces_detected=1,
            warning_level="clean",
            message="Environment verified clean"
        )
        db.session.add(violation)

        # Add Report
        report = Report(
            interview_id=interview.id,
            user_id=user.id,
            candidate_name=user.full_name,
            target_role="Cloud Engineer",
            overall_score=88.5,
            communication_score=86.0,
            technical_score=91.0,
            confidence_score=88.0,
            eye_contact_pct=85.0
        )
        report.set_strengths(["Strong database knowledge", "Clear communication"])
        report.set_weaknesses(["Could provide more real-world examples"])
        db.session.add(report)

        # Add Candidate Files
        cf_cv = CandidateFile(
            candidate_id=cid,
            user_id=user.id,
            file_type="resume",
            object_key=f"{cid}/resume/{cid}.pdf",
            file_name=f"{cid}.pdf",
            mime_type="application/pdf"
        )
        cf_vid = CandidateFile(
            candidate_id=cid,
            user_id=user.id,
            interview_id=interview.id,
            file_type="interview_video",
            object_key=f"{cid}/interview/video/{cid}.mp4",
            file_name=f"{cid}.mp4",
            mime_type="video/mp4"
        )
        db.session.add(cf_cv)
        db.session.add(cf_vid)
        db.session.commit()

        check("TC-PG-03c", "Complete Candidate Graph Linked by Candidate ID",
              len(user.resumes) == 1 and len(user.interviews) == 1 and len(user.candidate_files) == 2)

        # TC-PG-04: Unique Constraints Enforcement & Validation
        check("TC-PG-04a", "Candidate ID Unique Constraint in Metadata",
              User.__table__.c.candidate_id.unique is True or any(idx.unique and "candidate_id" in [c.name for c in idx.columns] for idx in User.__table__.indexes))

        dup_email_user = User(
            candidate_id=f"CID-2026-UNIQ{rand_s.upper()}",
            full_name="Duplicate Email Candidate",
            email=user.email, # Duplicate email
            role="candidate"
        )
        dup_email_user.set_password("pass123")
        db.session.add(dup_email_user)
        is_rejected = False
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            is_rejected = True

        check("TC-PG-04b", "Duplicate Record Rejected by Unique Constraint", is_rejected)

    print("=" * 80)
    print(f"  POSTGRESQL TEST SUMMARY: {passed}/{total} TESTS PASSED ({(passed/total)*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
