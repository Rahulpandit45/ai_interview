import secrets
from datetime import datetime, timezone
from backend.services.database import db
from backend.utils.helpers import utc_now
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.String(50), unique=True, nullable=True, index=True)
    admin_id = db.Column(db.String(50), unique=True, nullable=True, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="candidate")  # "candidate" or "admin"
    institution = db.Column(db.String(120), default="Mid-West University", nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    target_role = db.Column(db.String(100), default="Software Engineer")
    profile_photo = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(120), default="Kathmandu, Nepal", nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    github = db.Column(db.String(255), nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    email_verified = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)


    # Relationships
    resumes = db.relationship("Resume", backref="user", cascade="all, delete-orphan", lazy=True)
    interviews = db.relationship("Interview", backref="user", cascade="all, delete-orphan", lazy=True)
    reports = db.relationship("Report", backref="user", cascade="all, delete-orphan", lazy=True)

    @classmethod
    def generate_candidate_id(cls, year=None):
        """
        Generates a collision-resistant, permanent unique candidate identifier.
        Format: CID-YYYY-XXXXXX (e.g. CID-2026-9E4B2A)
        """
        if not year:
            year = datetime.now(timezone.utc).year
        # High readability characters without ambiguity (no 0/O, 1/I)
        chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
        while True:
            token = "".join(secrets.choice(chars) for _ in range(6))
            cid = f"CID-{year}-{token}"
            if not cls.query.filter_by(candidate_id=cid).first():
                return cid

    @classmethod
    def generate_admin_id(cls, year=None):
        """
        Generates an official institutional Administrator ID.
        Format: ADM-YYYY-XXX (e.g. ADM-2026-001, ADM-2026-002)
        """
        if not year:
            year = datetime.now(timezone.utc).year
        prefix = f"ADM-{year}-"
        admins = cls.query.filter(cls.admin_id.like(f"{prefix}%")).all()
        max_idx = 0
        for a in admins:
            if a.admin_id:
                parts = a.admin_id.split("-")
                if len(parts) == 3 and parts[2].isdigit():
                    max_idx = max(max_idx, int(parts[2]))
        return f"{prefix}{max_idx + 1:03d}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        photo_url = None
        if self.profile_photo:
            clean_path = self.profile_photo.replace("\\", "/")
            if clean_path.startswith("http://") or clean_path.startswith("https://") or clean_path.startswith("data:"):
                photo_url = clean_path
            elif "uploads/" in clean_path:
                photo_url = "/" + clean_path[clean_path.find("uploads/"):]
            elif clean_path.startswith("profiles/"):
                photo_url = f"/uploads/{clean_path}"
            elif clean_path.startswith("CID-") and "/" in clean_path:
                photo_url = f"/api/storage/file/{clean_path}"
            elif not clean_path.startswith("/"):
                photo_url = f"/uploads/{clean_path}"
            else:
                photo_url = clean_path

        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "admin_id": self.admin_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "institution": self.institution,
            "phone": self.phone or "",
            "target_role": self.target_role or "Software Engineer",
            "profile_photo": self.profile_photo,
            "profile_photo_url": photo_url,
            "location": self.location or "Kathmandu, Nepal",
            "linkedin": self.linkedin or "",
            "github": self.github or "",
            "education": self.education or "",
            "experience": self.experience or "",
            "email_verified": bool(self.email_verified),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
