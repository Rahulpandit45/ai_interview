import json
from flask import Blueprint, request, jsonify
from backend.models.interview import Interview
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

@interview_bp.route("/test-transcription", methods=["POST"])
def test_transcription():
    """
    Direct test endpoint for Whisper transcription (Phase 9 requirement).
    """
    if "audio" not in request.files:
        return jsonify({"status": "error", "message": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    saved_path, err = save_uploaded_file(audio_file, Config.RECORDING_UPLOAD_FOLDER, Config.ALLOWED_RECORDING_EXTENSIONS)
    if err:
        return jsonify({"status": "error", "message": err}), 400

    result = transcribe_audio(saved_path, model_size=Config.WHISPER_MODEL_SIZE)
    return jsonify({
        "status": "success",
        "result": result
    }), 200
