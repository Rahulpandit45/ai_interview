import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Load environment variables from .env file if present
load_dotenv(os.path.join(PROJECT_ROOT, ".env"), override=True)
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

def normalize_db_uri(uri: str) -> str:
    """
    Normalizes PostgreSQL and MySQL database URIs for SQLAlchemy compatibility.
    Handles 'postgres://' -> 'postgresql+psycopg://' and 'postgresql://' -> 'postgresql+psycopg://'.
    """
    if not uri:
        return uri
    uri = uri.strip()
    if uri.startswith("postgres://"):
        return "postgresql+psycopg://" + uri[len("postgres://"):]
    if uri.startswith("postgresql://") and not uri.startswith("postgresql+"):
        return "postgresql+psycopg://" + uri[len("postgresql://"):]
    return uri

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai_interview_assessment_super_secret_key_2026")
    
    # Upload directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    RESUME_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    RECORDING_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "recordings")
    PROFILE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "profiles")
    
    # Trained models directory
    MODELS_DIR = os.path.join(BASE_DIR, "trained_models")
    
    # Reports output
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    
    # Allowed file extensions
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx", "txt"}
    ALLOWED_RECORDING_EXTENSIONS = {"webm", "mp4", "wav", "ogg", "mp3"}
    ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Max file upload size (100MB for media)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    
    # Database configuration (PostgreSQL Primary, MySQL / SQLite fallback)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "interview_db")
    
    DEFAULT_POSTGRES_URI = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Legacy MySQL default
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
    MYSQL_DB = os.environ.get("MYSQL_DB", "interview_db")
    DEFAULT_MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'interview_db.sqlite')}"
    
    # Resolve SQLALCHEMY_DATABASE_URI
    _raw_db_url = os.environ.get("DATABASE_URL", DEFAULT_POSTGRES_URI)
    SQLALCHEMY_DATABASE_URI = normalize_db_uri(_raw_db_url)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase Object Storage Configuration
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_KEY", "")).strip()
    SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "ai-interview").strip()
    
    # AI Model Settings
    WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL", "tiny")
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    FACE_LANDMARKER_MODEL_PATH = os.path.join(MODELS_DIR, "face_landmarker.task")
    SCORING_MODEL_PATH = os.path.join(MODELS_DIR, "multimodal_scoring_rf.pkl")

    # Application Environment ('development' or 'production')
    APP_ENV = os.environ.get("APP_ENV", os.environ.get("FLASK_ENV", "development")).strip().lower()

    # Email Provider Configuration (SMTP or Resend API)
    EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "smtp").strip().lower()
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
    EMAIL_FROM = os.environ.get("EMAIL_FROM", os.environ.get("MAIL_DEFAULT_SENDER", "AI Interview <onboarding@resend.dev>")).strip()

    # SMTP Settings (Gmail, Outlook, Yahoo, University SMTP)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", os.environ.get("SMTP_SERVER", "smtp.gmail.com")).strip()
    MAIL_PORT = int(os.environ.get("MAIL_PORT", os.environ.get("SMTP_PORT", 587)))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", os.environ.get("SMTP_USERNAME", "")).strip()
    
    # Clean up Google App Password spaces if present (e.g., 'abcd efgh ijkl mnop' -> 'abcdefghijklmnop')
    _raw_mail_pass = os.environ.get("MAIL_PASSWORD", os.environ.get("SMTP_PASSWORD", "")).strip()
    MAIL_PASSWORD = _raw_mail_pass.replace(" ", "") if (len(_raw_mail_pass.replace(" ", "")) == 16 and "gmail.com" in MAIL_SERVER.lower()) else _raw_mail_pass

    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "AI Interview Assessment System <noreply@interview.ai>").strip()
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 12))  # Timeout in seconds
    MAIL_AUTO_FALLBACK = os.environ.get("MAIL_AUTO_FALLBACK", "true").lower() in ["true", "1", "yes"]

    # OTP Lifecycle Policies
    OTP_EXPIRE_MINUTES = int(os.environ.get("OTP_EXPIRE_MINUTES", os.environ.get("OTP_EXPIRY_MINUTES", 5)))
    OTP_EXPIRY_MINUTES = OTP_EXPIRE_MINUTES  # Compatibility alias
    OTP_RESEND_COOLDOWN_SECONDS = int(os.environ.get("OTP_RESEND_COOLDOWN_SECONDS", 60))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 5))

    # Email Verification Link Policies
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000").rstrip("/")
    VERIFICATION_LINK_EXPIRE_MINUTES = int(os.environ.get("VERIFICATION_LINK_EXPIRE_MINUTES", 15))

    @classmethod
    def is_production(cls) -> bool:
        """Returns True if the application is configured to run in production mode."""
        if cls.APP_ENV in ["production", "prod"]:
            return True
        env_val = os.environ.get("APP_ENV", cls.APP_ENV).strip().lower()
        return env_val in ["production", "prod"]

    @classmethod
    def is_development(cls) -> bool:
        """Returns True if running in development mode."""
        return not cls.is_production()

    @classmethod
    def is_supabase_configured(cls) -> bool:
        """Checks whether valid Supabase Storage credentials and bucket are configured."""
        url = (cls.SUPABASE_URL or "").strip()
        key = (cls.SUPABASE_SERVICE_ROLE_KEY or "").strip()
        bucket = (cls.SUPABASE_STORAGE_BUCKET or "").strip()
        if not url or not key or not bucket:
            return False
        if any(p in url.lower() for p in ["your_supabase", "placeholder", "xxx", "your-project"]):
            return False
        if any(p in key.lower() for p in ["your_supabase", "placeholder", "xxx", "your_service_role_key"]):
            return False
        return url.startswith("http://") or url.startswith("https://")

    @classmethod
    def is_resend_configured(cls) -> bool:
        """Checks whether a valid Resend API key is provided."""
        key = (cls.RESEND_API_KEY or os.environ.get("RESEND_API_KEY", "")).strip()
        if not key or key in ["YOUR_RESEND_API_KEY", "re_your_api_key_here"]:
            return False
        return key.startswith("re_")

    @classmethod
    def is_smtp_configured(cls) -> bool:
        """Checks whether valid SMTP delivery credentials are provided."""
        user = cls.MAIL_USERNAME.strip()
        pwd = cls.MAIL_PASSWORD.strip()
        srv = cls.MAIL_SERVER.strip()
        if not user or not pwd or not srv:
            return False
        # Avoid treating placeholder values as active credentials
        if user in ["your_actual_gmail@gmail.com", "your_email@gmail.com"]:
            return False
        if pwd in ["your_16_digit_app_password", "your_password_here"]:
            return False
        return True

    @classmethod
    def is_email_configured(cls) -> bool:
        """Checks whether any real email provider (SMTP or Resend API) is configured."""
        if cls.EMAIL_PROVIDER == "smtp":
            return cls.is_smtp_configured() or cls.is_resend_configured()
        elif cls.EMAIL_PROVIDER == "resend":
            return cls.is_resend_configured() or cls.is_smtp_configured()
        return cls.is_smtp_configured() or cls.is_resend_configured()

    @classmethod
    def get_envelope_sender(cls) -> str:
        """
        Returns a clean RFC 5321 bare email address (e.g. user@gmail.com)
        strictly required by SMTP servers for MAIL FROM command.
        """
        from email.utils import parseaddr
        _, parsed_email = parseaddr(cls.MAIL_DEFAULT_SENDER)

        # For Gmail/Google Workspace, envelope must match authenticated username if username is an email
        if "gmail.com" in cls.MAIL_SERVER.lower() or "googlemail.com" in cls.MAIL_SERVER.lower():
            if "@" in cls.MAIL_USERNAME:
                return cls.MAIL_USERNAME.lower()

        if parsed_email and "@" in parsed_email:
            return parsed_email.lower()
        if cls.MAIL_USERNAME and "@" in cls.MAIL_USERNAME:
            return cls.MAIL_USERNAME.lower()
        return "noreply@interview.ai"

    @classmethod
    def get_formatted_sender(cls) -> str:
        """
        Returns an RFC 5322 header format for the 'From:' field (e.g. 'Display Name <email@domain.com>').
        """
        from email.utils import parseaddr
        display_name, parsed_email = parseaddr(cls.MAIL_DEFAULT_SENDER)
        if not display_name:
            display_name = "AI Interview System"
        envelope = cls.get_envelope_sender()
        return f"{display_name} <{envelope}>"
