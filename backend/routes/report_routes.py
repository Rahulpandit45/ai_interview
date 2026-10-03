from flask import Blueprint, jsonify
from backend.models.report import Report
from backend.services.report_service import get_report_by_interview, get_candidate_reports
from backend.utils.security import token_required

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@report_bp.route("/<int:interview_id>", methods=["GET"])
@token_required
def get_report(current_user, interview_id):
    report_data = get_report_by_interview(interview_id)
    if not report_data:
        return jsonify({"status": "error", "message": "Report not found"}), 404

    # Allow candidate to view their own report or admin
    if report_data["user_id"] != current_user.id and current_user.role not in ["admin", "recruiter"]:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    return jsonify({
        "status": "success",
        "report": report_data
    }), 200

@report_bp.route("/my-reports", methods=["GET"])
@token_required
def get_my_reports(current_user):
    reports = get_candidate_reports(current_user.id)
    return jsonify({
        "status": "success",
        "reports": reports
    }), 200
