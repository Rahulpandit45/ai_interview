from datetime import datetime
import json
from backend.services.database import db
from backend.utils.helpers import utc_now

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    raw_text = db.Column(db.Text, nullable=True)
    candidate_name = db.Column(db.String(120), nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    technical_skills = db.Column(db.Text, nullable=True)  # JSON encoded list
    soft_skills = db.Column(db.Text, nullable=True)       # JSON encoded list
    screening_score = db.Column(db.Float, default=0.0)
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(50), default="unverified")  # "verified", "rejected", "unverified"
    verification_message = db.Column(db.String(255), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=utc_now)

    def get_technical_skills(self):
        try:
            return json.loads(self.technical_skills) if self.technical_skills else []
        except Exception:
            return []

    def set_technical_skills(self, skills):
        self.technical_skills = json.dumps(skills)

    def get_soft_skills(self):
        try:
            return json.loads(self.soft_skills) if self.soft_skills else []
        except Exception:
            return []

    def set_soft_skills(self, skills):
        self.soft_skills = json.dumps(skills)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "candidate_name": self.candidate_name,
            "education": self.education,
            "experience": self.experience,
            "technical_skills": self.get_technical_skills(),
            "soft_skills": self.get_soft_skills(),
            "screening_score": round(self.screening_score or 0.0, 1),
            "is_verified": bool(self.is_verified),
            "verification_status": self.verification_status or "unverified",
            "verification_message": self.verification_message,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
