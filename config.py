"""Central configuration. Every value comes from environment variables (.env)."""
import os
from decimal import Decimal
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def _bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def _resolve_database_uri():
    # SQLite is default as specified.
    # If DATABASE_URL is explicitly set to an existing SQLite path or if USE_MYSQL is enabled,
    # we honor it; otherwise we default to local SQLite.
    env_db = os.getenv("DATABASE_URL", "")
    force_mysql = _bool("USE_MYSQL", False)

    if env_db and not force_mysql and env_db.startswith("mysql"):
        # Default to SQLite unless MySQL is explicitly requested and running
        sqlite_path = os.path.join(basedir, "skillswap.db")
        return f"sqlite:///{sqlite_path}"

    if env_db:
        return env_db

    sqlite_path = os.path.join(basedir, "skillswap.db")
    return f"sqlite:///{sqlite_path}"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "skillswap-dev-secret-key-college-demo-2026")
    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {}
        if SQLALCHEMY_DATABASE_URI.startswith("sqlite")
        else {"pool_pre_ping": True, "pool_recycle": 280}
    )

    # Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB uploads
    UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "300 per hour"

    # Video
    JITSI_DOMAIN = os.getenv("JITSI_DOMAIN", "meet.jit.si")
    JITSI_SCRIPT_URL = os.getenv("JITSI_SCRIPT_URL", "https://meet.jit.si/external_api.js")

    # Wallet & Credits
    SIGNUP_BONUS_CREDITS = Decimal(os.getenv("SIGNUP_BONUS_CREDITS", "2.0"))
    ALLOWED_DURATIONS_MIN = (30, 60, 90, 120)

    # AI
    AI_ENCRYPTION_KEY = os.getenv("AI_ENCRYPTION_KEY", "")
    PLATFORM_AI_ENABLED = _bool("PLATFORM_AI_ENABLED", False)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    HOSTED_FREE_ENABLED = _bool("HOSTED_FREE_ENABLED", False)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    AI_USER_REQUESTS_PER_DAY = int(os.getenv("AI_USER_REQUESTS_PER_DAY", "30"))
    AI_MAX_INPUT_CHARS = int(os.getenv("AI_MAX_INPUT_CHARS", "4000"))
    AI_MAX_OUTPUT_TOKENS = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "1200"))


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    PLATFORM_AI_ENABLED = False
    HOSTED_FREE_ENABLED = False
