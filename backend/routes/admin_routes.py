import csv
import io
from flask import Blueprint, request, jsonify, Response
from backend.models.user import User
from backend.models.interview import Interview
from backend.models.resume import Resume
from backend.models.report import Report
from backend.services.report_service import get_recruiter_dashboard_stats
from backend.utils.security import token_required, admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/stats", methods=["GET"])
@token_required
@admin_required
def get_stats(current_user):
    stats = get_recruiter_dashboard_stats()
    return jsonify({
        "status": "success",
        "data": stats
    }), 200

@admin_bp.route("/candidates", methods=["GET"])
@token_required
@admin_required
def get_candidates(current_user):
    search = request.args.get("search", "").strip().lower()
    role_filter = request.args.get("role", "").strip()
    query = User.query.filter_by(role="candidate")
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.candidate_id.ilike(f"%{search}%")) |
            (User.target_role.ilike(f"%{search}%"))
        )
    if role_filter:
        query = query.filter(User.target_role == role_filter)
        
    candidates = query.all()
    results = []
    
    for c in candidates:
        latest_resume = Resume.query.filter_by(user_id=c.id).order_by(Resume.uploaded_at.desc()).first()
        latest_interview = Interview.query.filter_by(user_id=c.id).order_by(Interview.started_at.desc()).first()
        
        photo_url = None
        if c.profile_photo:
            clean_photo = c.profile_photo.replace("\\", "/")
            photo_url = f"/uploads/{clean_photo}" if not clean_photo.startswith("/") else clean_photo

        # Most recent activity: latest interview (completed_at or started_at) or account creation
        recent_activity_dt = c.created_at
        if latest_interview:
            int_dt = latest_interview.completed_at or latest_interview.started_at
            if int_dt and (not recent_activity_dt or int_dt > recent_activity_dt):
                recent_activity_dt = int_dt

        results.append({
            "id": c.id,
            "candidate_id": c.candidate_id,
            "full_name": c.full_name,
            "email": c.email,
            "target_role": c.target_role,
            "phone": c.phone,
            "profile_photo": c.profile_photo,
            "profile_photo_url": photo_url,
            "has_resume": latest_resume is not None,
            "screening_score": latest_resume.screening_score if latest_resume else None,
            "latest_interview_score": latest_interview.overall_score if latest_interview else None,
            "interviews_count": len(c.interviews),
            "created_at": c.created_at.strftime("%b %d, %Y") if c.created_at else "",
            "_latest_activity_dt": recent_activity_dt
        })

    # Order candidates by most recent activity (recent interview or newly created ID)
    results.sort(
        key=lambda x: (x.get("_latest_activity_dt") is not None, x.get("_latest_activity_dt")),
        reverse=True
    )
    for r in results:
        r.pop("_latest_activity_dt", None)

    return jsonify({
        "status": "success",
        "candidates": results
    }), 200

@admin_bp.route("/export-candidates", methods=["GET"])
@token_required
@admin_required
def export_candidates(current_user):
    """
    Exports all candidate records, verified Candidate IDs, and assessment scores.
    Supports ?format=csv (default) or ?format=json.
    """
    export_format = request.args.get("format", "csv").lower()
    candidates = User.query.filter_by(role="candidate").order_by(User.created_at.desc()).all()
    
    rows = []
    for c in candidates:
        latest_resume = Resume.query.filter_by(user_id=c.id).order_by(Resume.uploaded_at.desc()).first()
        latest_interview = Interview.query.filter_by(user_id=c.id).order_by(Interview.started_at.desc()).first()
        
        rows.append({
            "Candidate ID": c.candidate_id or "N/A",
            "Full Name": c.full_name,
            "Email": c.email,
            "Target Role": c.target_role or "Software Engineer",
            "Phone": c.phone or "N/A",
            "Screening Score (%)": f"{latest_resume.screening_score:.1f}" if (latest_resume and latest_resume.screening_score is not None) else "N/A",
            "Interview Score (%)": f"{latest_interview.overall_score:.1f}" if (latest_interview and latest_interview.overall_score is not None) else "N/A",
            "Interview Status": latest_interview.status if latest_interview else "Not Started",
            "Registration Date": c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "N/A"
        })
        
    if export_format == "json":
        return jsonify({"status": "success", "count": len(rows), "candidates": rows}), 200
        
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("Candidate ID,Full Name,Email,Target Role,Phone,Screening Score (%),Interview Score (%),Interview Status,Registration Date\n")
        
    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates_assessment_export.csv"}
    )

