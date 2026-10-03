import os
import json
import tempfile
from flask import Blueprint, request, jsonify, Response
from backend.models.interview import Interview, InterviewResponse, InterviewMedia
from backend.services.interview_service import (
    start_interview_session,
    process_question_response,
    finalize_interview_and_generate_report
)
from backend.ai.speech.whisper_transcriber import transcribe_audio
from backend.utils.security import token_required
from backend.utils.helpers import save_uploaded_file
from backend.config import Config

interview_bp = Blueprint("interview", __name__, url_prefix="/api/interview")

@interview_bp.route("/start", methods=["POST"])
@token_required
def start_interview(current_user):
    data = request.get_json() or {}
    target_role = data.get("target_role", current_user.target_role or "Software Engineer")
    
    session_data, err = start_interview_session(current_user, target_role=target_role)
    if err:
        return jsonify({
            "status": "error",
            "message": err,
            "code": "CV_VERIFICATION_FAILED" if "does not match" in err else "NO_CV"
        }), 403

    return jsonify({
        "status": "success",
        "message": "Interview session initiated",
        "data": session_data
    }), 201

@interview_bp.route("/<int:interview_id>/response", methods=["POST"])
@token_required
def submit_response(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    if interview.status == "terminated":
        return jsonify({
            "status": "error",
            "message": f"Interview Terminated: {interview.termination_reason or 'Another person remained present after the final warning.'}"
        }), 403

    question_id = request.form.get("question_id")
    question_text = request.form.get("question_text", "Interview question")
    client_transcript = request.form.get("transcript", "")
    benchmark_answer = request.form.get("benchmark_answer", "")
    
    # Optional client-side live tracking metrics (JSON string)
    metrics_str = request.form.get("metrics", "{}")
    try:
        client_metrics = json.loads(metrics_str)
    except Exception:
        client_metrics = {}

    media_file = request.files.get("recording")
    
    resp_data, err = process_question_response(
        interview_id=interview_id,
        question_id=question_id,
        question_text=question_text,
        media_file=media_file,
        client_transcript=client_transcript,
        client_metrics=client_metrics,
        benchmark_answer=benchmark_answer
    )

    if err:
        return jsonify({"status": "error", "message": err}), 400

    return jsonify({
        "status": "success",
        "message": "Response processed successfully",
        "data": resp_data
    }), 200

@interview_bp.route("/<int:interview_id>/finish", methods=["POST"])
@token_required
def finish_interview(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    if interview.status == "terminated":
        return jsonify({
            "status": "error",
            "message": f"Interview Terminated: {interview.termination_reason or 'Another person remained present after the final warning.'}"
        }), 403

    report_data, err = finalize_interview_and_generate_report(interview_id)
    if err:
        return jsonify({"status": "error", "message": err}), 400

    return jsonify({
        "status": "success",
        "message": "Interview finalized and AI assessment report generated",
        "report": report_data
    }), 200

@interview_bp.route("/<int:interview_id>/proctoring-check", methods=["POST"])
@token_required
def check_interview_proctoring(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    data = request.get_json() or {}
    from backend.services.proctoring_service import ProctoringManager
    result = ProctoringManager.process_check(
        interview_id=interview_id,
        faces_detected=data.get("faces_detected"),
        frame_base64=data.get("frame_b64"),
        current_time=data.get("timestamp")
    )
    return jsonify(result), 200

@interview_bp.route("/<int:interview_id>/next-question", methods=["POST"])
@token_required
def get_next_question_route(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    if interview.status == "terminated":
        return jsonify({
            "status": "error",
            "message": f"Interview Terminated: {interview.termination_reason or 'Another person remained present after the final warning.'}"
        }), 403

    data = request.get_json() or {}
    question_id = data.get("question_id")
    answer = data.get("answer", "")

    from backend.services.adaptive_interview_service import AdaptiveInterviewManager
    result = AdaptiveInterviewManager.process_next_question(
        interview_id=interview_id,
        question_id=question_id,
        answer_text=answer
    )
    return jsonify(result), 200

@interview_bp.route("/<int:interview_id>", methods=["GET"])
@token_required
def get_interview(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    if interview.user_id != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    return jsonify({
        "status": "success",
        "interview": interview.to_dict(),
        "responses": [r.to_dict() for r in interview.responses]
    }), 200

@interview_bp.route("/history", methods=["GET"])
@token_required
def get_user_interviews(current_user):
    interviews = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.started_at.desc()).all()
    return jsonify({
        "status": "success",
        "interviews": [i.to_dict() for i in interviews]
    }), 200

def stream_db_media(data: bytes, mime_type: str = "video/webm", filename: str = "recording.webm"):
    """
    Streams binary media data directly from database storage with RFC 7233 HTTP Range support.
    Enables seeking, scrub bar buffering, and low-latency playback in HTML5 video/audio players.
    """
    if not data:
        return jsonify({"status": "error", "message": "Media content not found in database"}), 404

    total_size = len(data)
    range_header = request.headers.get("Range")

    if not range_header:
        resp = Response(data, status=200, mimetype=mime_type or "video/webm")
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Content-Length"] = str(total_size)
        resp.headers["Content-Disposition"] = f'inline; filename="{filename}"'
        resp.headers["Cache-Control"] = "public, max-age=3600"
        return resp

    try:
        range_val = range_header.strip().replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else total_size - 1

        if start >= total_size or end >= total_size or start > end:
            return Response(status=416, headers={"Content-Range": f"bytes */{total_size}"})

        chunk = data[start:end + 1]
        resp = Response(chunk, status=206, mimetype=mime_type or "video/webm")
        resp.headers["Content-Range"] = f"bytes {start}-{end}/{total_size}"
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Content-Length"] = str(len(chunk))
        resp.headers["Content-Disposition"] = f'inline; filename="{filename}"'
        resp.headers["Cache-Control"] = "public, max-age=3600"
        return resp
    except Exception:
        resp = Response(data, status=200, mimetype=mime_type or "video/webm")
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Content-Length"] = str(total_size)
        return resp

@interview_bp.route("/<int:interview_id>/media", methods=["GET"])
def get_interview_media(interview_id):
    """
    Fetches the primary video/audio recording for an interview directly from database storage.
    Supports Range header requests for continuous HTML5 streaming and instant scrubbing.
    """
    # Look for recorded media linked to this interview
    media_rec = InterviewMedia.query.filter_by(interview_id=interview_id).order_by(InterviewMedia.id.desc()).first()
    if media_rec and media_rec.data:
        return stream_db_media(media_rec.data, media_rec.mime_type, media_rec.file_name)

    # Fallback: check if any response has media
    responses = InterviewResponse.query.filter_by(interview_id=interview_id).order_by(InterviewResponse.id.desc()).all()
    for r in responses:
        resp_media = InterviewMedia.query.filter_by(response_id=r.id).first()
        if resp_media and resp_media.data:
            return stream_db_media(resp_media.data, resp_media.mime_type, resp_media.file_name)

    # Legacy fallback: check CandidateFile
    interview = Interview.query.get_or_404(interview_id)
    cid = interview.user.candidate_id if interview.user else None
    if cid:
        from backend.services.storage_service import StorageService
        cand_key = f"{cid}/interview/video/{cid}.mp4"
        dbytes, mtype, fname = StorageService.get_file_stream_or_bytes(cand_key)
        if dbytes:
            return stream_db_media(dbytes, mtype, fname)

    return jsonify({"status": "error", "message": "No media recording found for this interview in database"}), 404

@interview_bp.route("/media/<int:media_id>", methods=["GET"])
def get_media_by_id(media_id):
    """
    Fetches specific media record directly from the database by its primary key ID.
    """
    media_rec = InterviewMedia.query.get_or_404(media_id)
    return stream_db_media(media_rec.data, media_rec.mime_type, media_rec.file_name)

@interview_bp.route("/response/<int:response_id>/media", methods=["GET"])
def get_response_media(response_id):
    """
    Fetches the media recorded for a specific interview question response directly from the database.
    """
    media_rec = InterviewMedia.query.filter_by(response_id=response_id).first()
    if media_rec and media_rec.data:
        return stream_db_media(media_rec.data, media_rec.mime_type, media_rec.file_name)

    resp = InterviewResponse.query.get_or_404(response_id)
    media_rec = InterviewMedia.query.filter_by(interview_id=resp.interview_id).order_by(InterviewMedia.id.desc()).first()
    if media_rec and media_rec.data:
        return stream_db_media(media_rec.data, media_rec.mime_type, media_rec.file_name)

    return jsonify({"status": "error", "message": "No media found for this response"}), 404

@interview_bp.route("/<int:interview_id>/media-list", methods=["GET"])
def list_interview_media(interview_id):
    """
    Returns metadata list of all media recordings in the database for an interview.
    """
    media_items = InterviewMedia.query.filter_by(interview_id=interview_id).order_by(InterviewMedia.id.asc()).all()
    return jsonify({
        "status": "success",
        "interview_id": interview_id,
        "media": [m.to_dict() for m in media_items]
    }), 200

@interview_bp.route("/test-transcription", methods=["POST"])
def test_transcription():
    """
    Direct test endpoint for Whisper transcription without local persistent file storage.
    """
    if "audio" not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    if not audio_file or not audio_file.filename:
        return jsonify({"status": "error", "message": "Invalid audio file"}), 400

    ext = audio_file.filename.rsplit(".", 1)[-1].lower() if "." in audio_file.filename else "wav"
    raw_bytes = audio_file.read()

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(raw_bytes)
            temp_path = tmp.name

        result = transcribe_audio(temp_path, model_size=Config.WHISPER_MODEL_SIZE)
        return jsonify({
            "status": "success",
            "result": result
        }), 200
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
