"""
storage_routes.py - Secure Supabase & PostgreSQL File Access Endpoints
Provides authenticated streaming, signed URL generation, and candidate file management.
"""

import io
from flask import Blueprint, request, jsonify, send_file
from backend.models.user import User
from backend.models.stored_file import CandidateFile
from backend.services.storage_service import StorageService
from backend.services.supabase_storage import SupabaseStorageClient
from backend.utils.security import token_required, decode_token

storage_bp = Blueprint("storage", __name__, url_prefix="/api/storage")


def resolve_user_from_request():
    """Extracts authenticated user from Authorization header or ?token= query parameter."""
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.args.get("token")

    if not token:
        return None

    payload = decode_token(token)
    if not payload or not payload.get("user_id"):
        return None

    return User.query.get(payload["user_id"])


@storage_bp.route("/file/<path:object_key>", methods=["GET"])
def get_file(object_key):
    """
    Secure file retrieval endpoint.
    Verifies user authentication and authorization (Candidate can access only their own files, Admin has global access).
    Streams content directly from Supabase Storage or local cache with proper MIME types.
    """
    user = resolve_user_from_request()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required to access storage files."}), 401

    # Security check: verify access permissions
    if not StorageService.check_authorization(user, object_key):
        return jsonify({"status": "error", "message": "Access Denied: You do not have permission to access this file."}), 403

    data_bytes, mime_type, filename = StorageService.get_file_stream_or_bytes(object_key)
    if data_bytes is None:
        return jsonify({"status": "error", "message": f"File '{object_key}' not found."}), 404

    as_attachment = request.args.get("download", "false").lower() in ["true", "1", "yes"]

    return send_file(
        io.BytesIO(data_bytes),
        mimetype=mime_type or "application/octet-stream",
        as_attachment=as_attachment,
        download_name=filename or "download"
    )


@storage_bp.route("/presigned-url", methods=["GET"])
@storage_bp.route("/signed-url", methods=["GET"])
@token_required
def get_signed_url(current_user):
    """
    Generates a secure, short-lived signed URL for direct streaming from Supabase Storage.
    """
    object_key = request.args.get("key") or request.args.get("object_key")
    if not object_key:
        return jsonify({"status": "error", "message": "Query parameter 'key' is required."}), 400

    if not StorageService.check_authorization(current_user, object_key):
        return jsonify({"status": "error", "message": "Access Denied."}), 403

    if not SupabaseStorageClient.is_configured():
        # Supabase not active; return local proxy URL
        return jsonify({
            "status": "success",
            "storage_provider": "local",
            "url": f"/api/storage/file/{object_key}",
            "signed_url": f"/api/storage/file/{object_key}"
        }), 200

    expires_in = int(request.args.get("expires_in", 3600))
    signed_url = SupabaseStorageClient.generate_signed_url(object_key, expiration=expires_in)

    if not signed_url:
        return jsonify({
            "status": "success",
            "storage_provider": "local",
            "url": f"/api/storage/file/{object_key}",
            "signed_url": f"/api/storage/file/{object_key}"
        }), 200

    return jsonify({
        "status": "success",
        "storage_provider": "supabase",
        "object_key": object_key,
        "signed_url": signed_url,
        "presigned_url": signed_url,
        "expires_in_seconds": expires_in
    }), 200


@storage_bp.route("/candidate/<string:candidate_id>/files", methods=["GET"])
@token_required
def get_candidate_files(current_user, candidate_id):
    """
    Retrieves all file references for a Candidate ID from PostgreSQL.
    """
    is_admin = current_user.role in ["admin", "recruiter"]
    is_owner = current_user.candidate_id and current_user.candidate_id.upper() == candidate_id.upper()

    if not is_admin and not is_owner:
        return jsonify({"status": "error", "message": "Access Denied."}), 403

    files = CandidateFile.query.filter(CandidateFile.candidate_id.ilike(candidate_id)).order_by(CandidateFile.uploaded_at.desc()).all()

    return jsonify({
        "status": "success",
        "candidate_id": candidate_id,
        "total_files": len(files),
        "files": [f.to_dict() for f in files]
    }), 200


@storage_bp.route("/health", methods=["GET"])
def storage_health():
    """
    Diagnostic endpoint reporting Supabase Storage and PostgreSQL connection state.
    """
    from backend.services.database import db
    from sqlalchemy import text

    db_ok = False
    try:
        db.session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return jsonify({
        "status": "online",
        "storage_provider": "supabase",
        "supabase_configured": SupabaseStorageClient.is_configured(),
        "bucket_name": SupabaseStorageClient.get_bucket_name(),
        "database_connected": db_ok
    }), 200
