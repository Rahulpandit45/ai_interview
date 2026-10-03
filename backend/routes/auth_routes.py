from flask import Blueprint, request, jsonify
from backend.services.database import db
from backend.models.user import User
from backend.utils.security import generate_token, token_required, verify_email_token
from backend.utils.photo_storage import process_and_save_photo
from backend.services.otp_service import OTPService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    """
    Sends a 6-digit verification code to the candidate's email address.
    Enforces rate-limiting cooldown and checks for duplicate registrations.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    full_name = data.get("full_name", "").strip()
    resp, code = OTPService.send_registration_otp(email, full_name)
    return jsonify(resp), code

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Validates the 6-digit OTP code submitted by the candidate.
    Issues a cryptographically signed verification token upon successful match.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    otp = data.get("otp", "").strip()
    resp, code = OTPService.verify_registration_otp(email, otp)
    return jsonify(resp), code

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """
    Resends a 6-digit verification code to the candidate email.
    Enforces rate-limiting cooldown.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    full_name = data.get("full_name", "").strip()
    resp, code = OTPService.resend_registration_otp(email, full_name)
    return jsonify(resp), code

@auth_bp.route("/verify-link", methods=["GET", "POST"])
def verify_link():
    """
    Validates a one-click verification token clicked from candidate's email.
    Supports GET (browser query param ?token=...) and POST (JSON body {token: ...}).
    """
    token = request.args.get("token")
    if not token and request.is_json:
        token = (request.get_json() or {}).get("token")
    if not token:
        return jsonify({
            "status": "error",
            "message": "Verification token is required.",
            "code": "TOKEN_REQUIRED"
        }), 400

    resp, code = OTPService.verify_email_link(token)
    return jsonify(resp), code

@auth_bp.route("/verification-status", methods=["GET"])
def verification_status():
    """
    Polls verification status for a candidate email during registration.
    Allows auto-advancement when email link is clicked on another device or tab.
    """
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"status": "error", "message": "Email query parameter is required."}), 400
    resp, code = OTPService.check_verification_status(email)
    return jsonify(resp), code

@auth_bp.route("/test-smtp", methods=["POST", "GET"])
def test_smtp():
    """
    Diagnostic endpoint to test SMTP connectivity, SSL/TLS handshake,
    credentials, and optionally dispatch a test verification email.
    """
    from backend.services.email_service import EmailService
    from backend.config import Config
    data = request.get_json() if request.is_json else {}
    recipient = data.get("recipient", "").strip() if data else request.args.get("recipient", "").strip()

    status_result = EmailService.test_smtp_connection(test_recipient=recipient if recipient else None)
    response_code = 200 if status_result.success else (503 if status_result.error_code == "SMTP_NOT_CONFIGURED" else 502)
    return jsonify({
        "status": "success" if status_result.success else "error",
        "message": status_result.message,
        "code": status_result.error_code,
        "details": status_result.details,
        "environment": Config.APP_ENV,
        "smtp_configured": Config.is_smtp_configured(),
        "smtp_server": Config.MAIL_SERVER,
        "smtp_port": Config.MAIL_PORT,
        "envelope_sender": Config.get_envelope_sender()
    }), response_code

@auth_bp.route("/register", methods=["POST"])
def register():
    # Support both JSON payloads and multipart/form-data
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict() or {}

    email = data.get("email", "").strip().lower()
    full_name = data.get("full_name", "").strip()
    password = data.get("password", "").strip()
    requested_role = data.get("role", "candidate").strip().lower()
    target_role = data.get("target_role", "Software Engineer").strip()
    phone = data.get("phone", "").strip()

    if not email or not full_name or not password:
        return jsonify({"status": "error", "message": "Name, email, and password are required"}), 400

    # Administrator accounts must not be registered publicly
    if requested_role in ["admin", "recruiter"]:
        return jsonify({
            "status": "error",
            "message": "Administrator registration is restricted. Admin accounts are provisioned exclusively by institutional administration."
        }), 403

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "An account with this email already exists"}), 409

    # Public registration is strictly for candidates
    resolved_role = "candidate"
    candidate_id = User.generate_candidate_id()

    # Process profile photo if supplied (file upload or webcam base64)
    profile_photo_path = None
    photo_file = request.files.get("profile_photo") or request.files.get("photo")
    photo_data = data.get("profile_photo") or data.get("photo")

    photo_input = photo_file if photo_file else photo_data
    if photo_input:
        cid_for_storage = candidate_id or f"USR-{email.split('@')[0]}"
        try:
            profile_photo_path = process_and_save_photo(photo_input, cid_for_storage)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Profile photo processing failed: {str(e)}"}), 400

    user = User(
        candidate_id=candidate_id,
        full_name=full_name,
        email=email,
        role=resolved_role,
        target_role=target_role,
        phone=phone,
        profile_photo=profile_photo_path,
        email_verified=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id, role=user.role)
    return jsonify({
        "status": "success",
        "message": "Account registered successfully",
        "candidate_id": user.candidate_id,
        "token": token,
        "user": user.to_dict()
    }), 201

