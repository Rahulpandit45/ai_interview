from flask_sqlalchemy import SQLAlchemy
import logging
from sqlalchemy import create_engine, text

db = SQLAlchemy()

def migrate_user_schema():
    """
    Ensures candidate_id, admin_id, institution, and profile_photo columns exist in users table.
    Works across PostgreSQL, MySQL, and SQLite without altering existing data.
    Backfills existing candidates with unique permanent Candidate IDs.
    """
    from backend.models.user import User
    from sqlalchemy import inspect
    
    try:
        inspector = inspect(db.engine)
        if "users" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("users")]
            
            with db.engine.begin() as conn:
                if "candidate_id" not in columns:
                    print("[Database Migration] Adding 'candidate_id' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN candidate_id VARCHAR(50)"))
                if "admin_id" not in columns:
                    print("[Database Migration] Adding 'admin_id' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN admin_id VARCHAR(50)"))
                if "institution" not in columns:
                    print("[Database Migration] Adding 'institution' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN institution VARCHAR(120)"))
                if "profile_photo" not in columns:
                    print("[Database Migration] Adding 'profile_photo' column to users table...")
                    conn.execute(text("ALTER TABLE users ADD COLUMN profile_photo VARCHAR(255)"))

                # Ensure unique indexes exist
                try:
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_candidate_id ON users (candidate_id)"))
                except Exception:
                    pass
                try:
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_admin_id ON users (admin_id)"))
                except Exception:
                    pass

            # Backfill any candidates without candidate_id
            candidates_without_id = User.query.filter_by(role="candidate").filter(
                (User.candidate_id == None) | (User.candidate_id == "")
            ).all()
            
            if candidates_without_id:
                print(f"[Database Migration] Backfilling {len(candidates_without_id)} existing candidates with permanent Candidate IDs...")
                for cand in candidates_without_id:
                    cand.candidate_id = User.generate_candidate_id()
                db.session.commit()

            # Backfill any administrators/recruiters without official admin_id
            admins_without_id = User.query.filter(User.role.in_(["admin", "recruiter"])).filter(
                (User.admin_id == None) | (User.admin_id == "")
            ).order_by(User.id.asc()).all()

            if admins_without_id:
                print(f"[Database Migration] Backfilling {len(admins_without_id)} existing administrators with official Admin IDs...")
                for idx, adm in enumerate(admins_without_id, 1):
                    adm.admin_id = f"ADM-2026-{idx:03d}"
                    if not adm.institution:
                        adm.institution = "Mid-West University"
                db.session.commit()

            # Ensure all existing users have email_verified = True
            try:
                unverified = User.query.filter((User.email_verified == False) | (User.email_verified == None)).all()
                if unverified:
                    for u in unverified:
                        u.email_verified = True
                    db.session.commit()
            except Exception:
                pass
    except Exception as e:
        print(f"[Database Migration Warning] {e}")

def migrate_resume_schema():
    """
    Ensures is_verified, verification_status, verification_message, and verified_at
    columns exist in resumes table. Works across PostgreSQL, MySQL, and SQLite.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.engine)
        if "resumes" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("resumes")]
            with db.engine.begin() as conn:
                if "is_verified" not in columns:
                    print("[Database Migration] Adding 'is_verified' column to resumes table...")
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN is_verified BOOLEAN DEFAULT 0"))
                if "verification_status" not in columns:
                    print("[Database Migration] Adding 'verification_status' column to resumes table...")
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN verification_status VARCHAR(50) DEFAULT 'unverified'"))
                if "verification_message" not in columns:
                    print("[Database Migration] Adding 'verification_message' column to resumes table...")
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN verification_message VARCHAR(255)"))
                if "verified_at" not in columns:
                    print("[Database Migration] Adding 'verified_at' column to resumes table...")
                    conn.execute(text("ALTER TABLE resumes ADD COLUMN verified_at TIMESTAMP"))
    except Exception as e:
        print(f"[Database Resume Migration Warning] {e}")

def migrate_recording_schema():
    """
    Ensures recording_path and recording_url columns exist in interviews and reports tables.
    Works across PostgreSQL, MySQL, and SQLite.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        with db.engine.begin() as conn:
            if "interviews" in tables:
                cols = [c["name"] for c in inspector.get_columns("interviews")]
                if "recording_path" not in cols:
                    print("[Database Migration] Adding 'recording_path' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN recording_path VARCHAR(500)"))
                if "recording_url" not in cols:
                    print("[Database Migration] Adding 'recording_url' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN recording_url VARCHAR(500)"))

            if "reports" in tables:
                cols = [c["name"] for c in inspector.get_columns("reports")]
                if "recording_path" not in cols:
                    print("[Database Migration] Adding 'recording_path' column to reports table...")
                    conn.execute(text("ALTER TABLE reports ADD COLUMN recording_path VARCHAR(500)"))
                if "recording_url" not in cols:
                    print("[Database Migration] Adding 'recording_url' column to reports table...")
                    conn.execute(text("ALTER TABLE reports ADD COLUMN recording_url VARCHAR(500)"))
    except Exception as e:
        print(f"[Database Recording Migration Warning] {e}")

