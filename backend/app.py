import os
import sys

# Ensure root workspace directory is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.services.database import db, init_db

# Import Blueprints
from backend.routes.auth_routes import auth_bp
from backend.routes.resume_routes import resume_bp
from backend.routes.interview_routes import interview_bp
from backend.routes.report_routes import report_bp
from backend.routes.admin_routes import admin_bp
from backend.routes.qa_routes import qa_bp
from backend.routes.storage_routes import storage_bp

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure uploads and reports directories exist
    os.makedirs(app.config["RESUME_UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RECORDING_UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["PROFILE_UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_DIR"], exist_ok=True)

    # Initialize Database
    init_db(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(storage_bp)

    # Seed Initial Administrator and Candidate Accounts
    with app.app_context():
        from backend.models.user import User
        # System Administrator / Recruitment Lead (Official Institutional Admin)
        admin = User.query.filter_by(email="admin@interview.ai").first()
        if not admin:
            admin = User(
                admin_id="ADM-2026-001",
                full_name="System Administrator (Mid-West University)",
                email="admin@interview.ai",
                role="admin",
                institution="Mid-West University",
                target_role="Recruitment Lead",
                phone="+977-9800000000"
            )
            admin.set_password("admin123")
            db.session.add(admin)
        else:
            if not admin.admin_id:
                admin.admin_id = "ADM-2026-001"
            if not admin.institution:
                admin.institution = "Mid-West University"

        db.session.commit()

    # Frontend Static File Serving
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/forgot-password")
    def forgot_password_page():
        return send_from_directory(frontend_dir, "forgot-password.html")

    @app.route("/reset-password/<token>")
    @app.route("/reset-password")
    def reset_password_page(token=None):
        return send_from_directory(frontend_dir, "reset-password.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        target = os.path.join(frontend_dir, path)
        if os.path.exists(target):
            return send_from_directory(frontend_dir, path)
        # Check if requesting an html page without extension
        html_target = os.path.join(frontend_dir, f"{path}.html")
        if os.path.exists(html_target):
            return send_from_directory(frontend_dir, f"{path}.html")
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.route("/api/health")
    def health_check():
        db_uri = str(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
        db_type = "postgresql" if "postgres" in db_uri else ("sqlite" if "sqlite" in db_uri else "mysql")
        return jsonify({
            "status": "online",
            "system": "AI-Powered Video Interview Assessment System",
            "version": "1.0.0",
            "database": {
                "type": db_type,
                "status": "connected"
            },
            "storage": {
                "supabase_configured": Config.is_supabase_configured(),
                "bucket": Config.SUPABASE_STORAGE_BUCKET if Config.is_supabase_configured() else None
            },
            "whisper": "ready",
            "sentence_transformers": "ready",
            "cv_mesh": "ready"
        })

    return app

app = create_app()

if __name__ == "__main__":
    print("====================================================================")
    print("  AI-POWERED INTELLIGENT VIDEO INTERVIEW ASSESSMENT SYSTEM")
    print("  Server running at: http://localhost:5000")
    print("====================================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
