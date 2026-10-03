import os
import subprocess
import uuid
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from backend.config import Config

def utc_now():
    """Returns current UTC datetime without timezone offset for clean naive DB storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def save_uploaded_file(file_storage, target_folder, allowed_extensions):
    if not file_storage or not file_storage.filename:
        return None, "No file uploaded"
        
    ext = file_storage.filename.rsplit(".", 1)[1].lower() if "." in file_storage.filename else ""
    if ext not in allowed_extensions:
        return None, f"Unsupported file format '.{ext}'. Allowed: {', '.join(allowed_extensions)}"
        
    safe_base = secure_filename(file_storage.filename.rsplit(".", 1)[0])
    unique_filename = f"{safe_base}_{uuid.uuid4().hex[:8]}.{ext}"
    os.makedirs(target_folder, exist_ok=True)
    full_path = os.path.join(target_folder, unique_filename)
    file_storage.save(full_path)
    return full_path, None

def convert_media_to_wav(media_path):
    """
    Converts any video or audio file (.webm, .mp4, .ogg) to standard 16kHz mono WAV
    using the bundled static ffmpeg binary from imageio_ffmpeg, which Whisper requires.
    """
    try:
        import imageio_ffmpeg
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_bin = "ffmpeg"
        
    wav_path = media_path.rsplit(".", 1)[0] + "_audio.wav"
    if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
        return wav_path

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", media_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        wav_path
    ]
    
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if os.path.exists(wav_path):
            return wav_path
    except Exception as e:
        print(f"[Helper Warning] FFmpeg conversion failed ({e}). Returning original path.")
        
    return media_path
