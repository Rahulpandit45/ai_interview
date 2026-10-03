"""
supabase_storage.py - Supabase Object Storage Client
Provides secure, high-performance upload, download, signed URL generation,
and canonical Candidate-ID folder structure management for the AI Interview Platform.
"""

import os
import io
import mimetypes
import logging
from typing import Optional, Dict, Any, List, Union
from supabase import create_client, Client
from backend.config import Config

logger = logging.getLogger("supabase_storage")


class SupabaseStorageClient:
    """
    Direct interface to Supabase Storage for candidate files, resumes, photos, videos, and reports.
    """
    _client: Optional[Client] = None
    _verified_buckets: set = set()

    @classmethod
    def is_configured(cls) -> bool:
        """Checks if valid Supabase URL, Service Role Key, and bucket are configured."""
        return Config.is_supabase_configured()

    @classmethod
    def get_bucket_name(cls) -> str:
        """Returns the configured Supabase Storage bucket name."""
        return (Config.SUPABASE_STORAGE_BUCKET or "ai-interview").strip()

    @classmethod
    def get_client(cls) -> Client:
        """Initializes and caches the Supabase client using privileged Service Role credentials."""
        if cls._client is None:
            if not cls.is_configured():
                raise RuntimeError("Supabase Storage is not configured with valid credentials.")

            url = Config.SUPABASE_URL.strip()
            key = Config.SUPABASE_SERVICE_ROLE_KEY.strip()
            cls._client = create_client(url, key)
            logger.info(f"[Supabase Storage] Initialized client for {url}")
        return cls._client

    @classmethod
    def ensure_bucket_exists(cls, bucket_name: Optional[str] = None) -> bool:
        """
        Ensures the target Supabase Storage bucket exists. Creates it as a private bucket if missing.
        """
        if not cls.is_configured():
            return False

        b_name = (bucket_name or cls.get_bucket_name()).strip()
        if b_name in cls._verified_buckets:
            return True

        try:
            client = cls.get_client()
            # Try getting bucket or listing buckets
            try:
                bucket_info = client.storage.get_bucket(b_name)
                if bucket_info:
                    cls._verified_buckets.add(b_name)
                    return True
            except Exception:
                pass

            # If get_bucket failed, check list_buckets or attempt creation
            try:
                buckets = client.storage.list_buckets()
                bucket_names = [b.name if hasattr(b, 'name') else b.get('name') for b in buckets]
                if b_name in bucket_names:
                    cls._verified_buckets.add(b_name)
                    return True
            except Exception:
                pass

            # Create private bucket
            logger.info(f"[Supabase Storage] Creating bucket '{b_name}'...")
            client.storage.create_bucket(b_name, options={"public": False})
            cls._verified_buckets.add(b_name)
            return True
        except Exception as e:
            logger.warning(f"[Supabase Storage] Notice checking/creating bucket '{b_name}': {e}")
            cls._verified_buckets.add(b_name)  # Mark verified to prevent redundant attempts
            return True

    @classmethod
    def build_object_key(
        cls,
        candidate_id: str,
        file_type: str,
        filename: Optional[str] = None,
        ext: Optional[str] = None,
        index: Optional[int] = None
    ) -> str:
        """
        Builds canonical Candidate-ID organized object key adhering to specifications:
        - {candidate_id}/resume/{candidate_id}.pdf
        - {candidate_id}/registration-photo/{candidate_id}.jpg
        - {candidate_id}/interview/video/{candidate_id}.mp4
        - {candidate_id}/interview/photos/001.jpg
        - {candidate_id}/report/{candidate_id}-report.pdf
        """
        cid = (candidate_id or "CID-UNKNOWN").strip().replace(":", "_").replace("/", "_").replace("\\", "_")
        ft = (file_type or "general").lower().strip()

        # Determine file extension
        resolved_ext = ext
        if not resolved_ext and filename:
            if "." in filename:
                resolved_ext = filename.rsplit(".", 1)[-1].lower()
        if not resolved_ext:
            if ft in ["resume", "report"]:
                resolved_ext = "pdf"
            elif ft in ["registration_photo", "registration-photo", "interview_photo", "photos"]:
                resolved_ext = "jpg"
            elif ft in ["interview_video", "video"]:
                resolved_ext = "mp4"
            else:
                resolved_ext = "bin"

        resolved_ext = resolved_ext.lstrip(".")

        if ft in ["resume", "cv"]:
            return f"{cid}/resume/{cid}.{resolved_ext}"
        elif ft in ["registration_photo", "registration-photo", "profile_photo", "photo"]:
            return f"{cid}/registration-photo/{cid}.{resolved_ext}"
        elif ft in ["interview_video", "video"]:
            if index is not None and index > 0:
                return f"{cid}/interview/video/{cid}_q{index}.{resolved_ext}"
            return f"{cid}/interview/video/{cid}.{resolved_ext}"
        elif ft in ["interview_photo", "interview_photos", "photos", "snapshot"]:
            idx_str = f"{index:03d}" if (index is not None and isinstance(index, int)) else "001"
            return f"{cid}/interview/photos/{idx_str}.{resolved_ext}"
        elif ft in ["report", "assessment_report"]:
            return f"{cid}/report/{cid}-report.{resolved_ext}"
        else:
            safe_name = filename or f"file.{resolved_ext}"
            return f"{cid}/{ft}/{safe_name}"

    @classmethod
    def upload_file(
        cls,
        local_path: str,
        object_key: str,
        content_type: Optional[str] = None,
        upsert: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads a local file to Supabase Storage bucket.
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file '{local_path}' does not exist.")

        file_size = os.path.getsize(local_path)
        if not content_type:
            content_type, _ = mimetypes.guess_type(local_path)
            content_type = content_type or "application/octet-stream"

        bucket_name = cls.get_bucket_name()
        cls.ensure_bucket_exists(bucket_name)

        client = cls.get_client()
        storage = client.storage.from_(bucket_name)

        file_options: Dict[str, Any] = {
            "content-type": content_type,
            "upsert": "true" if upsert else "false"
        }
        if metadata:
            file_options["metadata"] = metadata

        with open(local_path, "rb") as f:
            file_bytes = f.read()
            storage.upload(
                path=object_key,
                file=file_bytes,
                file_options=file_options
            )

        public_url = cls.get_public_url(object_key)
        signed_url = cls.generate_signed_url(object_key, expiration=3600)

        return {
            "object_key": object_key,
            "bucket": bucket_name,
            "file_size": file_size,
            "mime_type": content_type,
            "url": signed_url or public_url,
            "public_url": public_url,
            "signed_url": signed_url
        }

    @classmethod
    def upload_bytes(
        cls,
        data_bytes: bytes,
        object_key: str,
        content_type: Optional[str] = None,
        upsert: bool = True,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads in-memory bytes directly to Supabase Storage.
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(object_key)
            content_type = content_type or "application/octet-stream"

        bucket_name = cls.get_bucket_name()
        cls.ensure_bucket_exists(bucket_name)

        client = cls.get_client()
        storage = client.storage.from_(bucket_name)

        file_options: Dict[str, Any] = {
            "content-type": content_type,
            "upsert": "true" if upsert else "false"
        }
        if metadata:
            file_options["metadata"] = metadata

        storage.upload(
            path=object_key,
            file=data_bytes,
            file_options=file_options
        )

        public_url = cls.get_public_url(object_key)
        signed_url = cls.generate_signed_url(object_key, expiration=3600)

        return {
            "object_key": object_key,
            "bucket": bucket_name,
            "file_size": len(data_bytes),
            "mime_type": content_type,
            "url": signed_url or public_url,
            "public_url": public_url,
            "signed_url": signed_url
        }

    @classmethod
    def download_file(cls, object_key: str, destination_path: str) -> bool:
        """Downloads an object from Supabase Storage to local filesystem."""
        try:
            data = cls.download_bytes(object_key)
            if data is None:
                return False
            os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
            with open(destination_path, "wb") as f:
                f.write(data)
            return True
        except Exception as e:
            logger.error(f"Failed to download file '{object_key}' from Supabase: {e}")
            return False

    @classmethod
    def download_bytes(cls, object_key: str) -> Optional[bytes]:
        """Downloads an object from Supabase Storage directly as raw bytes."""
        if not cls.is_configured():
            return None
        try:
            client = cls.get_client()
            storage = client.storage.from_(cls.get_bucket_name())
            res = storage.download(object_key)
            if isinstance(res, bytes):
                return res
            elif hasattr(res, "read"):
                return res.read()
            elif isinstance(res, str):
                return res.encode("utf-8")
            return res
        except Exception as e:
            logger.error(f"Failed to fetch bytes for '{object_key}' from Supabase Storage: {e}")
            return None

    @classmethod
    def generate_signed_url(
        cls,
        object_key: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generates a secure, time-limited signed URL for private object access.
        """
        if not cls.is_configured():
            return None
        try:
            client = cls.get_client()
            storage = client.storage.from_(cls.get_bucket_name())
            res = storage.create_signed_url(object_key, expires_in=expiration)
            if isinstance(res, dict):
                signed = res.get("signedURL") or res.get("signedUrl")
                if signed:
                    return signed
            elif hasattr(res, "signed_url") and res.signed_url:
                return str(res.signed_url)
            elif hasattr(res, "signedURL") and res.signedURL:
                return str(res.signedURL)
            elif isinstance(res, str):
                return res
            return None
        except Exception as e:
            logger.error(f"Failed to generate signed URL for '{object_key}': {e}")
            return None

    # Alias for backward compatibility
    generate_presigned_url = generate_signed_url

    @classmethod
    def get_public_url(cls, object_key: str) -> str:
        """
        Returns the public URL for an object in Supabase Storage.
        """
        if not cls.is_configured():
            return ""
        try:
            client = cls.get_client()
            storage = client.storage.from_(cls.get_bucket_name())
            url = storage.get_public_url(object_key)
            return str(url) if url else ""
        except Exception as e:
            logger.error(f"Failed to resolve public URL for '{object_key}': {e}")
            return ""

    @classmethod
    def delete_file(cls, object_key: str) -> bool:
        """Deletes an object from Supabase Storage."""
        if not cls.is_configured():
            return False
        try:
            client = cls.get_client()
            storage = client.storage.from_(cls.get_bucket_name())
            storage.remove([object_key])
            return True
        except Exception as e:
            logger.error(f"Failed to delete object '{object_key}' from Supabase: {e}")
            return False

    # Alias for compatibility
    delete_object = delete_file

    @classmethod
    def list_files(cls, prefix: str = "") -> List[Dict[str, Any]]:
        """Lists objects within the bucket under the specified folder prefix."""
        if not cls.is_configured():
            return []
        try:
            client = cls.get_client()
            storage = client.storage.from_(cls.get_bucket_name())
            clean_path = prefix.rstrip("/").lstrip("/")
            res = storage.list(clean_path)
            return res if isinstance(res, list) else []
        except Exception as e:
            logger.error(f"Failed to list objects in '{prefix}' from Supabase: {e}")
            return []
