import json
from datetime import datetime
from backend.services.database import db
from backend.utils.helpers import utc_now

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    candidate_name = db.Column(db.String(120), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    communication_score = db.Column(db.Float, nullable=False)
    technical_score = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    eye_contact_pct = db.Column(db.Float, nullable=False)
    head_movement_score = db.Column(db.Float, default=80.0)
    facial_engagement_score = db.Column(db.Float, default=82.0)
    speech_fluency_wpm = db.Column(db.Float, default=120.0)
    resume_score = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.Text, nullable=True) # JSON list
    weaknesses = db.Column(db.Text, nullable=True) # JSON list
    feedback = db.Column(db.Text, nullable=True)
    detailed_metrics = db.Column(db.Text, nullable=True) # JSON dictionary
    recording_path = db.Column(db.String(500), nullable=True)
    recording_url = db.Column(db.String(500), nullable=True)
    generated_at = db.Column(db.DateTime, default=utc_now)

    def get_strengths(self):
        try:
            return json.loads(self.strengths) if self.strengths else []
        except Exception:
            return []

    def set_strengths(self, items):
        self.strengths = json.dumps(items)

    def get_weaknesses(self):
        try:
            return json.loads(self.weaknesses) if self.weaknesses else []
        except Exception:
            return []

    def set_weaknesses(self, items):
        self.weaknesses = json.dumps(items)

    def get_detailed_metrics(self):
        try:
            return json.loads(self.detailed_metrics) if self.detailed_metrics else {}
        except Exception:
            return {}

    def set_detailed_metrics(self, metrics):
        self.detailed_metrics = json.dumps(metrics)

    def to_dict(self):
        rec_url = self.recording_url
        if not rec_url and self.recording_path:
            clean_rec = self.recording_path.replace("\\", "/")
            if clean_rec.startswith("http://") or clean_rec.startswith("https://"):
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

        photo_url = None
        if self.user and self.user.profile_photo:
            clean_photo = self.user.profile_photo.replace("\\", "/")
            if clean_photo.startswith("http://") or clean_photo.startswith("https://") or clean_photo.startswith("data:"):
                photo_url = clean_photo
            elif "uploads/" in clean_photo:
                photo_url = "/" + clean_photo[clean_photo.find("uploads/"):]
            elif clean_photo.startswith("CID-") and "/" in clean_photo:
                photo_url = f"/api/storage/file/{clean_photo}"
            elif clean_photo.startswith("profiles/"):
                photo_url = f"/uploads/{clean_photo}"
            else:
                photo_url = f"/uploads/{clean_photo}" if not clean_photo.startswith("/") else clean_photo

        responses_list = []
        if self.interview and self.interview.responses:
            responses_list = [r.to_dict() for r in self.interview.responses]

        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "user_id": self.user_id,
            "candidate_id": self.user.candidate_id if self.user else None,
            "profile_photo": self.user.profile_photo if self.user else None,
            "profile_photo_url": photo_url,
            "candidate_name": self.candidate_name,
            "target_role": self.target_role,
            "recording_path": self.recording_path,
            "recording_url": rec_url,
            "responses": responses_list,
            "overall_score": round(self.overall_score, 1),
            "communication_score": round(self.communication_score, 1),
            "technical_score": round(self.technical_score, 1),
            "confidence_score": round(self.confidence_score, 1),
            "eye_contact_pct": round(self.eye_contact_pct, 1),
            "head_movement_score": round(self.head_movement_score, 1),
            "facial_engagement_score": round(self.facial_engagement_score, 1),
            "speech_fluency_wpm": round(self.speech_fluency_wpm, 1),
            "resume_score": round(self.resume_score, 1),
            "strengths": self.get_strengths(),
            "weaknesses": self.get_weaknesses(),
            "feedback": self.feedback,
            "detailed_metrics": self.get_detailed_metrics(),
            "generated_at": self.generated_at.strftime("%B %d, %Y %H:%M") if self.generated_at else None
        }
