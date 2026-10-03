from datetime import datetime
from backend.services.database import db
from backend.utils.helpers import utc_now

class CandidateFile(db.Model):
    """
    CandidateFile Model
    Stores Supabase object storage references and metadata for all candidate files:
      - Resumes / CVs: {candidate_id}/resume/{candidate_id}.pdf
      - Registration Photos: {candidate_id}/registration-photo/{candidate_id}.jpg
      - Interview Videos: {candidate_id}/interview/video/{candidate_id}.mp4
      - Interview Snapshots: {candidate_id}/interview/photos/{index}.jpg
      - Assessment Reports: {candidate_id}/report/{candidate_id}-report.pdf
    """
    __tablename__ = "candidate_files"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id", ondelete="SET NULL"), nullable=True, index=True)
    file_type = db.Column(db.String(50), nullable=False, index=True)  # resume, registration_photo, interview_video, interview_photo, report
    object_key = db.Column(db.String(500), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.BigInteger, default=0)
    storage_provider = db.Column(db.String(20), default="supabase")  # "supabase" or "local"
    local_path = db.Column(db.String(500), nullable=True)
    public_url = db.Column(db.String(500), nullable=True)
    uploaded_at = db.Column(db.DateTime, default=utc_now, index=True)

    # Relationships
    user = db.relationship("User", backref=db.backref("candidate_files", cascade="all, delete-orphan", lazy=True))
    interview = db.relationship("Interview", backref=db.backref("files", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "user_id": self.user_id,
            "interview_id": self.interview_id,
            "file_type": self.file_type,
            "object_key": self.object_key,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "file_size": self.file_size or 0,
            "storage_provider": self.storage_provider or "supabase",
            "local_path": self.local_path,
            "public_url": self.public_url,
            "access_url": f"/api/storage/file/{self.object_key}",
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