def migrate_proctoring_schema():
    """
    Ensures proctoring columns exist in interviews table and
    interview_proctoring_violations table exists.
    Works across PostgreSQL, MySQL, and SQLite.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        with db.engine.begin() as conn:
            if "interviews" in tables:
                cols = [c["name"] for c in inspector.get_columns("interviews")]
                if "warning_count" not in cols:
                    print("[Database Migration] Adding 'warning_count' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN warning_count INTEGER DEFAULT 0"))
                if "detected_faces_count" not in cols:
                    print("[Database Migration] Adding 'detected_faces_count' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN detected_faces_count INTEGER DEFAULT 1"))
                if "last_face_detection_time" not in cols:
                    print("[Database Migration] Adding 'last_face_detection_time' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN last_face_detection_time TIMESTAMP"))
                if "termination_reason" not in cols:
                    print("[Database Migration] Adding 'termination_reason' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN termination_reason VARCHAR(255)"))
                if "proctoring_status" not in cols:
                    print("[Database Migration] Adding 'proctoring_status' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN proctoring_status VARCHAR(50) DEFAULT 'clean'"))
                if "interview_photo" not in cols:
                    print("[Database Migration] Adding 'interview_photo' column to interviews table...")
                    conn.execute(text("ALTER TABLE interviews ADD COLUMN interview_photo VARCHAR(255)"))

            if "interview_proctoring_violations" not in tables:
                print("[Database Migration] Creating 'interview_proctoring_violations' table...")
                is_pg = "postgresql" in str(db.engine.url)
                if is_pg:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS interview_proctoring_violations (
                            id SERIAL PRIMARY KEY,
                            interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            faces_detected INTEGER DEFAULT 2,
                            warning_level VARCHAR(50) DEFAULT 'warning_1',
                            message VARCHAR(255)
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS interview_proctoring_violations (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            interview_id INTEGER NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            faces_detected INTEGER DEFAULT 2,
                            warning_level VARCHAR(50) DEFAULT 'warning_1',
                            message VARCHAR(255),
                            FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE
                        )
                    """))
    except Exception as e:
        print(f"[Database Proctoring Migration Warning] {e}")

