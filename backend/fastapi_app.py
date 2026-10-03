"""
fastapi_app.py
High-performance FastAPI application for the AI Interview System IT Question & Answer API.

Endpoints:
- POST /api/qa/ask : Ask an IT question and receive a beginner-friendly answer
- GET  /api/qa/categories : List all 21 supported IT categories
- GET  /api/qa/stats : Statistics on questions and models
- GET  / : Interactive API overview and documentation links
"""

import os
import sys
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.qa_service import QAService

app = FastAPI(
    title="AI Interview System - IT Q&A API",
    description="Fine-tuned IT Question & Answer endpoint and Knowledge Base for Beginner-Level IT Interviews",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str = Field(..., example="What is Python?")
    style: Optional[str] = Field("standard", description="Answer depth: 'short', 'standard', or 'detailed'")


class QuestionResponse(BaseModel):
    question: str
    answer: str


@app.get("/")
def root():
    return {
        "system": "AI-Powered Intelligent Video Interview Assessment System",
        "module": "IT Technical Q&A Intelligence Engine",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "ask_api": "POST /api/qa/ask",
            "categories": "GET /api/qa/categories",
            "stats": "GET /api/qa/stats",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.post("/api/qa/ask", response_model=QuestionResponse)
def ask_question(req: QuestionRequest):
    """
    Submits an IT interview question and receives an accurate answer.
    Supports paraphrased and natural variations of questions.
    """
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="The 'question' field cannot be empty.")

    result = QAService.answer_question(req.question, answer_style=req.style or "standard")
    return QuestionResponse(
        question=result["question"],
        answer=result["answer"]
    )


@app.get("/api/qa/categories")
def get_categories():
    """Returns the list of 21 supported IT categories."""
    json_path = os.path.join(PROJECT_ROOT, "backend", "datasets", "it_questions.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(PROJECT_ROOT, "it_questions.json")

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cat_counts = {}
        for item in data:
            cat = item.get("category", "General")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        return {"status": "success", "total_categories": len(cat_counts), "categories": cat_counts}

    return {"status": "error", "message": "Dataset not found"}


# =========================================================================
# Email OTP Verification & Candidate Registration Endpoints
# =========================================================================
class SendOTPRequest(BaseModel):
    email: str = Field(..., example="candidate@example.com")
    full_name: Optional[str] = Field("Candidate", example="Aarav Sharma")


class VerifyOTPRequest(BaseModel):
    email: str = Field(..., example="candidate@example.com")
    otp: str = Field(..., example="123456")


class ResendOTPRequest(BaseModel):
    email: str = Field(..., example="candidate@example.com")
    full_name: Optional[str] = Field("Candidate", example="Aarav Sharma")


class VerifyLinkRequest(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


class CandidateRegisterRequest(BaseModel):
    full_name: str = Field(..., example="Rahul Kumar")
    email: str = Field(..., example="rahul@example.com")
    password: str = Field(..., min_length=6, example="password123")
    target_role: Optional[str] = Field("Software Engineer", example="Software Engineer")
    phone: Optional[str] = Field(None, example="+977-9812345678")
    verification_token: Optional[str] = Field(None, description="Cryptographically signed verification token from /verify-otp")
    profile_photo: Optional[str] = Field(None, description="Base64 encoded JPEG or image URL")


@app.post("/api/auth/send-otp")
@app.post("/auth/send-otp")
def fastapi_send_otp(req: SendOTPRequest):
    """Sends a 6-digit verification code to any candidate email (Gmail, Outlook, Yahoo, University, etc.)."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.otp_service import OTPService
        res, status = OTPService.send_registration_otp(req.email, req.full_name or "Candidate")
        if status >= 400:
            raise HTTPException(status_code=status, detail=res.get("message", "Failed to send OTP"))
        return res


@app.post("/api/auth/verify-otp")
@app.post("/auth/verify-otp")
def fastapi_verify_otp(req: VerifyOTPRequest):
    """Verifies candidate 6-digit OTP code and issues a signed email verification token."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.otp_service import OTPService
        res, status = OTPService.verify_registration_otp(req.email, req.otp)
        if status >= 400:
            raise HTTPException(status_code=status, detail=res.get("message", "Invalid or expired OTP"))
        return res


@app.post("/api/auth/resend-otp")
@app.post("/auth/resend-otp")
def fastapi_resend_otp(req: ResendOTPRequest):
    """Resends a fresh 6-digit verification OTP with rate-limiting cooldown enforcement."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.otp_service import OTPService
        res, status = OTPService.resend_registration_otp(req.email, req.full_name or "Candidate")
        if status >= 400:
            raise HTTPException(status_code=status, detail=res.get("message", "Failed to resend OTP"))
        return res


@app.get("/api/auth/verify-link")
@app.get("/auth/verify-link")
@app.post("/api/auth/verify-link")
@app.post("/auth/verify-link")
def fastapi_verify_link(token: Optional[str] = None, req: Optional[VerifyLinkRequest] = None):
    """Verifies a token clicked from the candidate's verification email."""
    resolved_token = token or (req.token if req else None)
    if not resolved_token:
        raise HTTPException(status_code=400, detail="Verification token is required.")

    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.otp_service import OTPService
        res, status = OTPService.verify_email_link(resolved_token)
        if status >= 400:
            raise HTTPException(status_code=status, detail=res.get("message", "Invalid or expired link"))
        return res


@app.get("/api/auth/verification-status")
@app.get("/auth/verification-status")
def fastapi_verification_status(email: str):
    """Polls email verification status to auto-advance registration when link is clicked on another device."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.otp_service import OTPService
        res, status = OTPService.check_verification_status(email)
        if status >= 400:
            raise HTTPException(status_code=status, detail=res.get("message", "Verification status check failed"))
        return res


@app.post("/api/auth/register")
@app.post("/auth/register")
def fastapi_register(req: CandidateRegisterRequest):
    """Completes candidate registration after successful OTP email verification."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.services.database import db
        from backend.models.user import User
        from backend.utils.security import verify_email_token, generate_token
        from backend.utils.photo_storage import process_and_save_photo

        clean_email = req.email.strip().lower()
        if not req.verification_token or not verify_email_token(req.verification_token, expected_email=clean_email):
            raise HTTPException(
                status_code=403,
                detail="Email verification required. Candidate registration must be verified with a valid OTP."
            )

        if User.query.filter_by(email=clean_email).first():
            raise HTTPException(status_code=409, detail="An account with this email address already exists.")

        candidate_id = User.generate_candidate_id()
        photo_path = None
        if req.profile_photo:
            try:
                photo_path = process_and_save_photo(req.profile_photo, candidate_id)
            except Exception:
                pass

        user = User(
            candidate_id=candidate_id,
            full_name=req.full_name.strip(),
            email=clean_email,
            role="candidate",
            target_role=req.target_role or "Software Engineer",
            phone=req.phone,
            profile_photo=photo_path,
            email_verified=True
        )
        user.set_password(req.password)
        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id, role=user.role)
        return {
            "status": "success",
            "message": "Account registered successfully",
            "candidate_id": user.candidate_id,
            "token": token,
            "user": user.to_dict()
        }



@app.get("/api/qa/stats")
def get_stats():
    """Returns dataset and model statistics."""
    json_path = os.path.join(PROJECT_ROOT, "backend", "datasets", "it_questions.json")
    total_q = 0
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            total_q = len(json.load(f))

    kb_path = os.path.join(PROJECT_ROOT, "backend", "trained_models", "it_qa_kb.pkl")
    model_dir = os.path.join(PROJECT_ROOT, "backend", "trained_models", "it_qa_model")

    return {
        "status": "success",
        "total_questions": total_q,
        "total_training_examples": total_q * 3,
        "semantic_kb_active": os.path.exists(kb_path),
        "finetuned_model_active": os.path.exists(model_dir)
    }


# =========================================================================
# AI Proctoring & Multi-Person Presence Detection Endpoints
# =========================================================================
from backend.services.proctoring_service import ProctoringManager, ProctoringConfig

class ProctoringCheckRequest(BaseModel):
    interview_id: int = Field(..., example=1)
    faces_detected: Optional[int] = Field(None, description="Direct face count if pre-computed by client or test harness")
    frame_b64: Optional[str] = Field(None, description="Base64 encoded JPEG/PNG webcam frame for server-side computer vision detection")
    timestamp: Optional[float] = Field(None, description="Client timestamp (epoch seconds)")


class ProctoringCheckResponse(BaseModel):
    interview_id: int
    status: str
    warning_count: int
    faces_detected: int
    additional_faces: int
    message: str
    is_terminated: bool
    remaining_seconds: Optional[float] = None


@app.post("/api/proctoring/check", response_model=ProctoringCheckResponse)
def check_proctoring(req: ProctoringCheckRequest):
    """
    Analyzes live webcam feed or face count to detect additional persons.
    Applies configurable confirmation window (2-3s) before issuing Warning 1 or Final Warning,
    and automatically terminates the interview if another person persists for >= 10s after final warning.
    """
    result = ProctoringManager.process_check(
        interview_id=req.interview_id,
        faces_detected=req.faces_detected,
        frame_base64=req.frame_b64,
        current_time=req.timestamp
    )
    return ProctoringCheckResponse(**result)


@app.get("/api/proctoring/status/{interview_id}")
def get_proctoring_status(interview_id: int):
    """Returns the current proctoring status for an interview session."""
    session = ProctoringManager.get_session(interview_id)
    return {
        "interview_id": interview_id,
        "status": session.status,
        "warning_count": session.warning_count,
        "is_terminated": session.is_terminated,
        "termination_reason": session.termination_reason,
        "last_faces_count": session.last_faces_count
    }


@app.post("/api/proctoring/reset/{interview_id}")
def reset_proctoring(interview_id: int):
    """Resets the in-memory proctoring state for an interview session (useful for test suites)."""
    ProctoringManager.reset_session(interview_id)
    return {"status": "success", "message": f"Proctoring session for interview {interview_id} reset."}


@app.get("/api/proctoring/config")
def get_proctoring_config():
    """Returns the active configurable thresholds for proctoring."""
    cfg = ProctoringConfig()
    return {
        "confirmation_seconds": cfg.confirmation_seconds,
        "final_warning_timeout_seconds": cfg.final_warning_timeout_seconds,
        "allowed_candidate_faces": cfg.allowed_candidate_faces
    }


# =============================================================================
# Adaptive Technical Interview Question & Progression Endpoints
# =============================================================================

from backend.services.adaptive_interview_service import AdaptiveInterviewManager, AdaptiveSession


class InitAdaptiveRequest(BaseModel):
    interview_id: int = Field(..., description="Unique interview session ID")
    candidate_skills: Optional[List[str]] = Field(default_factory=list, description="Skills extracted from CV")
    target_role: Optional[str] = Field("Software Engineer", description="Candidate target role")
    max_questions: Optional[int] = Field(10, description="Configured total questions limit (default 10)")
    experience: Optional[str] = Field(None, description="Candidate years of experience")
    projects: Optional[str] = Field(None, description="Candidate projects summary")


class NextQuestionRequest(BaseModel):
    interview_id: int = Field(..., description="Active interview ID")
    question_id: Optional[int] = Field(None, description="Previous question ID answered")
    answer: str = Field(..., description="Candidate spoken or typed answer text")


class GenerateProfileQuestionsRequest(BaseModel):
    candidate_name: Optional[str] = Field("Candidate", example="Aarav Sharma")
    target_role: Optional[str] = Field("Software Engineer", example="Full Stack Engineer")
    technical_skills: Optional[List[str]] = Field(default_factory=lambda: ["Python", "SQL"], example=["Python", "FastAPI", "React"])
    experience: Optional[str] = Field("2 years", example="3 years")
    projects: Optional[str] = Field(None, example="Built microservices and REST APIs")
    count: Optional[int] = Field(10, example=10)


@app.post("/api/interview/init-adaptive")
def init_adaptive_interview(req: InitAdaptiveRequest):
    """
    Initializes a dynamic adaptive interview session.
    Selects the foundational basic IT question (Easy difficulty) based on candidate's CV and role.
    """
    profile_data = {
        "technical_skills": req.candidate_skills,
        "target_role": req.target_role,
        "experience": req.experience,
        "projects": req.projects
    }
    session = AdaptiveInterviewManager.get_or_create_session(
        interview_id=req.interview_id,
        candidate_skills=req.candidate_skills,
        target_role=req.target_role,
        max_questions=req.max_questions or 10,
        profile_data=profile_data
    )
    return {
        "status": "success",
        "interview_id": req.interview_id,
        "first_question": session.initial_question,
        "state": session.get_state_summary()
    }


@app.post("/api/interview/generate-profile-questions")
def generate_profile_questions_route(req: GenerateProfileQuestionsRequest):
    """
    Generates a full 10-stage customized interview question track personalized to the candidate's CV profile.
    """
    from backend.ai.nlp.profile_question_model import ProfileQuestionGenerator
    profile_data = {
        "candidate_name": req.candidate_name,
        "target_role": req.target_role,
        "technical_skills": req.technical_skills,
        "experience": req.experience,
        "projects": req.projects
    }
    questions = ProfileQuestionGenerator.generate_candidate_questions(
        profile_data=profile_data,
        target_role=req.target_role or "Software Engineer",
        count=req.count or 10
    )
    return {
        "status": "success",
        "total_questions": len(questions),
        "target_role": req.target_role,
        "questions": questions
    }


@app.post("/api/interview/next-question")
def get_next_adaptive_question(req: NextQuestionRequest):
    """
    Evaluates candidate's previous response using NLP (correctness, relevance, completeness, technical accuracy)
    and dynamically selects the next question (or follow-up) based on demonstrated mastery:
    - Excellent / Good (71-100) -> Increases difficulty (Easy -> Medium -> Hard) & asks deeper concept.
    - Average (41-70) -> Maintains difficulty & asks related/follow-up question.
    - Poor (0-40) -> Decreases difficulty & asks foundational question.
    """
    result = AdaptiveInterviewManager.process_next_question(
        interview_id=req.interview_id,
        question_id=req.question_id,
        answer_text=req.answer
    )
    return result


@app.get("/api/interview/state/{interview_id}")
def get_interview_state(interview_id: int):
    """
    Returns current telemetry, difficulty level, and mastery tracking for the active interview.
    """
    session = AdaptiveInterviewManager.get_session(interview_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Adaptive session for interview {interview_id} not found")
    return session.get_state_summary()


@app.post("/api/interview/reset-adaptive/{interview_id}")
def reset_adaptive_interview(interview_id: int):
    """Resets adaptive session state (useful for test runs)."""
    AdaptiveInterviewManager.reset_session(interview_id)
    return {"status": "success", "message": f"Adaptive session {interview_id} reset"}


# =============================================================================
# =============================================================================
# Storage & Supabase Storage Endpoints
# =============================================================================
from fastapi.responses import Response, JSONResponse
from fastapi import Query, Header
from backend.services.storage_service import StorageService
from backend.services.supabase_storage import SupabaseStorageClient
from backend.config import Config


@app.get("/api/storage/file/{object_key:path}")
def fastapi_get_file(object_key: str, token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    """
    Secure file streaming endpoint via FastAPI.
    Validates token and streams from Supabase Storage or local storage cache.
    """
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.models.user import User
        from backend.utils.security import decode_token

        auth_token = token
        if not auth_token and authorization and authorization.startswith("Bearer "):
            auth_token = authorization.split(" ")[1]

        if not auth_token:
            raise HTTPException(status_code=401, detail="Authentication token required.")

        payload = decode_token(auth_token)
        if not payload or not payload.get("user_id"):
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

        user = User.query.get(payload["user_id"])
        if not user or not StorageService.check_authorization(user, object_key):
            raise HTTPException(status_code=403, detail="Access Denied.")

        data_bytes, mime_type, filename = StorageService.get_file_stream_or_bytes(object_key)
        if data_bytes is None:
            raise HTTPException(status_code=404, detail="File not found.")

        headers = {
            "Content-Type": mime_type or "application/octet-stream",
            "Content-Disposition": f'inline; filename="{filename}"'
        }
        return Response(content=data_bytes, headers=headers, media_type=mime_type or "application/octet-stream")


@app.get("/api/storage/presigned-url")
@app.get("/api/storage/signed-url")
def fastapi_signed_url(key: str = Query(..., alias="key"), token: Optional[str] = Query(None), authorization: Optional[str] = Header(None)):
    """Generates signed URL for direct Supabase Storage streaming."""
    from backend.app import app as flask_app
    with flask_app.app_context():
        from backend.models.user import User
        from backend.utils.security import decode_token

        auth_token = token
        if not auth_token and authorization and authorization.startswith("Bearer "):
            auth_token = authorization.split(" ")[1]

        if not auth_token:
            raise HTTPException(status_code=401, detail="Authentication token required.")

        payload = decode_token(auth_token)
        if not payload or not payload.get("user_id"):
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

        user = User.query.get(payload["user_id"])
        if not user or not StorageService.check_authorization(user, key):
            raise HTTPException(status_code=403, detail="Access Denied.")

        if not SupabaseStorageClient.is_configured():
            return {
                "status": "success",
                "storage_provider": "local",
                "url": f"/api/storage/file/{key}",
                "signed_url": f"/api/storage/file/{key}"
            }

        signed_url = SupabaseStorageClient.generate_signed_url(key, expiration=3600)
        return {
            "status": "success",
            "storage_provider": "supabase",
            "object_key": key,
            "signed_url": signed_url,
            "presigned_url": signed_url,
            "expires_in_seconds": 3600
        }


@app.get("/api/health")
def fastapi_health():
    """Health check endpoint."""
    db_uri = str(Config.SQLALCHEMY_DATABASE_URI)
    db_type = "postgresql" if "postgres" in db_uri else ("sqlite" if "sqlite" in db_uri else "mysql")
    return {
        "status": "online",
        "system": "AI-Powered Video Interview Assessment System",
        "framework": "FastAPI + Uvicorn",
        "database": {
            "type": db_type,
            "status": "ready"
        },
        "storage": {
            "supabase_configured": Config.is_supabase_configured(),
            "bucket": Config.SUPABASE_STORAGE_BUCKET if Config.is_supabase_configured() else None
        }
    }