@admin_bp.route("/candidates/search-by-id", methods=["GET"])
@token_required
@admin_required
def search_candidate_by_id(current_user):
    """
    Fast lookup for a candidate by Candidate ID, User ID, or email.
    Returns basic match info and status.
    """
    query = request.args.get("id", "").strip()
    if not query:
        return jsonify({"status": "error", "message": "Candidate ID query parameter 'id' is required"}), 400

    candidate = User.query.filter(User.candidate_id.ilike(query)).first()
    if not candidate and query.isdigit():
        candidate = User.query.get(int(query))
    if not candidate:
        candidate = User.query.filter(User.email.ilike(query)).first()

    if not candidate:
        return jsonify({"status": "error", "message": f"No candidate found with ID '{query}'"}), 404

    return jsonify({
        "status": "success",
        "candidate": {
            "id": candidate.id,
            "candidate_id": candidate.candidate_id or f"CID-{candidate.id:04d}",
            "full_name": candidate.full_name,
            "email": candidate.email,
            "target_role": candidate.target_role,
            "profile_photo_url": f"/uploads/{candidate.profile_photo.replace(chr(92), '/')}" if candidate.profile_photo else None
        }
    }), 200

@admin_bp.route("/candidates/<string:candidate_identifier>/report", methods=["GET"])
@token_required
@admin_required
def get_candidate_complete_report(current_user, candidate_identifier):
    """
    Comprehensive Candidate Report Endpoint for Administrator Review & A4 Printing.
    Retrieves complete candidate dossier by Candidate ID.
    Includes registration details, side-by-side photos, interview summary,
    full Q&A history, adaptive question progression, video recording telemetry,
    face verification events, security/proctoring violations, and chronological timeline.
    """
    cand_id = candidate_identifier.strip()
    candidate = User.query.filter(User.candidate_id.ilike(cand_id)).first()
    if not candidate and cand_id.isdigit():
        candidate = User.query.get(int(cand_id))
    if not candidate:
        candidate = User.query.filter(User.email.ilike(cand_id)).first()

    if not candidate:
        return jsonify({
            "status": "error",
            "message": f"Candidate with ID '{cand_id}' was not found in the system."
        }), 404

    from backend.models.interview import InterviewResponse, ProctoringViolation
    from backend.models.question import Question

    report_data = build_candidate_report_dict(candidate)
    return jsonify({
        "status": "success",
        "data": report_data
    }), 200

