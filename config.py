import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


class Config:
    """Configuration class for environment variables and app settings."""

    # ─────────────────────────────────────────────────────────
    #  Security Keys
    # ─────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(24).hex()
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.urandom(24).hex()

    # ─────────────────────────────────────────────────────────
    #  Database Configuration
    # ─────────────────────────────────────────────────────────
    DATABASE_URL = os.getenv("DATABASE_URL")

    # If using PostgreSQL, the old URL format "postgres://" needs to become "postgresql://"
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        raise ValueError("❌ DATABASE_URL is not set! Please check your environment variables.")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─────────────────────────────────────────────────────────
    #  Rate Limiting (Flask-Limiter)
    # ─────────────────────────────────────────────────────────
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per minute")

    # ─────────────────────────────────────────────────────────
    #  Flask Debug Mode
    # ─────────────────────────────────────────────────────────
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # ─────────────────────────────────────────────────────────
    #  CORS Configuration
    # ─────────────────────────────────────────────────────────
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")

    # ─────────────────────────────────────────────────────────
    #  Email Configuration
    # ─────────────────────────────────────────────────────────
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_DEFAULT_SENDER = MAIL_USERNAME if MAIL_USERNAME else "noreply@example.com"

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        raise ValueError("❌ MAIL_USERNAME or MAIL_PASSWORD is missing! Please check your environment variables.")

    # ─────────────────────────────────────────────────────────
    #  WebSocket (SocketIO) Settings
    # ─────────────────────────────────────────────────────────
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")

    # ─────────────────────────────────────────────────────────
    #  Razorpay Configuration
    # ─────────────────────────────────────────────────────────
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_SECRET_KEY = os.getenv("RAZORPAY_SECRET_KEY")

    # ─────────────────────────────────────────────────────────
    #  Celery Configuration
    # ─────────────────────────────────────────────────────────
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
