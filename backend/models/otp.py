from datetime import datetime
from backend.services.database import db
from backend.utils.helpers import utc_now
from werkzeug.security import generate_password_hash, check_password_hash

class EmailOTP(db.Model):
    __tablename__ = "email_otps"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_sent_at = db.Column(db.DateTime, default=utc_now)
    attempts = db.Column(db.Integer, default=0)
    is_used = db.Column(db.Boolean, default=False)
    purpose = db.Column(db.String(50), default="candidate_registration")

    def set_otp(self, plain_otp: str):
        """Hashes the 6-digit OTP code before storing. Never stores plaintext."""
        self.otp_hash = generate_password_hash(plain_otp)

    def verify_otp(self, plain_otp: str) -> bool:
        """Verifies candidate-submitted 6-digit OTP against the stored cryptographic hash."""
        return check_password_hash(self.otp_hash, plain_otp)

    def is_expired(self) -> bool:
        """Checks whether the OTP has exceeded its 5-minute validity window."""
        return utc_now() > self.expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "attempts": self.attempts,
            "is_used": self.is_used,
            "purpose": self.purpose
        }
