import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from backend.models.user import User
from backend.utils.helpers import utc_now

def generate_token(user_id, role="candidate", expires_in_hours=24):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": utc_now() + timedelta(hours=expires_in_hours),
        "iat": utc_now()
    }
    secret = current_app.config.get("SECRET_KEY", "secret_fallback")
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_token(token):
    secret = current_app.config.get("SECRET_KEY", "secret_fallback")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif request.cookies.get("token"):
            token = request.cookies.get("token")
        
        if not token:
            return jsonify({"status": "error", "message": "Authentication token missing"}), 401
            
        data = decode_token(token)
        if not data:
            return jsonify({"status": "error", "message": "Token has expired or is invalid"}), 401
            
        current_user = User.query.get(data["user_id"])
        if not current_user:
            return jsonify({"status": "error", "message": "User not found"}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != "admin" and current_user.role != "recruiter":
            return jsonify({"status": "error", "message": "Admin/Recruiter privileges required"}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def generate_verification_token(email: str, purpose: str = "email_verified", expires_in_minutes: int = 15):
    """
    Generates a cryptographically signed JWT token confirming email verification.
    Used to secure candidate registration against direct API bypass.
    """
    from backend.config import Config
    secret = "ai_interview_assessment_super_secret_key_2026"
    try:
        if current_app:
            secret = current_app.config.get("SECRET_KEY", secret)
    except Exception:
        secret = getattr(Config, "SECRET_KEY", secret)

    payload = {
        "email": email.strip().lower(),
        "purpose": purpose,
        "exp": utc_now() + timedelta(minutes=expires_in_minutes),
        "iat": utc_now()
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def decode_verification_token(token: str):
    """Decodes and validates a verification JWT token."""
    from backend.config import Config
    secret = "ai_interview_assessment_super_secret_key_2026"
    try:
        if current_app:
            secret = current_app.config.get("SECRET_KEY", secret)
    except Exception:
        secret = getattr(Config, "SECRET_KEY", secret)

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except Exception:
        return None

def verify_email_token(token: str, expected_email: str = None) -> bool:
    """
    Validates that a verification token is authentic, unexpired,
    has purpose='email_verified', and matches the candidate email.
    """
    if not token:
        return False
    data = decode_verification_token(token)
    if not data:
        return False
    if data.get("purpose") != "email_verified":
        return False
    if expected_email:
        if data.get("email", "").strip().lower() != expected_email.strip().lower():
            return False
    return True

def generate_email_verification_link(email: str, base_url: str = None, expires_in_minutes: int = 15):
    """
    Generates a secure verification link for candidate email confirmation.
    Returns (token, full_verification_url).
    """
    from backend.config import Config
    clean_email = email.strip().lower()
    token = generate_verification_token(
        email=clean_email,
        purpose="verify_email_link",
        expires_in_minutes=expires_in_minutes
    )
    domain = (base_url or getattr(Config, "APP_BASE_URL", "http://localhost:5000")).rstrip("/")
    verification_url = f"{domain}/verify-email.html?token={token}"
    return token, verification_url

def verify_email_link_token(token: str) -> dict:
    """
    Validates a verification link token from candidate's email.
    Returns the decoded token payload dict if valid, or None if invalid/expired.
    """
    if not token:
        return None
    data = decode_verification_token(token)
    if not data:
        return None
    if data.get("purpose") != "verify_email_link":
        return None
    return data

def generate_password_reset_token(user, expires_in_minutes: int = 20) -> str:
    """
    Generates a cryptographically signed password reset token.
    Embeds user id, email, and password hash fingerprint to ensure single-use
    (resetting the password immediately invalidates any prior tokens).
    """
    from backend.config import Config
    secret = "ai_interview_assessment_super_secret_key_2026"
    try:
        if current_app:
            secret = current_app.config.get("SECRET_KEY", secret)
    except Exception:
        secret = getattr(Config, "SECRET_KEY", secret)

    fp = (user.password_hash or "")[-12:]
    payload = {
        "user_id": user.id,
        "email": user.email.strip().lower(),
        "fp": fp,
        "purpose": "password_reset",
        "exp": utc_now() + timedelta(minutes=expires_in_minutes),
        "iat": utc_now()
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def verify_password_reset_token(token: str):
    """
    Validates password reset token.
    Returns (user, None) on success, or (None, error_message) on failure.
    """
    if not token:
        return None, "Password reset token is missing."
    
    from backend.config import Config
    secret = "ai_interview_assessment_super_secret_key_2026"
    try:
        if current_app:
            secret = current_app.config.get("SECRET_KEY", secret)
    except Exception:
        secret = getattr(Config, "SECRET_KEY", secret)

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, "This password reset link has expired (links are valid for 20 minutes). Please request a new one."
    except Exception:
        return None, "Invalid password reset link. Please request a new one."

    if payload.get("purpose") != "password_reset":
        return None, "Invalid token purpose."

    user_id = payload.get("user_id")
    user = User.query.get(user_id) if user_id else None
    if not user:
        return None, "User account associated with this reset link was not found."

    token_fp = payload.get("fp", "")
    current_fp = (user.password_hash or "")[-12:]
    if token_fp != current_fp:
        return None, "This password reset link has already been used. Please request a new link if needed."

    return user, None