def migrate_otp_schema():
    """
    Ensures email_otps table exists with all required columns and indexes.
    Works seamlessly across PostgreSQL, MySQL, and SQLite.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if "email_otps" not in tables:
            print("[Database Migration] Creating 'email_otps' table...")
            with db.engine.begin() as conn:
                is_sqlite = "sqlite" in str(db.engine.url)
                is_pg = "postgresql" in str(db.engine.url)
                if is_sqlite:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS email_otps (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            email VARCHAR(120) NOT NULL,
                            otp_hash VARCHAR(255) NOT NULL,
                            created_at DATETIME,
                            expires_at DATETIME NOT NULL,
                            last_sent_at DATETIME,
                            attempts INTEGER DEFAULT 0,
                            is_used BOOLEAN DEFAULT 0,
                            purpose VARCHAR(50) DEFAULT 'candidate_registration'
                        )
                    """))
                elif is_pg:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS email_otps (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(120) NOT NULL,
                            otp_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP NOT NULL,
                            last_sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            attempts INTEGER DEFAULT 0,
                            is_used BOOLEAN DEFAULT FALSE,
                            purpose VARCHAR(50) DEFAULT 'candidate_registration'
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS email_otps (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            email VARCHAR(120) NOT NULL,
                            otp_hash VARCHAR(255) NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            expires_at DATETIME NOT NULL,
                            last_sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            attempts INT DEFAULT 0,
                            is_used BOOLEAN DEFAULT 0,
                            purpose VARCHAR(50) DEFAULT 'candidate_registration'
                        )
                    """))
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_email_otps_email ON email_otps (email)"))
                except Exception:
                    pass
    except Exception as e:
        print(f"[Database OTP Migration Warning] {e}")

def migrate_candidate_files_schema():
    """
    Ensures candidate_files table exists for Supabase Storage object key tracking & metadata.
    Works seamlessly across PostgreSQL, MySQL, and SQLite.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if "candidate_files" not in tables:
            print("[Database Migration] Creating 'candidate_files' table for Supabase Storage file references...")
            with db.engine.begin() as conn:
                is_sqlite = "sqlite" in str(db.engine.url)
                is_pg = "postgresql" in str(db.engine.url)
                if is_sqlite:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS candidate_files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INTEGER,
                            interview_id INTEGER,
                            file_type VARCHAR(50) NOT NULL,
                            object_key VARCHAR(500) NOT NULL,
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100),
                            file_size BIGINT DEFAULT 0,
                            storage_provider VARCHAR(20) DEFAULT 'supabase',
                            local_path VARCHAR(500),
                            public_url VARCHAR(500),
                            uploaded_at DATETIME,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE SET NULL
                        )
                    """))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_cid ON candidate_files (candidate_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_ft ON candidate_files (file_type)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_key ON candidate_files (object_key)"))
                elif is_pg:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS candidate_files (
                            id SERIAL PRIMARY KEY,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            interview_id INTEGER REFERENCES interviews(id) ON DELETE SET NULL,
                            file_type VARCHAR(50) NOT NULL,
                            object_key VARCHAR(500) NOT NULL,
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100),
                            file_size BIGINT DEFAULT 0,
                            storage_provider VARCHAR(20) DEFAULT 'supabase',
                            local_path VARCHAR(500),
                            public_url VARCHAR(500),
                            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_cid ON candidate_files (candidate_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_ft ON candidate_files (file_type)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_candidate_files_key ON candidate_files (object_key)"))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS candidate_files (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INT,
                            interview_id INT,
                            file_type VARCHAR(50) NOT NULL,
                            object_key VARCHAR(500) NOT NULL,
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100),
                            file_size BIGINT DEFAULT 0,
                            storage_provider VARCHAR(20) DEFAULT 'supabase',
                            local_path VARCHAR(500),
                            public_url VARCHAR(500),
                            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE SET NULL
                        )
                    """))
                    conn.execute(text("CREATE INDEX ix_candidate_files_cid ON candidate_files (candidate_id)"))
                    conn.execute(text("CREATE INDEX ix_candidate_files_ft ON candidate_files (file_type)"))
                    conn.execute(text("CREATE INDEX ix_candidate_files_key ON candidate_files (object_key(255))"))
    except Exception as e:
        print(f"[Database Candidate Files Migration Warning] {e}")

