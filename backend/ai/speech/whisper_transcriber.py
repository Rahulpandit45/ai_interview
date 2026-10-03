import os
import sys
import whisper
from backend.utils.helpers import convert_media_to_wav

# Add bundled ffmpeg directory to PATH so whisper's internal ffmpeg calls succeed
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    backend_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bin"))
    for d in [ffmpeg_dir, backend_bin]:
        if os.path.exists(d) and d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f"[Whisper Init Warning] FFmpeg path setup: {e}")

_whisper_model = None

def get_whisper_model(model_size="tiny"):
    global _whisper_model
    if _whisper_model is None:
        try:
            print(f"[Speech] Loading Whisper model '{model_size}'...")
            _whisper_model = whisper.load_model(model_size)
            print("[Speech] Whisper model ready.")
        except Exception as e:
            print(f"[Speech Error] Could not load Whisper model: {e}")
            _whisper_model = None
    return _whisper_model

def transcribe_audio(audio_path, model_size="tiny"):
    """
    Transcribes audio file to text using OpenAI Whisper.
    Returns:
      {
        "text": str,
        "language": str,
        "duration_seconds": float,
        "word_count": int,
        "wpm": float,
        "segments": list
      }
    """
    if not os.path.exists(audio_path):
        return {
            "text": "",
            "language": "en",
            "duration_seconds": 0.0,
            "word_count": 0,
            "wpm": 0.0,
            "segments": [],
            "error": "Audio file not found"
        }
        
    # Convert webm / mp4 to 16kHz wav for optimal whisper ingestion
    wav_path = convert_media_to_wav(audio_path)
    model = get_whisper_model(model_size)
    
    if not model:
        return {
            "text": "Transcription engine offline.",
            "language": "en",
            "duration_seconds": 10.0,
            "word_count": 3,
            "wpm": 18.0,
            "segments": [],
            "error": "Model failed to load"
        }

    try:
        result = model.transcribe(wav_path, fp16=False)
        transcription_text = result.get("text", "").strip()
        words = transcription_text.split()
        word_count = len(words)
        
        # Estimate duration from segments
        duration = 0.0
        segments = result.get("segments", [])
        if segments:
            duration = segments[-1].get("end", 0.0)
            
        wpm = round((word_count / max(0.1, duration / 60.0)), 1) if duration > 0 else 0.0

        return {
            "text": transcription_text,
            "language": result.get("language", "en"),
            "duration_seconds": round(duration, 2),
            "word_count": word_count,
            "wpm": wpm,
            "segments": segments
        }
    except Exception as e:
        print(f"[Whisper Transcription Error] {e}")
        return {
            "text": "",
            "language": "en",
            "duration_seconds": 0.0,
            "word_count": 0,
            "wpm": 0.0,
            "segments": [],
            "error": str(e)
        }
