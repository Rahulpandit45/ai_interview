"""
photo_storage.py - Secure profile photo processing, validation, and Supabase Storage utility
"""

import os
import io
import time
import base64
import uuid
import logging
from PIL import Image
from werkzeug.utils import secure_filename
from backend.config import Config

logger = logging.getLogger("photo_storage")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
TARGET_DIMENSION = 500  # Max width/height for optimized profile avatars

def allowed_file(filename):
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def process_and_save_photo(photo_input, candidate_id, user_id=None):
    """
    Validates, sanitizes, resizes, and saves a profile photo.
    Uploads to Supabase Storage ({candidate_id}/registration-photo/{candidate_id}.jpg)
    and caches locally in uploads/profiles/.

    Supports:
      - werkzeug.datastructures.FileStorage object
      - base64 data string (data:image/jpeg;base64,...) from webcam snapshot
      - raw bytes

    Returns:
      relative_path (str): e.g. "profiles/CID-2026-X7Y8Z9_1710000000.jpg"
    Raises:
      ValueError: on invalid format, excessive file size, or corrupted image data.
    """
    os.makedirs(Config.PROFILE_UPLOAD_FOLDER, exist_ok=True)
    raw_bytes = None

    # 1. Extract bytes from input
    if hasattr(photo_input, "read"):
        raw_bytes = photo_input.read()
    elif isinstance(photo_input, str):
        data_str = photo_input.strip()
        if data_str.startswith("data:"):
            if "," in data_str:
                _, data_str = data_str.split(",", 1)
        try:
            raw_bytes = base64.b64decode(data_str)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {e}")
    elif isinstance(photo_input, (bytes, bytearray)):
        raw_bytes = bytes(photo_input)
    else:
        raise ValueError("Unsupported photo input type.")

    if not raw_bytes:
        raise ValueError("Empty image data provided.")

    if len(raw_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"Profile photo exceeds maximum limit of {MAX_FILE_SIZE // (1024 * 1024)}MB.")

    # 2. Verify and parse image with Pillow
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        image.verify()  # Verifies file integrity
        image = Image.open(io.BytesIO(raw_bytes))
    except Exception as e:
        raise ValueError(f"Uploaded file is not a valid or readable image: {e}")

    # 3. Normalize image format and mode (crop to square & resize)
    try:
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Center-crop to square
        width, height = image.size
        min_dim = min(width, height)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        image = image.crop((left, top, right, bottom))

        # Resize to standard avatar dimension if larger
        if min_dim > TARGET_DIMENSION:
            image = image.resize((TARGET_DIMENSION, TARGET_DIMENSION), Image.Resampling.LANCZOS)

        # 4. Generate secure filename
        safe_cid = secure_filename(candidate_id.replace(":", "_").replace("/", "_"))
        timestamp = int(time.time())
        random_suffix = uuid.uuid4().hex[:6]
        filename = f"{safe_cid}_{timestamp}_{random_suffix}.jpg"
        full_dest_path = os.path.join(Config.PROFILE_UPLOAD_FOLDER, filename)

        # 5. Save optimized JPEG locally
        image.save(full_dest_path, "JPEG", quality=88, optimize=True)

        # 6. Upload to Cloudflare R2 & register in PostgreSQL candidate_files
        try:
            from backend.services.storage_service import StorageService
            StorageService.save_candidate_file(
                candidate_id=candidate_id,
                file_type="registration_photo",
                file_input=full_dest_path,
                filename=filename,
                user_id=user_id,
                content_type="image/jpeg"
            )
        except Exception as e:
            logger.warning(f"Background R2 storage sync notice: {e}")

        # Return relative path accessible via /uploads/profiles/...
        return f"profiles/{filename}"

    except Exception as e:
        raise ValueError(f"Failed to process and optimize image: {e}")