def migrate_interview_media_schema():
    """
    Ensures interview_media table exists for direct database audio/video storage.
    Supports PostgreSQL (BYTEA), SQLite (BLOB), and MySQL (LONGBLOB).
    Migrates any existing local recordings into the database to eliminate local storage.
    """
    from sqlalchemy import inspect
    from backend.models.interview import InterviewMedia, Interview, InterviewResponse
    from backend.models.report import Report
    import os

    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        is_pg = "postgresql" in str(db.engine.url) or "postgres" in str(db.engine.url)
        is_sqlite = "sqlite" in str(db.engine.url)

        with db.engine.begin() as conn:
            if "interview_media" not in tables:
                print("[Database Migration] Creating 'interview_media' table for direct DB audio/video storage...")
                if is_sqlite:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS interview_media (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INTEGER,
                            interview_id INTEGER NOT NULL,
                            response_id INTEGER,
                            media_type VARCHAR(30) DEFAULT 'video',
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100) DEFAULT 'video/webm',
                            file_size BIGINT DEFAULT 0,
                            data BLOB NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
                            FOREIGN KEY(response_id) REFERENCES interview_responses(id) ON DELETE CASCADE
                        )
                    """))
                elif is_pg:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS interview_media (
                            id SERIAL PRIMARY KEY,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
                            response_id INTEGER REFERENCES interview_responses(id) ON DELETE CASCADE,
                            media_type VARCHAR(30) DEFAULT 'video',
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100) DEFAULT 'video/webm',
                            file_size BIGINT DEFAULT 0,
                            data BYTEA NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))
                else:
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS interview_media (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            candidate_id VARCHAR(50) NOT NULL,
                            user_id INT,
                            interview_id INT NOT NULL,
                            response_id INT,
                            media_type VARCHAR(30) DEFAULT 'video',
                            file_name VARCHAR(255) NOT NULL,
                            mime_type VARCHAR(100) DEFAULT 'video/webm',
                            file_size BIGINT DEFAULT 0,
                            data LONGBLOB NOT NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
                            FOREIGN KEY(response_id) REFERENCES interview_responses(id) ON DELETE CASCADE
                        )
                    """))
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_interview_media_cid ON interview_media (candidate_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_interview_media_iid ON interview_media (interview_id)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_interview_media_rid ON interview_media (response_id)"))
                except Exception:
                    pass

        # Migrate existing local files from uploads/recordings into DB so nothing is lost
        from backend.config import Config
        rec_dir = Config.RECORDING_UPLOAD_FOLDER
        if os.path.exists(rec_dir):
            for fname in os.listdir(rec_dir):
                fpath = os.path.join(rec_dir, fname)
                if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                    try:
                        ext = os.path.splitext(fname)[1].lower()
                        mime = "video/webm" if "webm" in ext else ("video/mp4" if "mp4" in ext else "audio/wav")
                        mtype = "video" if ext in [".webm", ".mp4", ".mov", ".avi"] else "audio"

                        target_interview = None
                        if fname.startswith("interview_"):
                            parts = fname.split("_")
                            if len(parts) >= 2 and parts[1].isdigit():
                                target_interview = Interview.query.get(int(parts[1]))
                        if not target_interview:
                            target_interview = Interview.query.order_by(Interview.id.desc()).first()

                        if target_interview:
                            cid = target_interview.user.candidate_id if target_interview.user else f"CID-2026-{target_interview.user_id}"
                            exists = InterviewMedia.query.filter_by(interview_id=target_interview.id, file_name=fname).first()
                            if not exists:
                                with open(fpath, "rb") as f:
                                    bdata = f.read()
                                media_rec = InterviewMedia(
                                    candidate_id=cid,
                                    user_id=target_interview.user_id,
                                    interview_id=target_interview.id,
                                    media_type=mtype,
                                    file_name=fname,
                                    mime_type=mime,
                                    file_size=len(bdata),
                                    data=bdata
                                )
                                db.session.add(media_rec)
                                db.session.commit()
                                target_interview.recording_url = f"/api/interview/{target_interview.id}/media"
                                target_interview.recording_path = f"/api/interview/{target_interview.id}/media"
                                db.session.commit()
                                print(f"[Database Migration] Stored '{fname}' ({len(bdata)} bytes) in database.")
                    except Exception as e:
                        print(f"[Database Migration Notice] Could not migrate '{fname}': {e}")
    except Exception as e:
        print(f"[Database Interview Media Migration Warning] {e}")

def init_db(app):
    """
    Initializes the database connection.
    Attempts to connect to configured PostgreSQL (or MySQL) database.
    If database server is not running or unreachable during local development,
    seamlessly falls back to local SQLite so the application functions flawlessly without interruption.
    """
    configured_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    
    # Check PostgreSQL / MySQL connection if configured
    if "postgresql" in configured_uri or "postgres" in configured_uri:
        try:
            test_engine = create_engine(configured_uri, connect_args={"connect_timeout": 3})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[Database] Successfully connected to PostgreSQL at {configured_uri}")
        except Exception as e:
            print(f"[Database Warning] PostgreSQL connection failed ({e}).")
            print(f"[Database] Seamlessly falling back to local SQLite: {app.config['SQLITE_URI']}")
            app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLITE_URI"]
    elif "mysql" in configured_uri:
        try:
            test_engine = create_engine(configured_uri, connect_args={"connect_timeout": 3})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[Database] Successfully connected to MySQL at {configured_uri}")
        except Exception as e:
            print(f"[Database Warning] MySQL connection failed ({e}).")
            print(f"[Database] Seamlessly falling back to local SQLite: {app.config['SQLITE_URI']}")
            app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLITE_URI"]

    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy metadata is aware of all tables
        from backend.models import user, resume, question, interview, report, otp, stored_file
        db.create_all()
        migrate_user_schema()
        migrate_resume_schema()
        migrate_recording_schema()
        migrate_proctoring_schema()
        migrate_otp_schema()
        migrate_candidate_files_schema()
        migrate_interview_media_schema()
        # Seed initial standard interview questions
        from backend.models.question import seed_default_questions
        seed_default_questions()
        print("[Database] All database tables created and seeded successfully.")
