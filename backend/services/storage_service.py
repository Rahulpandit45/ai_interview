"""
storage_service.py - Unified Candidate File Management & PostgreSQL + Supabase Storage Coordinator
Seamlessly coordinates file storage between PostgreSQL file metadata references,
Supabase Storage bucket, and local caching fallback.
"""

import os
import io
import mimetypes
import logging
from typing import Optional, Dict, Any, Tuple, Union
from backend.config import Config
from backend.services.database import db
from backend.models.stored_file import CandidateFile
from backend.services.supabase_storage import SupabaseStorageClient

logger = logging.getLogger("storage_service")


class StorageService:
    """
    Unified Storage Coordinator:
    - Organizes candidate files by Candidate ID:
        {candidate_id}/resume/{candidate_id}.pdf
        {candidate_id}/registration-photo/{candidate_id}.jpg
        {candidate_id}/interview/video/{candidate_id}.mp4
        {candidate_id}/interview/photos/{index:03d}.jpg
        {candidate_id}/report/{candidate_id}-report.pdf
    - Stores file metadata and Supabase object keys in PostgreSQL `candidate_files` table.
    - Uploads actual binary content to Supabase Storage if configured, or saves to local disk as fallback.
    - Provides secure authorization checks and URL resolution.
    """

    @classmethod
    def save_candidate_file(
        cls,
        candidate_id: str,
        file_type: str,
        file_input: Union[str, bytes, io.BytesIO, Any],
        filename: Optional[str] = None,
        user_id: Optional[int] = None,
        interview_id: Optional[int] = None,
        content_type: Optional[str] = None,
        index: Optional[int] = None
    ) -> Tuple[Optional[CandidateFile], Optional[str]]:
        """
        Saves a candidate file to Supabase Storage (and local cache) and records reference in PostgreSQL.

        Args:
            candidate_id: Unique candidate ID (e.g. CID-2026-HDP62N)
            file_type: "resume", "registration_photo", "interview_video", "interview_photo", "report"
            file_input: file path (str), raw bytes, or file-like object
            filename: original filename
            user_id: database user ID
            interview_id: database interview ID if applicable
            content_type: MIME type
            index: snapshot index or question number if applicable

        Returns:
            (CandidateFile instance, error_message or None)
        """
        if not candidate_id:
            return None, "Candidate ID is required for file storage."

        # Generate canonical Supabase object key based on Candidate ID
        object_key = SupabaseStorageClient.build_object_key(
            candidate_id=candidate_id,
            file_type=file_type,
            filename=filename,
            index=index
        )

        # Determine raw bytes and local path
        raw_bytes = None
        local_path = None
        file_size = 0

        if isinstance(file_input, str):
            if os.path.exists(file_input):
                local_path = os.path.abspath(file_input)
                file_size = os.path.getsize(local_path)
                if not filename:
                    filename = os.path.basename(local_path)
            else:
                raw_bytes = file_input.encode("utf-8")
                file_size = len(raw_bytes)
        elif isinstance(file_input, (bytes, bytearray)):
            raw_bytes = bytes(file_input)
            file_size = len(raw_bytes)
        elif hasattr(file_input, "read"):
            # FileStorage or BytesIO
            raw_bytes = file_input.read()
            if hasattr(file_input, "seek"):
                file_input.seek(0)
            file_size = len(raw_bytes)
            if not filename and hasattr(file_input, "filename"):
                filename = file_input.filename
        else:
            return None, "Unsupported file input type."

        if not filename:
            filename = os.path.basename(object_key)

        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        # Determine target local folder for non-media files (audio & video are stored strictly in DB)
        is_media_file = file_type in ["interview_video", "video", "interview_audio", "audio"]
        if not is_media_file:
            if file_type in ["resume", "cv"]:
                target_folder = Config.RESUME_UPLOAD_FOLDER
            elif file_type in ["registration_photo", "registration-photo", "profile_photo", "photo"]:
                target_folder = Config.PROFILE_UPLOAD_FOLDER
            elif file_type in ["report"]:
                target_folder = Config.REPORTS_DIR
            else:
                target_folder = Config.UPLOAD_FOLDER

            os.makedirs(target_folder, exist_ok=True)

            # Save local copy if not already on disk
            if not local_path or not os.path.exists(local_path):
                local_filename = os.path.basename(object_key)
                local_dest = os.path.join(target_folder, local_filename)
                try:
                    if raw_bytes is not None:
                        with open(local_dest, "wb") as f:
                            f.write(raw_bytes)
                        local_path = local_dest
                except Exception as e:
                    logger.warning(f"Could not save local cache file ({e}).")
        else:
            # Audio and Video are stored directly in DB - no local disk copy
            local_path = None
            storage_provider = "database"

        # 1. Upload to Supabase Storage if configured
        storage_provider = "database" if is_media_file else "local"
        public_url = None

        if SupabaseStorageClient.is_configured():
            try:
                if local_path and os.path.exists(local_path):
                    supa_res = SupabaseStorageClient.upload_file(
                        local_path=local_path,
                        object_key=object_key,
                        content_type=content_type,
                        metadata={"candidate_id": candidate_id, "file_type": file_type}
                    )
                elif raw_bytes is not None:
                    supa_res = SupabaseStorageClient.upload_bytes(
                        data_bytes=raw_bytes,
                        object_key=object_key,
                        content_type=content_type,
                        metadata={"candidate_id": candidate_id, "file_type": file_type}
                    )
                else:
                    supa_res = None

                if supa_res:
                    storage_provider = "supabase"
                    public_url = supa_res.get("url")
                    logger.info(f"[Supabase Storage] Uploaded '{object_key}' to bucket '{SupabaseStorageClient.get_bucket_name()}'.")
            except Exception as e:
                logger.error(f"[Supabase Storage Error] Failed to upload to Supabase ({e}). Falling back to database storage.")
                storage_provider = "database" if is_media_file else "local"

        # 2. Record or update reference in PostgreSQL `candidate_files` table
        try:
            # Check if file record for this object_key already exists
            file_rec = CandidateFile.query.filter_by(object_key=object_key).first()
            if not file_rec:
                file_rec = CandidateFile(
                    candidate_id=candidate_id,
                    user_id=user_id,
                    interview_id=interview_id,
                    file_type=file_type,
                    object_key=object_key,
                    file_name=filename,
                    mime_type=content_type,
                    file_size=file_size,
                    storage_provider=storage_provider,
                    local_path=local_path,
                    public_url=public_url
                )
                db.session.add(file_rec)
            else:
                file_rec.user_id = user_id or file_rec.user_id
                file_rec.interview_id = interview_id or file_rec.interview_id
                file_rec.file_size = file_size
                file_rec.storage_provider = storage_provider
                file_rec.local_path = local_path
                file_rec.public_url = public_url
                file_rec.mime_type = content_type

            db.session.commit()
            return file_rec, None
        except Exception as e:
            logger.error(f"[Database Error] Could not register CandidateFile in DB: {e}")
            return None, str(e)

    @classmethod
    def get_file_stream_or_bytes(cls, object_key: str) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
        """
        Retrieves file bytes, MIME type, and download filename.
        Checks local cache first, then fetches from Supabase Storage if necessary.
        """
        file_rec = CandidateFile.query.filter_by(object_key=object_key).first()
        content_type = file_rec.mime_type if file_rec else None
        filename = file_rec.file_name if file_rec else os.path.basename(object_key)

        if not content_type:
            content_type, _ = mimetypes.guess_type(object_key)
            content_type = content_type or "application/octet-stream"

        # 1. Check if available on local filesystem
        if file_rec and file_rec.local_path and os.path.exists(file_rec.local_path):
            try:
                with open(file_rec.local_path, "rb") as f:
                    return f.read(), content_type, filename
            except Exception:
                pass

        # Check in standard upload folders
        for folder in [Config.PROFILE_UPLOAD_FOLDER, Config.RESUME_UPLOAD_FOLDER, Config.RECORDING_UPLOAD_FOLDER, Config.REPORTS_DIR]:
            candidate_path = os.path.join(folder, os.path.basename(object_key))
            if os.path.exists(candidate_path):
                try:
                    with open(candidate_path, "rb") as f:
                        return f.read(), content_type, filename
                except Exception:
                    pass

        # 2. Check Database InterviewMedia table for audio/video media
        try:
            from backend.models.interview import InterviewMedia
            base_fname = os.path.basename(object_key)
            cand_id = object_key.split("/")[0] if "/" in object_key else None
            query = InterviewMedia.query.filter(
                (InterviewMedia.file_name == base_fname) |
                (InterviewMedia.file_name == filename)
            )
            if cand_id:
                query = query.filter_by(candidate_id=cand_id)
            media_rec = query.order_by(InterviewMedia.id.desc()).first()

            if not media_rec and cand_id:
                media_rec = InterviewMedia.query.filter_by(candidate_id=cand_id).order_by(InterviewMedia.id.desc()).first()

            if media_rec and media_rec.data:
                return media_rec.data, media_rec.mime_type or content_type, media_rec.file_name or filename
        except Exception as e:
            logger.debug(f"InterviewMedia retrieval attempt: {e}")

        # 3. Fetch from Supabase Storage
        if SupabaseStorageClient.is_configured():
            data_bytes = SupabaseStorageClient.download_bytes(object_key)
            if data_bytes is not None:
                return data_bytes, content_type, filename

        return None, content_type, filename

    @classmethod
    def get_access_url(cls, object_key: str, expires_in: int = 3600) -> str:
        """
        Generates best access URL: signed Supabase URL if Supabase is configured,
        or internal authenticated proxy URL.
        """
        if SupabaseStorageClient.is_configured():
            signed_url = SupabaseStorageClient.generate_signed_url(object_key, expiration=expires_in)
            if signed_url:
                return signed_url
        return f"/api/storage/file/{object_key}"

    @classmethod
    def get_file_url(
        cls,
        candidate_id: str,
        file_type: str,
        filename: Optional[str] = None,
        index: Optional[int] = None,
        default: Optional[str] = None,
        signed: bool = False
    ) -> Optional[str]:
        """
        Resolves access URL for candidate file by type and Candidate ID.
        """
        if not candidate_id:
            return default

        key = SupabaseStorageClient.build_object_key(candidate_id, file_type, filename=filename, index=index)
        if signed and SupabaseStorageClient.is_configured():
            signed_url = SupabaseStorageClient.generate_signed_url(key, expiration=3600)
            if signed_url:
                return signed_url

        return f"/api/storage/file/{key}"

    @classmethod
    def check_authorization(cls, current_user, object_key: str) -> bool:
        """
        Ensures strict security:
        - Administrators & recruiters have global access.
        - Candidates can access ONLY their own files (matching their Candidate ID).
        """
        if not current_user:
            return False

        if current_user.role in ["admin", "recruiter"]:
            return True

        if not current_user.candidate_id:
            return False

        # Extract Candidate ID prefix from object key (e.g. CID-2026-HDP62N/...)
        parts = object_key.replace("\\", "/").split("/", 1)
        if parts:
            key_cid = parts[0]
            if key_cid.upper() == current_user.candidate_id.upper():
                return True

        # Check DB record
        file_rec = CandidateFile.query.filter_by(object_key=object_key).first()
        if file_rec and file_rec.candidate_id:
            if file_rec.candidate_id.upper() == current_user.candidate_id.upper():
                return True

        return False