@auth_bp.route("/profile/photo", methods=["POST"])
@token_required
def upload_profile_photo(current_user):
    photo_file = request.files.get("profile_photo") or request.files.get("photo")
    photo_data = request.form.get("profile_photo") or request.form.get("photo")
    if not photo_data and request.is_json:
        json_data = request.get_json() or {}
        photo_data = json_data.get("profile_photo") or json_data.get("photo")

    photo_input = photo_file if photo_file else photo_data
    if not photo_input:
        return jsonify({"status": "error", "message": "No profile photo provided"}), 400

    cid = current_user.candidate_id or f"USR-{current_user.id}"
    try:
        saved_path = process_and_save_photo(photo_input, cid)
        current_user.profile_photo = saved_path
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Profile photo updated successfully",
            "user": current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    portal = data.get("portal", "").strip().lower()
    admin_id = data.get("admin_id", "").strip().upper()
    candidate_id = data.get("candidate_id", "").strip().upper()
    identifier = data.get("identifier", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    # 1. Administrator Portal Login (Admins can log in ONLY using official Admin ID)
    if portal == "admin" or admin_id:
        # If user passed identifier or email instead of admin_id field
        effective_admin_id = admin_id
        if not effective_admin_id:
            raw_id = identifier or email
            if "@" in raw_id:
                return jsonify({
                    "status": "error",
                    "message": "Admins can log in only using their official Admin ID and password. Email login is not permitted for administrators."
                }), 400
            effective_admin_id = raw_id.upper()

        if not effective_admin_id or not password:
            return jsonify({"status": "error", "message": "Official Admin ID and password are required"}), 400

        # Reject candidate IDs trying to access Admin Portal
        if User.query.filter_by(candidate_id=effective_admin_id).first():
            return jsonify({
                "status": "error",
                "message": "Access Denied: Candidate accounts cannot access the Administrator Console. Please switch to the Candidate Portal."
            }), 403

        admin_user = User.query.filter(
            (User.admin_id == effective_admin_id) & (User.role.in_(["admin", "recruiter"]))
        ).first()

        if not admin_user or not admin_user.check_password(password):
            return jsonify({"status": "error", "message": "Invalid Admin ID or password"}), 401

        token = generate_token(admin_user.id, role=admin_user.role)
        return jsonify({
            "status": "success",
            "message": "Administrator authenticated successfully",
            "token": token,
            "user": admin_user.to_dict()
        }), 200

    # 2. Candidate Portal Login
    if portal == "candidate":
        target = identifier or email or candidate_id
        if not target or not password:
            return jsonify({"status": "error", "message": "Candidate Email / ID and password are required"}), 400

        # Check if an admin attempts to sign in via candidate portal
        admin_check = User.query.filter(
            (User.email == target.lower()) | (User.admin_id == target.upper())
        ).filter(User.role.in_(["admin", "recruiter"])).first()

        if admin_check:
            return jsonify({
                "status": "error",
                "message": "Administrator account detected. Administrators must log in via the Administrator Portal using their official Admin ID."
            }), 403

        candidate_user = User.query.filter(
            (User.email == target.lower()) | (User.candidate_id == target.upper())
        ).filter_by(role="candidate").first()

        if not candidate_user or not candidate_user.check_password(password):
            return jsonify({"status": "error", "message": "Invalid candidate email or password"}), 401

        token = generate_token(candidate_user.id, role=candidate_user.role)
        return jsonify({
            "status": "success",
            "message": "Candidate login successful",
            "token": token,
            "user": candidate_user.to_dict()
        }), 200

    # 3. Direct API Login (portal unspecified)
    if not password:
        return jsonify({"status": "error", "message": "Password is required"}), 400

    # If an email is supplied, verify it is not an admin account
    target_email = email or identifier
    if target_email and "@" in target_email:
        user = User.query.filter_by(email=target_email.lower()).first()
        if user and user.role in ["admin", "recruiter"]:
            return jsonify({
                "status": "error",
                "message": "Admins can log in only using their official Admin ID and password. Direct email login is disabled for administrator accounts."
            }), 403
        if not user or not user.check_password(password):
            return jsonify({"status": "error", "message": "Invalid email or password"}), 401

        token = generate_token(user.id, role=user.role)
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }), 200

    # Lookup by Admin ID or Candidate ID
    lookup_id = (identifier or admin_id or candidate_id).upper()
    if not lookup_id:
        return jsonify({"status": "error", "message": "Email, Admin ID, or Candidate ID is required"}), 400

    user = User.query.filter(
        (User.admin_id == lookup_id) | (User.candidate_id == lookup_id)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Invalid credentials or password"}), 401

    token = generate_token(user.id, role=user.role)
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({
        "status": "success",
        "user": current_user.to_dict()
    }), 200

@auth_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile(current_user):
    """
    Allows authenticated candidate to update their profile details.
    """
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    target_role = data.get("target_role", "").strip()
    location = data.get("location", "").strip()
    linkedin = data.get("linkedin", "").strip()
    github = data.get("github", "").strip()
    education = data.get("education", "").strip()
    experience = data.get("experience", "").strip()

    if full_name:
        current_user.full_name = full_name
    if phone is not None:
        current_user.phone = phone
    if target_role:
        current_user.target_role = target_role
    if location is not None:
        current_user.location = location
    if linkedin is not None:
        current_user.linkedin = linkedin
    if github is not None:
        current_user.github = github
    if education is not None:
        current_user.education = education
    if experience is not None:
        current_user.experience = experience

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Candidate profile updated successfully",
        "user": current_user.to_dict()
    }), 200


