from backend.models.report import Report
from backend.models.interview import Interview
from backend.models.user import User

def get_report_by_interview(interview_id):
    report = Report.query.filter_by(interview_id=interview_id).first()
    return report.to_dict() if report else None

def get_candidate_reports(user_id):
    reports = Report.query.filter_by(user_id=user_id).order_by(Report.generated_at.desc()).all()
    return [r.to_dict() for r in reports]

def get_recruiter_dashboard_stats():
    total_candidates = User.query.filter_by(role="candidate").count()
    total_interviews = Interview.query.count()
    completed_interviews = Interview.query.filter_by(status="completed").count()
    
    all_reports = Report.query.all()
    avg_score = round(sum(r.overall_score for r in all_reports) / len(all_reports), 1) if all_reports else 0.0
    avg_comm = round(sum(r.communication_score for r in all_reports) / len(all_reports), 1) if all_reports else 0.0
    avg_tech = round(sum(r.technical_score for r in all_reports) / len(all_reports), 1) if all_reports else 0.0

    # Top ranking candidates
    ranked_reports = Report.query.order_by(Report.overall_score.desc()).limit(15).all()
    rankings = []
    for rank, r in enumerate(ranked_reports, 1):
        photo_url = None
        if r.user and r.user.profile_photo:
            clean_photo = r.user.profile_photo.replace("\\", "/")
            photo_url = f"/uploads/{clean_photo}" if not clean_photo.startswith("/") else clean_photo

        rankings.append({
            "rank": rank,
            "report_id": r.id,
            "interview_id": r.interview_id,
            "candidate_id": r.user.candidate_id if r.user else None,
            "candidate_name": r.candidate_name,
            "profile_photo": r.user.profile_photo if r.user else None,
            "profile_photo_url": photo_url,
            "target_role": r.target_role,
            "overall_score": r.overall_score,
            "communication_score": r.communication_score,
            "technical_score": r.technical_score,
            "confidence_score": r.confidence_score,
            "eye_contact_pct": r.eye_contact_pct,
            "date": r.generated_at.strftime("%b %d, %Y") if r.generated_at else ""
        })

    return {
        "total_candidates": total_candidates,
        "total_interviews": total_interviews,
        "completed_interviews": completed_interviews,
        "average_score": avg_score,
        "average_communication": avg_comm,
        "average_technical": avg_tech,
        "candidate_rankings": rankings
    }