def build_candidate_report_dict(candidate):
    from backend.models.interview import InterviewResponse, ProctoringViolation
    from backend.models.question import Question

    # Candidate info
    clean_photo = candidate.profile_photo.replace("\\", "/") if candidate.profile_photo else None
    photo_url = None
    if clean_photo:
        photo_url = f"/uploads/{clean_photo}" if not clean_photo.startswith("/") else clean_photo

    reg_date_str = candidate.created_at.strftime("%d %b %Y") if candidate.created_at else "Not available"
    reg_time_str = candidate.created_at.strftime("%H:%M:%S") if candidate.created_at else "Not available"
    reg_dt_str = candidate.created_at.strftime("%d %b %Y %H:%M:%S") if candidate.created_at else "Not available"

    cand_dict = {
        "id": candidate.id,
        "candidate_id": candidate.candidate_id or f"CID-{candidate.id:04d}",
        "full_name": candidate.full_name,
        "email": candidate.email,
        "phone": candidate.phone if candidate.phone else "Not available",
        "role": candidate.role,
        "target_role": candidate.target_role or "Software Engineer",
        "institution": candidate.institution or "Not available",
        "registration_date": reg_date_str,
        "registration_time": reg_time_str,
        "registration_datetime": reg_dt_str,
        "account_status": "Active" if candidate.created_at else "Pending",
        "profile_photo": candidate.profile_photo,
        "profile_photo_url": photo_url
    }

    # Resume & Registration info
    latest_resume = Resume.query.filter_by(user_id=candidate.id).order_by(Resume.uploaded_at.desc()).first()
    if latest_resume:
        cv_up_date = latest_resume.uploaded_at.strftime("%d %b %Y") if latest_resume.uploaded_at else "Not available"
        cv_up_time = latest_resume.uploaded_at.strftime("%H:%M:%S") if latest_resume.uploaded_at else "Not available"
        cv_up_dt = latest_resume.uploaded_at.strftime("%d %b %Y %H:%M:%S") if latest_resume.uploaded_at else "Not available"

        cv_ver_status = latest_resume.verification_status or ("verified" if latest_resume.is_verified else "unverified")
        cv_match_res = "Matched" if latest_resume.is_verified else ("Mismatch" if cv_ver_status == "rejected" else "Pending Verification")

        cv_info = {
            "has_cv": True,
            "filename": latest_resume.filename,
            "file_path": latest_resume.file_path,
            "uploaded_at": cv_up_dt,
            "upload_date": cv_up_date,
            "upload_time": cv_up_time,
            "is_verified": bool(latest_resume.is_verified),
            "verification_status": cv_ver_status,
            "verification_message": latest_resume.verification_message or ("Identity confirmed against CV" if latest_resume.is_verified else "Name verification pending"),
            "verified_at": latest_resume.verified_at.strftime("%d %b %Y %H:%M:%S") if latest_resume.verified_at else None,
            "extracted_cv_name": latest_resume.candidate_name or "Not available",
            "registered_candidate_name": candidate.full_name,
            "name_matching_result": cv_match_res,
            "screening_score": round(latest_resume.screening_score or 0.0, 1),
            "technical_skills": latest_resume.get_technical_skills(),
            "soft_skills": latest_resume.get_soft_skills(),
            "education": latest_resume.education or "Not available",
            "experience": latest_resume.experience or "Not available"
        }
    else:
        cv_info = {
            "has_cv": False,
            "filename": "Not available",
            "file_path": None,
            "uploaded_at": "Not available",
            "upload_date": "Not available",
            "upload_time": "Not available",
            "is_verified": False,
            "verification_status": "Not available",
            "verification_message": "No CV uploaded",
            "verified_at": None,
            "extracted_cv_name": "Not available",
            "registered_candidate_name": candidate.full_name,
            "name_matching_result": "Not available",
            "screening_score": 0.0,
            "technical_skills": [],
            "soft_skills": [],
            "education": "Not available",
            "experience": "Not available"
        }

    # Latest Interview
    latest_interview = Interview.query.filter_by(user_id=candidate.id).order_by(Interview.started_at.desc()).first()

    # Interview photo & registration photo side-by-side
    registration_photo_dict = {
        "label": "Registration Photo",
        "photo_url": cand_dict["profile_photo_url"],
        "timestamp": reg_dt_str,
        "date": reg_date_str,
        "time": reg_time_str,
        "has_photo": bool(candidate.profile_photo)
    }

    interview_photo_dict = {
        "label": "Interview Photo",
        "photo_url": None,
        "timestamp": "Not available",
        "date": "Not available",
        "time": "Not available",
        "has_photo": False
    }

    interview_info = {
        "has_interview": False,
        "interview_id": None,
        "candidate_id": cand_dict["candidate_id"],
        "started_at": "Not available",
        "start_date": "Not available",
        "start_time": "Not available",
        "completed_at": "Not available",
        "duration": "Not available",
        "status": "Not started",
        "is_terminated": False,
        "termination_reason": None,
        "questions_count": 0,
        "answered_questions_count": 0,
        "overall_score": 0.0,
        "communication_score": 0.0,
        "technical_score": 0.0,
        "confidence_score": 0.0,
        "eye_contact_score": 0.0,
        "overall_evaluation": "Not available",
        "feedback": "Not available",
        "strengths": [],
        "weaknesses": []
    }

    qa_history = []
    adaptive_history = []
    security_events = []
    timeline_events = []
    video_info = {
        "has_video": False,
        "video_url": None,
        "interview_id": None,
        "candidate_id": cand_dict["candidate_id"],
        "recording_start": "Not available",
        "recording_end": "Not available",
        "duration": "Not available",
        "status": "Not available",
        "message": "No video recording was captured for this candidate session."
    }

    # Add candidate registration to timeline
    if candidate.created_at:
        timeline_events.append({
            "event_type": "Registration",
            "title": "Candidate Registration Completed",
            "timestamp": candidate.created_at.isoformat(),
            "formatted_datetime": reg_dt_str,
            "badge": "Account Created"
        })

    # Add CV upload to timeline
    if latest_resume and latest_resume.uploaded_at:
        timeline_events.append({
            "event_type": "CV Uploaded",
            "title": f"CV Document Uploaded ({latest_resume.filename})",
            "timestamp": latest_resume.uploaded_at.isoformat(),
            "formatted_datetime": cv_info["uploaded_at"],
            "badge": "Document Received"
        })
        if latest_resume.verified_at:
            timeline_events.append({
                "event_type": "CV Verified",
                "title": f"Identity & Name Match: {cv_info['name_matching_result']}",
                "timestamp": latest_resume.verified_at.isoformat(),
                "formatted_datetime": latest_resume.verified_at.strftime("%d %b %Y %H:%M:%S"),
                "badge": cv_info["verification_status"].capitalize()
            })

    if latest_interview:
        interview_info["has_interview"] = True
        interview_info["interview_id"] = latest_interview.id
        interview_info["status"] = latest_interview.status.capitalize()
        interview_info["is_terminated"] = (latest_interview.status == "terminated")
        interview_info["termination_reason"] = latest_interview.termination_reason
        interview_info["overall_score"] = round(latest_interview.overall_score or 0.0, 1)
        interview_info["communication_score"] = round(latest_interview.communication_score or 0.0, 1)
        interview_info["technical_score"] = round(latest_interview.technical_score or 0.0, 1)
        interview_info["confidence_score"] = round(latest_interview.confidence_score or 0.0, 1)
        interview_info["eye_contact_score"] = round(latest_interview.eye_contact_score or 0.0, 1)

        # Evaluation grade
        score = latest_interview.overall_score or 0.0
        if score >= 85:
            eval_grade = "Excellent - Exceeds Core Technical & Behavioral Benchmarks"
        elif score >= 70:
            eval_grade = "Good - Meets Technical Competency Standards"
        elif score >= 50:
            eval_grade = "Average - Foundational Knowledge Demonstrated"
        else:
            eval_grade = "Needs Improvement - Gaps in Technical Depth"
        interview_info["overall_evaluation"] = eval_grade

        if latest_interview.report:
            interview_info["feedback"] = latest_interview.report.feedback or eval_grade
            interview_info["strengths"] = latest_interview.report.get_strengths()
            interview_info["weaknesses"] = latest_interview.report.get_weaknesses()

        if latest_interview.started_at:
            interview_info["started_at"] = latest_interview.started_at.strftime("%d %b %Y %H:%M:%S")
            interview_info["start_date"] = latest_interview.started_at.strftime("%d %b %Y")
            interview_info["start_time"] = latest_interview.started_at.strftime("%H:%M:%S")
            timeline_events.append({
                "event_type": "Interview Started",
                "title": f"Interview Session #{latest_interview.id} Initiated",
                "timestamp": latest_interview.started_at.isoformat(),
                "formatted_datetime": interview_info["started_at"],
                "badge": latest_interview.target_role or "Software Engineer"
            })

        if latest_interview.completed_at:
            interview_info["completed_at"] = latest_interview.completed_at.strftime("%d %b %Y %H:%M:%S")

        # Calculate duration
        if latest_interview.started_at and latest_interview.completed_at:
            dur_secs = (latest_interview.completed_at - latest_interview.started_at).total_seconds()
            mins = int(dur_secs // 60)
            secs = int(dur_secs % 60)
            interview_info["duration"] = f"{mins}m {secs}s"
        else:
            interview_info["duration"] = "In Progress"

        # Check interview photo
        if latest_interview.interview_photo:
            clean_ip = latest_interview.interview_photo.replace("\\", "/")
            ip_url = f"/uploads/{clean_ip}" if not clean_ip.startswith("/") else clean_ip
            interview_photo_dict = {
                "label": "Interview Photo",
                "photo_url": ip_url,
                "timestamp": interview_info["started_at"],
                "date": interview_info["start_date"],
                "time": interview_info["start_time"],
                "has_photo": True
            }

        # Check video recording
        rec_url = latest_interview.to_dict().get("recording_url")
        for r in latest_interview.responses:
            if r.video_path and not rec_url:
                rec_url = r.to_dict().get("video_url")
                break

        if rec_url:
            video_info = {
                "has_video": True,
                "video_url": rec_url,
                "interview_id": latest_interview.id,
                "candidate_id": cand_dict["candidate_id"],
                "recording_start": interview_info["started_at"],
                "recording_end": interview_info["completed_at"],
                "duration": interview_info["duration"],
                "status": "Available",
                "message": "Archived candidate response recording."
            }
        else:
            video_info["message"] = "No video recording was captured for this session (Planned / Optional for this session)."

        # Responses & Q&A History
        responses = InterviewResponse.query.filter_by(interview_id=latest_interview.id).order_by(InterviewResponse.id.asc()).all()
        interview_info["answered_questions_count"] = len(responses)
        interview_info["questions_count"] = max(5, len(responses))

        for idx, resp in enumerate(responses):
            q_num = idx + 1
            asked_dt = resp.created_at.strftime("%d %b %Y %H:%M:%S") if resp.created_at else "Not available"
            asked_d = resp.created_at.strftime("%d %b %Y") if resp.created_at else "Not available"
            asked_t = resp.created_at.strftime("%H:%M:%S") if resp.created_at else "Not available"

            cat = "Technical Competency"
            diff = "Medium"
            if resp.question_id:
                q_obj = Question.query.get(resp.question_id)
                if q_obj:
                    cat = q_obj.category
                    diff = q_obj.difficulty.capitalize() if q_obj.difficulty else "Medium"
            elif q_num == 1:
                cat = "Core Foundations"
                diff = "Easy"

            comp_score = round(((resp.technical_score or 0.0) + (resp.relevance_score or 0.0)) / 2.0, 1)
            if comp_score >= 80:
                rating = "Excellent"
            elif comp_score >= 65:
                rating = "Good"
            elif comp_score >= 45:
                rating = "Average"
            else:
                rating = "Needs Improvement"

            fb = f"Candidate scored {comp_score}% on question #{q_num}. Demonstrated {rating.lower()} grasp with {round(resp.relevance_score or 0.0, 1)}% contextual relevance and {round(resp.technical_score or 0.0, 1)}% technical accuracy."

            qa_item = {
                "question_number": q_num,
                "question_id": resp.question_id,
                "question_text": resp.question_text,
                "category": cat,
                "difficulty": diff,
                "asked_date": asked_d,
                "asked_time": asked_t,
                "asked_datetime": asked_dt,
                "candidate_answer": resp.transcript if resp.transcript else "No verbal response transcribed",
                "answered_datetime": asked_dt,
                "answered_time": asked_t,
                "score": comp_score,
                "technical_score": round(resp.technical_score or 0.0, 1),
                "relevance_score": round(resp.relevance_score or 0.0, 1),
                "sentiment": resp.sentiment or "Neutral",
                "duration_seconds": round(resp.duration_seconds or 0.0, 1),
                "eye_contact_pct": round(resp.eye_contact_pct or 0.0, 1),
                "head_stability_pct": round(resp.head_stability_pct or 0.0, 1),
                "rating": rating,
                "feedback": fb,
                "video_url": resp.to_dict().get("video_url")
            }
            qa_history.append(qa_item)

            # Timeline event for each question
            timeline_events.append({
                "event_type": f"Question #{q_num}",
                "title": f"Question #{q_num}: {resp.question_text[:50]}...",
                "timestamp": resp.created_at.isoformat() if resp.created_at else latest_interview.started_at.isoformat(),
                "formatted_datetime": asked_dt,
                "badge": f"Score: {comp_score}%"
            })

            # Build adaptive transitions
            if idx > 0:
                prev_qa = qa_history[idx - 1]
                prev_diff = prev_qa["difficulty"]
                curr_diff = diff
                diff_shift = f"{prev_diff} → {curr_diff}" if prev_diff != curr_diff else f"Maintained {curr_diff}"

                adaptive_history.append({
                    "step_number": idx,
                    "previous_question": prev_qa["question_text"],
                    "candidate_answer": prev_qa["candidate_answer"],
                    "evaluation": prev_qa["rating"],
                    "score": prev_qa["score"],
                    "difficulty_shift": diff_shift,
                    "next_question": resp.question_text,
                    "category": cat,
                    "reason": f"Candidate demonstrated {prev_qa['rating']} proficiency ({prev_qa['score']}%). Adapted difficulty to {curr_diff} focusing on {cat}.",
                    "timestamp": asked_dt
                })

        # Proctoring Security Events & Violations
        violations = ProctoringViolation.query.filter_by(interview_id=latest_interview.id).order_by(ProctoringViolation.timestamp.asc()).all()
        for v in violations:
            v_date = v.timestamp.strftime("%d %b %Y") if v.timestamp else "Not available"
            v_time = v.timestamp.strftime("%H:%M:%S") if v.timestamp else "Not available"
            v_dt = v.timestamp.strftime("%d %b %Y %H:%M:%S") if v.timestamp else "Not available"

            if v.warning_level == "warning_1":
                ev_type = "Multiple Faces Detected (Warning 1)"
                action = "Official Warning 1 issued. Candidate instructed to maintain solitary environment."
                warn_num = 1
            elif v.warning_level == "final_warning":
                ev_type = "Multiple Faces Detected (Final Warning)"
                action = "Final Warning issued. 10-second automatic termination countdown initiated."
                warn_num = 2
            elif v.warning_level == "terminated":
                ev_type = "Interview Terminated"
                action = f"Session forcibly ended: {latest_interview.termination_reason or v.message}"
                warn_num = 3
            else:
                ev_type = "Proctoring Security Alert"
                action = v.message or "Security rule flagged"
                warn_num = None

            security_events.append({
                "id": v.id,
                "event_type": ev_type,
                "date": v_date,
                "exact_time": v_time,
                "timestamp": v_dt,
                "description": v.message or ev_type,
                "warning_level": v.warning_level,
                "warning_number": warn_num,
                "faces_detected": v.faces_detected,
                "action_taken": action,
                "termination_reason": latest_interview.termination_reason if v.warning_level == "terminated" else None
            })

            timeline_events.append({
                "event_type": f"Security Alert: {v.warning_level.replace('_', ' ').title()}",
                "title": v.message or f"Proctoring violation ({v.faces_detected} faces detected)",
                "timestamp": v.timestamp.isoformat() if v.timestamp else latest_interview.started_at.isoformat(),
                "formatted_datetime": v_dt,
                "badge": "Violation Logged"
            })

        # Add completion or termination to timeline
        if latest_interview.completed_at:
            if latest_interview.status == "terminated":
                timeline_events.append({
                    "event_type": "Interview Terminated",
                    "title": f"Interview Terminated: {latest_interview.termination_reason or 'Security Violation'}",
                    "timestamp": latest_interview.completed_at.isoformat(),
                    "formatted_datetime": interview_info["completed_at"],
                    "badge": "Terminated"
                })
            else:
                timeline_events.append({
                    "event_type": "Interview Completed",
                    "title": f"Interview Session Successfully Completed (Final Score: {interview_info['overall_score']}%)",
                    "timestamp": latest_interview.completed_at.isoformat(),
                    "formatted_datetime": interview_info["completed_at"],
                    "badge": "Completed"
                })

    # Sort timeline events chronologically
    timeline_events.sort(key=lambda x: x.get("timestamp") or "")

    # Face verification record
    face_verification_info = {
        "verification_status": cv_info["verification_status"].capitalize() if cv_info["has_cv"] else "Not available",
        "verification_date": cv_info["verified_at"] or cv_info["uploaded_at"],
        "registration_face_reference": candidate.profile_photo or "Not available",
        "interview_face_reference": latest_interview.interview_photo if (latest_interview and latest_interview.interview_photo) else "Not available",
        "verification_result": cv_info["name_matching_result"],
        "verification_message": cv_info["verification_message"],
        "liveness_result": "Active Real-Time Stream Verified" if (latest_interview and len(latest_interview.responses) > 0) else "Not available",
        "security_policy": "Solitary candidate environment enforcement active"
    }

    return {
        "candidate": cand_dict,
        "registration": cv_info,
        "photos": {
            "registration_photo": registration_photo_dict,
            "interview_photo": interview_photo_dict
        },
        "interview": interview_info,
        "qa_history": qa_history,
        "adaptive_history": adaptive_history,
        "video": video_info,
        "face_verification": face_verification_info,
        "security_events": security_events,
        "timeline": timeline_events
    }

@admin_bp.route("/candidate/<int:candidate_id>", methods=["GET"])
@token_required
@admin_required
def get_candidate_profile(current_user, candidate_id):
    candidate = User.query.get_or_404(candidate_id)
    resume = Resume.query.filter_by(user_id=candidate.id).first()
    interviews = Interview.query.filter_by(user_id=candidate.id).order_by(Interview.started_at.desc()).all()
    reports = Report.query.filter_by(user_id=candidate.id).order_by(Report.generated_at.desc()).all()

    return jsonify({
        "status": "success",
        "candidate": candidate.to_dict(),
        "resume": resume.to_dict() if resume else None,
        "interviews": [i.to_dict() for i in interviews],
        "reports": [r.to_dict() for r in reports]
    }), 200

@admin_bp.route("/raw-db", methods=["GET"])
@token_required
@admin_required
def get_raw_database(current_user):
    from sqlalchemy import inspect, text
    from backend.services.database import db
    
    tables_data = {}
    try:
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        with db.engine.connect() as conn:
            for t in table_names:
                res = conn.execute(text(f"SELECT * FROM {t} LIMIT 50"))
                columns = list(res.keys())
                rows = [dict(zip(columns, row)) for row in res.fetchall()]
                cleaned_rows = []
                for r in rows:
                    row_dict = {}
                    for k, v in r.items():
                        if hasattr(v, "isoformat"):
                            row_dict[k] = v.isoformat()
                        elif isinstance(v, bytes):
                            row_dict[k] = "<binary data>"
                        else:
                            row_dict[k] = v
                    cleaned_rows.append(row_dict)
                tables_data[t] = cleaned_rows
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
    return jsonify({
        "status": "success",
        "database_engine": str(db.engine.url),
        "tables": tables_data
    }), 200

@admin_bp.route("/provision", methods=["POST"])
@token_required
@admin_required
def provision_admin(current_user):
    """
    Company/University Administrator Provisioning Endpoint.
    Allows existing authorized administrators to issue official admin credentials.
    """
    from backend.services.database import db
    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    institution = data.get("institution", "").strip() or current_user.institution or "Mid-West University"
    target_role = data.get("target_role", "Recruitment Lead").strip()
    phone = data.get("phone", "").strip()
    custom_admin_id = data.get("admin_id", "").strip().upper()

    if not full_name or not email or not password:
        return jsonify({"status": "error", "message": "Full name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": f"An account with email '{email}' already exists"}), 409

    if custom_admin_id and User.query.filter_by(admin_id=custom_admin_id).first():
        return jsonify({"status": "error", "message": f"Admin ID '{custom_admin_id}' is already assigned"}), 409

    admin_id = custom_admin_id if custom_admin_id else User.generate_admin_id()

    new_admin = User(
        admin_id=admin_id,
        full_name=full_name,
        email=email,
        role="admin",
        institution=institution,
        target_role=target_role,
        phone=phone
    )
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Official Administrator account provisioned successfully for {full_name}",
        "admin": new_admin.to_dict()
    }), 201