@auth_bp.route("/password", methods=["PUT"])
@token_required
def change_password(current_user):
    """
    Allows authenticated user to update their account password.
    """
    data = request.get_json() or {}
    current_password = data.get("current_password", "").strip()
    new_password = data.get("new_password", "").strip()

    if not current_password or not new_password:
        return jsonify({"status": "error", "message": "Current password and new password are required"}), 400

    if not current_user.check_password(current_password):
        return jsonify({"status": "error", "message": "Current password is incorrect"}), 400

    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "New password must be at least 6 characters long"}), 400

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Password updated successfully"
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """
    Initiates password reset flow.
    Accepts candidate email, generates cryptographically signed 20-minute token,
    dispatches email (or logs to terminal in dev), and returns generic success response
    to prevent email enumeration.
    """
    from backend.services.email_service import EmailService
    from backend.config import Config
    from backend.utils.security import generate_password_reset_token

    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email address is required.", "code": "EMAIL_REQUIRED"}), 400

    user = User.query.filter_by(email=email).first()
    reset_url = None

    if user:
        token = generate_password_reset_token(user, expires_in_minutes=20)
        base_url = getattr(Config, "APP_BASE_URL", "http://localhost:5000").rstrip("/")
        reset_url = f"{base_url}/reset-password.html?token={token}"

        # Dispatch via email service
        EmailService.send_password_reset_email(
            to_email=user.email,
            user_name=user.full_name,
            reset_link=reset_url,
            expires_in_minutes=20
        )

    # Generic security response preventing email enumeration
    resp = {
        "status": "success",
        "message": "If an account exists with that email address, a password reset link has been dispatched."
    }

    # In local development mode, return reset_link in payload for instant testing
    if not Config.is_production() and reset_url:
        resp["reset_link"] = reset_url
        resp["dev_mode"] = True

    return jsonify(resp), 200


@auth_bp.route("/verify-reset-token", methods=["GET", "POST"])
def verify_reset_token_endpoint():
    """
    Validates a password reset token from query string (?token=...) or JSON body ({token: ...}).
    """
    from backend.utils.security import verify_password_reset_token

    token = request.args.get("token")
    if not token and request.is_json:
        token = (request.get_json() or {}).get("token")

    if not token:
        return jsonify({
            "status": "error",
            "message": "Password reset token is required.",
            "code": "TOKEN_REQUIRED"
        }), 400

    user, err_msg = verify_password_reset_token(token)
    if not user or err_msg:
        return jsonify({
            "status": "error",
            "message": err_msg or "Invalid or expired password reset link.",
            "code": "INVALID_OR_EXPIRED_TOKEN"
        }), 400

    return jsonify({
        "status": "success",
        "valid": True,
        "email": user.email,
        "full_name": user.full_name
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    Sets a new password using a validated password reset token.
    Enforces minimum length criteria (>= 6 chars) and matching passwords.
    """
    from backend.utils.security import verify_password_reset_token

    data = request.get_json() or {}
    token = data.get("token", "").strip()
    new_password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()

    if not token:
        return jsonify({"status": "error", "message": "Password reset token is required.", "code": "TOKEN_REQUIRED"}), 400

    if not new_password:
        return jsonify({"status": "error", "message": "New password is required.", "code": "PASSWORD_REQUIRED"}), 400

    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long.", "code": "PASSWORD_TOO_SHORT"}), 400

    if confirm_password and new_password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match. Please re-enter your password.", "code": "PASSWORDS_MISMATCH"}), 400

    user, err_msg = verify_password_reset_token(token)
    if not user or err_msg:
        return jsonify({
            "status": "error",
            "message": err_msg or "Invalid or expired reset token. Please request a new link.",
            "code": "INVALID_OR_EXPIRED_TOKEN"
        }), 400

    # Securely hash and update password (this also changes password fingerprint, invalidating the token)
    user.set_password(new_password)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Password successfully reset. Please log in with your new credentials."
    }), 200


