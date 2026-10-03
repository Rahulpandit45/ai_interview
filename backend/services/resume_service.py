import os
import logging
from backend.services.database import db
from backend.models.resume import Resume
from backend.ai.resume.parser import parse_resume
from backend.ai.resume.screening import screen_resume
from backend.services.storage_service import StorageService

logger = logging.getLogger("resume_service")

def process_resume_upload(user, file_storage, target_folder, target_role="Software Engineer"):
    """
    Saves uploaded resume locally, uploads to Supabase Storage under {candidate_id}/resume/{candidate_id}.pdf,
    registers file metadata in PostgreSQL candidate_files table, parses extracted fields,
    computes screening score, and commits record to database.
    """
    from backend.utils.helpers import save_uploaded_file, utc_now
    from backend.config import Config

    saved_path, err = save_uploaded_file(file_storage, target_folder, Config.ALLOWED_RESUME_EXTENSIONS)
    if err:
        return None, err

    filename = os.path.basename(saved_path)
    cid = user.candidate_id or f"CID-2026-{user.id:04d}"
    
    # Run NLP Resume Parser
    parsed = parse_resume(saved_path)
    
    # Run NLP Resume Screening
    screening = screen_resume(parsed, target_role=target_role)
    screening_score = screening.get("screening_score", 70.0)

    # Check if user already has an existing resume, update or create new
    resume_obj = Resume.query.filter_by(user_id=user.id).first()
    if not resume_obj:
        resume_obj = Resume(user_id=user.id)

    from backend.utils.name_matcher import verify_name_match

    extracted_name = parsed.get("candidate_name") or ""
    is_match, verify_msg = verify_name_match(user.full_name, extracted_name)

    resume_obj.filename = filename
    resume_obj.file_path = saved_path
    resume_obj.raw_text = parsed.get("raw_text")
    resume_obj.candidate_name = extracted_name
    resume_obj.education = parsed.get("education")
    resume_obj.experience = parsed.get("experience")
    resume_obj.set_technical_skills(parsed.get("technical_skills", []))
    resume_obj.set_soft_skills(parsed.get("soft_skills", []))
    resume_obj.screening_score = screening_score
    resume_obj.is_verified = is_match
    resume_obj.verification_status = "verified" if is_match else "rejected"
    resume_obj.verification_message = verify_msg
    resume_obj.verified_at = utc_now() if is_match else None

    db.session.add(resume_obj)
    db.session.commit()

    # Save to Cloudflare R2 and register CandidateFile reference
    try:
        StorageService.save_candidate_file(
            candidate_id=cid,
            file_type="resume",
            file_input=saved_path,
            filename=filename,
            user_id=user.id
        )
    except Exception as e:
        logger.warning(f"R2 storage sync notice for resume: {e}")

    return {
        "resume": resume_obj.to_dict(),
        "screening": screening,
        "verification": {
            "is_verified": is_match,
            "status": resume_obj.verification_status,
            "message": verify_msg,
            "registered_name": user.full_name,
            "extracted_name": extracted_name
        }
    }, None