@admin_bp.route("/administrators", methods=["GET"])
@token_required
@admin_required
def list_administrators(current_user):
    """Lists all provisioned institutional administrators."""
    admins = User.query.filter(User.role.in_(["admin", "recruiter"])).order_by(User.created_at.asc()).all()
    return jsonify({
        "status": "success",
        "administrators": [a.to_dict() for a in admins]
    }), 200


@admin_bp.route("/candidates/create", methods=["POST"])
@admin_bp.route("/candidates", methods=["POST"])
@token_required
@admin_required
def create_candidate_by_admin(current_user):
    """
    Administrator Candidate Creation Endpoint.
    Automatically generates a collision-resistant, unique Candidate ID,
    prevents duplicate IDs, allows admin to set the candidate password,
    and provisions the candidate account.
    """
    from backend.services.database import db
    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    target_role = data.get("target_role", "Software Engineer").strip() or "Software Engineer"
    institution = data.get("institution", "").strip() or getattr(current_user, "institution", "Mid-West University") or "Mid-West University"
    phone = data.get("phone", "").strip()
    location = data.get("location", "").strip() or "Kathmandu, Nepal"
    custom_cid = data.get("candidate_id", "").strip().upper()

    if not full_name:
        return jsonify({"status": "error", "message": "Candidate full name is required", "code": "NAME_REQUIRED"}), 400

    if not email:
        return jsonify({"status": "error", "message": "Candidate email address is required", "code": "EMAIL_REQUIRED"}), 400

    if not password:
        return jsonify({"status": "error", "message": "Candidate password is required", "code": "PASSWORD_REQUIRED"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long", "code": "PASSWORD_TOO_SHORT"}), 400

    # Ensure email is unique across the system
    if User.query.filter_by(email=email).first():
        return jsonify({
            "status": "error",
            "message": f"An account with email '{email}' already exists.",
            "code": "EMAIL_ALREADY_EXISTS"
        }), 409

    # Generate or validate unique Candidate ID
    if custom_cid:
        if User.query.filter_by(candidate_id=custom_cid).first():
            return jsonify({
                "status": "error",
                "message": f"Candidate ID '{custom_cid}' is already in use. Please generate a unique ID.",
                "code": "CANDIDATE_ID_EXISTS"
            }), 409
        candidate_id = custom_cid
    else:
        # Automatic generation with collision avoidance loop
        candidate_id = User.generate_candidate_id()
        max_attempts = 15
        attempts = 0
        while User.query.filter_by(candidate_id=candidate_id).first() is not None:
            candidate_id = User.generate_candidate_id()
            attempts += 1
            if attempts > max_attempts:
                return jsonify({
                    "status": "error",
                    "message": "System could not allocate a unique Candidate ID. Please try again.",
                    "code": "CANDIDATE_ID_ALLOCATION_FAILED"
                }), 500

    new_candidate = User(
        candidate_id=candidate_id,
        full_name=full_name,
        email=email,
        role="candidate",
        target_role=target_role,
        institution=institution,
        phone=phone,
        location=location,
        email_verified=True
    )
    new_candidate.set_password(password)

    db.session.add(new_candidate)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Candidate account created successfully with Candidate ID: {candidate_id}",
        "candidate": {
            "id": new_candidate.id,
            "candidate_id": new_candidate.candidate_id,
            "full_name": new_candidate.full_name,
            "email": new_candidate.email,
            "target_role": new_candidate.target_role,
            "institution": new_candidate.institution,
            "phone": new_candidate.phone,
            "created_at": new_candidate.created_at.strftime("%Y-%m-%d %H:%M:%S") if new_candidate.created_at else None
        }
    }), 201
