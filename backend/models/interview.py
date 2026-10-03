from datetime import datetime
from backend.services.database import db
from backend.utils.helpers import utc_now

class ProctoringViolation(db.Model):
    __tablename__ = "interview_proctoring_violations"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    timestamp = db.Column(db.DateTime, default=utc_now)
    faces_detected = db.Column(db.Integer, default=2)
    warning_level = db.Column(db.String(50), default="warning_1") # warning_1, final_warning, terminated
    message = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "faces_detected": self.faces_detected,
            "warning_level": self.warning_level,
            "message": self.message
        }

class InterviewResponse(db.Model):
    __tablename__ = "interview_responses"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    video_path = db.Column(db.String(500), nullable=True)
    audio_path = db.Column(db.String(500), nullable=True)
    transcript = db.Column(db.Text, nullable=True)
    relevance_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    sentiment = db.Column(db.String(30), default="Neutral")
    duration_seconds = db.Column(db.Float, default=0.0)
    eye_contact_pct = db.Column(db.Float, default=0.0)
    head_stability_pct = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        v_url = None
        if self.video_path:
            clean_v = self.video_path.replace("\\", "/")
            if clean_v.startswith("/api/"):
                v_url = clean_v
            elif clean_v.startswith("http://") or clean_v.startswith("https://"):
                v_url = clean_v
            elif "uploads/" in clean_v:
                v_url = "/" + clean_v[clean_v.find("uploads/"):]
            elif clean_v.startswith("CID-") and "/" in clean_v:
                v_url = f"/api/storage/file/{clean_v}"
            elif clean_v.startswith("recordings/"):
                v_url = f"/uploads/{clean_v}"
            else:
                import os
                v_url = f"/uploads/recordings/{os.path.basename(clean_v)}"

        if not v_url and self.id:
            v_url = f"/api/interview/response/{self.id}/media"

        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "question_id": self.question_id,
            "question_text": self.question_text,
            "video_path": self.video_path,
            "video_url": v_url,
            "audio_path": self.audio_path,
            "transcript": self.transcript,
            "relevance_score": round(self.relevance_score or 0.0, 1),
            "technical_score": round(self.technical_score or 0.0, 1),
            "sentiment": self.sentiment,
            "duration_seconds": round(self.duration_seconds or 0.0, 1),
            "eye_contact_pct": round(self.eye_contact_pct or 0.0, 1),
            "head_stability_pct": round(self.head_stability_pct or 0.0, 1),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class InterviewMedia(db.Model):
    """
    Direct Database Media Storage for Audio & Video recordings.
    Completely eliminates dependency on local disk storage.
    Binary content is stored in PostgreSQL (BYTEA), SQLite (BLOB), or MySQL (LONGBLOB).
    Linked directly to Candidate ID, Interview ID, and optional Question Response ID.
    """
    __tablename__ = "interview_media"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = db.Column(db.Integer, db.ForeignKey("interview_responses.id", ondelete="CASCADE"), nullable=True, index=True)
    media_type = db.Column(db.String(30), default="video")  # "video", "audio"
    file_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), default="video/webm")
    file_size = db.Column(db.BigInteger, default=0)
    data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "user_id": self.user_id,
            "interview_id": self.interview_id,
            "response_id": self.response_id,
            "media_type": self.media_type,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size or (len(self.data) if self.data else 0),
            "media_url": f"/api/interview/media/{self.id}",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = db.Column(db.String(100), default="Software Engineer")
    status = db.Column(db.String(30), default="in_progress") # in_progress, completed, cancelled, terminated
    overall_score = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    eye_contact_score = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=utc_now)
    completed_at = db.Column(db.DateTime, nullable=True)
    recording_path = db.Column(db.String(500), nullable=True)
    recording_url = db.Column(db.String(500), nullable=True)
    interview_photo = db.Column(db.String(255), nullable=True)
    warning_count = db.Column(db.Integer, default=0)
    detected_faces_count = db.Column(db.Integer, default=1)
    last_face_detection_time = db.Column(db.DateTime, nullable=True)
    termination_reason = db.Column(db.String(255), nullable=True)
    proctoring_status = db.Column(db.String(50), default="clean") # clean, warning_1, final_warning, terminated

    # Relationships
    responses = db.relationship(InterviewResponse, backref="interview", cascade="all, delete-orphan", lazy=True)
    violations = db.relationship(ProctoringViolation, backref="interview", cascade="all, delete-orphan", lazy=True)
    report = db.relationship("Report", backref="interview", uselist=False, cascade="all, delete-orphan")
    media_files = db.relationship(InterviewMedia, backref="interview", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        rec_url = self.recording_url
        if not rec_url and self.recording_path:
            clean_rec = self.recording_path.replace("\\", "/")
            if clean_rec.startswith("/api/"):
                rec_url = clean_rec
            elif clean_rec.startswith("http://") or clean_rec.startswith("https://"):
                rec_url = clean_rec
            elif "uploads/" in clean_rec:
                rec_url = "/" + clean_rec[clean_rec.find("uploads/"):]
            elif clean_rec.startswith("CID-") and "/" in clean_rec:
                rec_url = f"/api/storage/file/{clean_rec}"
            elif clean_rec.startswith("recordings/"):
                rec_url = f"/uploads/{clean_rec}"
            else:
                import os
                rec_url = f"/uploads/recordings/{os.path.basename(clean_rec)}"

        if not rec_url and self.id:
            rec_url = f"/api/interview/{self.id}/media"

        photo_url = None
        if self.interview_photo:
            clean_p = self.interview_photo.replace("\\", "/")
            if clean_p.startswith("http://") or clean_p.startswith("https://"):
                photo_url = clean_p
            elif "uploads/" in clean_p:
                photo_url = "/" + clean_p[clean_p.find("uploads/"):]
            elif clean_p.startswith("CID-") and "/" in clean_p:
                photo_url = f"/api/storage/file/{clean_p}"
            elif clean_p.startswith("profiles/"):
                photo_url = f"/uploads/{clean_p}"
            else:
                photo_url = f"/uploads/{clean_p}" if not clean_p.startswith("/") else clean_p

        return {
            "id": self.id,
            "user_id": self.user_id,
            "target_role": self.target_role,
            "status": self.status,
            "overall_score": round(self.overall_score or 0.0, 1),
            "communication_score": round(self.communication_score or 0.0, 1),
            "technical_score": round(self.technical_score or 0.0, 1),
            "confidence_score": round(self.confidence_score or 0.0, 1),
            "eye_contact_score": round(self.eye_contact_score or 0.0, 1),
            "recording_path": self.recording_path,
            "recording_url": rec_url,
            "interview_photo": self.interview_photo,
            "interview_photo_url": photo_url,
            "warning_count": self.warning_count or 0,
            "detected_faces_count": self.detected_faces_count or 1,
            "last_face_detection_time": self.last_face_detection_time.isoformat() if self.last_face_detection_time else None,
            "termination_reason": self.termination_reason,
            "proctoring_status": self.proctoring_status or "clean",
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "responses_count": len(self.responses) if hasattr(self, 'responses') and self.responses else 0,
            "violations_count": len(self.violations) if hasattr(self, 'violations') and self.violations else 0
        }
