import os
import io
from flask import Blueprint, request, jsonify, send_file
from backend.models.resume import Resume
from backend.models.user import User
from backend.services.resume_service import process_resume_upload
from backend.ai.resume.screening import screen_resume, ROLE_REQUIREMENTS
from backend.services.storage_service import StorageService
from backend.services.supabase_storage import SupabaseStorageClient
from backend.utils.security import token_required
from backend.config import Config

resume_bp = Blueprint("resume", __name__, url_prefix="/api/resume")


@resume_bp.route("/upload", methods=["POST"])
@token_required
def upload_resume(current_user):
    if "resume" not in request.files:
        return jsonify({"status": "error", "message": "No resume file in request"}), 400

    file_storage = request.files["resume"]
    target_role = request.form.get("target_role", current_user.target_role or "Software Engineer")

    res, err = process_resume_upload(current_user, file_storage, Config.RESUME_UPLOAD_FOLDER, target_role=target_role)
    if err:
        return jsonify({"status": "error", "message": err}), 400

    return jsonify({
        "status": "success",
        "message": "Resume uploaded, parsed, and screened successfully",
        "data": res
    }), 200

@resume_bp.route("/parsed", methods=["GET"])
@token_required
def get_parsed_resume(current_user):
    # Support viewing parsed resume for a specific candidate if admin
    target_user_id = current_user.id
    cand_id_param = request.args.get("candidate_id")
    if cand_id_param and current_user.role in ["admin", "recruiter"]:
        cand_user = User.query.filter(User.candidate_id.ilike(cand_id_param)).first()
        if cand_user:
            target_user_id = cand_user.id

    resume_obj = Resume.query.filter_by(user_id=target_user_id).order_by(Resume.uploaded_at.desc()).first()
    if not resume_obj:
        return jsonify({"status": "error", "message": "No resume uploaded yet"}), 404

    target_role = current_user.target_role or "Software Engineer"
    parsed_data = {
        "technical_skills": resume_obj.get_technical_skills(),
        "soft_skills": resume_obj.get_soft_skills(),
        "education": resume_obj.education,
        "experience": resume_obj.experience,
        "raw_text": resume_obj.raw_text
    }
    screening = screen_resume(parsed_data, target_role=target_role)

    return jsonify({
        "status": "success",
        "resume": resume_obj.to_dict(),
        "screening": screening
    }), 200

@resume_bp.route("/download", methods=["GET"])
@token_required
def download_resume(current_user):
    target_user = current_user
    cand_id_param = request.args.get("candidate_id")
    if cand_id_param and current_user.role in ["admin", "recruiter"]:
        cand_user = User.query.filter(User.candidate_id.ilike(cand_id_param)).first()
        if cand_user:
            target_user = cand_user

    resume_obj = Resume.query.filter_by(user_id=target_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume_obj:
        return jsonify({"status": "error", "message": "Resume record not found"}), 404

    filename = resume_obj.filename or "candidate_resume.pdf"
    
    # 1. If file exists on local disk
    if resume_obj.file_path and os.path.exists(resume_obj.file_path):
        return send_file(
            resume_obj.file_path,
            as_attachment=True,
            download_name=filename
        )

    # 2. Try fetching via StorageService (Supabase Storage or candidate object key)
    cid = target_user.candidate_id or f"CID-{target_user.id}"
    object_key = SupabaseStorageClient.build_object_key(cid, "resume", filename=filename)
    data_bytes, mime_type, _ = StorageService.get_file_stream_or_bytes(object_key)

    if data_bytes is not None:
        return send_file(
            io.BytesIO(data_bytes),
            mimetype=mime_type or "application/pdf",
            as_attachment=True,
            download_name=filename
        )

    return jsonify({"status": "error", "message": "Resume file not found on server or cloud storage."}), 404

@resume_bp.route("/view", methods=["GET"])
@token_required
def view_resume(current_user):
    target_user = current_user
    cand_id_param = request.args.get("candidate_id")
    if cand_id_param and current_user.role in ["admin", "recruiter"]:
        cand_user = User.query.filter(User.candidate_id.ilike(cand_id_param)).first()
        if cand_user:
            target_user = cand_user

    resume_obj = Resume.query.filter_by(user_id=target_user.id).order_by(Resume.uploaded_at.desc()).first()
    if not resume_obj:
        return jsonify({"status": "error", "message": "Resume file not found"}), 404

    filename = resume_obj.filename or "resume.pdf"

    # Determine mimetype
    mimetype = "application/pdf"
    if filename.lower().endswith(".txt"):
        mimetype = "text/plain"
    elif filename.lower().endswith(".docx") or filename.lower().endswith(".doc"):
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    # 1. If file exists on local disk
    if resume_obj.file_path and os.path.exists(resume_obj.file_path):
        return send_file(
            resume_obj.file_path,
            as_attachment=False,
            mimetype=mimetype,
            download_name=filename
        )

    # 2. Try fetching from Supabase Storage / StorageService
    cid = target_user.candidate_id or f"CID-{target_user.id}"
    object_key = SupabaseStorageClient.build_object_key(cid, "resume", filename=filename)
    data_bytes, resolved_mime, _ = StorageService.get_file_stream_or_bytes(object_key)

    if data_bytes is not None:
        return send_file(
            io.BytesIO(data_bytes),
            mimetype=resolved_mime or mimetype,
            as_attachment=False,
            download_name=filename
        )

    return jsonify({"status": "error", "message": "Resume file not found on server or storage."}), 404

@resume_bp.route("/roles", methods=["GET"])
def get_roles():
    return jsonify({
        "status": "success",
        "roles": list(ROLE_REQUIREMENTS.keys()),
        "role_details": ROLE_REQUIREMENTS
    }), 200
