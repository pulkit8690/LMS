import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Configuration class for Flask app settings."""

    # ─────────────────────────────────────────────────────────
    #  Security Keys
    # ─────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(24).hex())

    # ─────────────────────────────────────────────────────────
    #  Database Configuration
    # ─────────────────────────────────────────────────────────
    DATABASE_URL = os.getenv("DATABASE_URL")

    # ✅ Ensure PostgreSQL URL format is correct
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    else:
        raise ValueError("❌ DATABASE_URL is not set! Please check your environment variables.")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─────────────────────────────────────────────────────────
    #  Redis Configuration (Render)
    # ─────────────────────────────────────────────────────────
    REDIS_URL = os.getenv("REDIS_URL")

    if not REDIS_URL:
        print("⚠ Warning: REDIS_URL is missing! Using local Redis instance (localhost:6379)")
        REDIS_URL = "redis://localhost:6379/0"  # ✅ Use local Redis as fallback

    # ─────────────────────────────────────────────────────────
    #  Rate Limiting (Flask-Limiter)
    # ─────────────────────────────────────────────────────────
    RATELIMIT_STORAGE_URL = REDIS_URL
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
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("⚠ Warning: MAIL_USERNAME or MAIL_PASSWORD is missing! Email notifications may not work.")

    MAIL_DEFAULT_SENDER = MAIL_USERNAME if MAIL_USERNAME else "noreply@example.com"

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
    #  Celery Configuration (Using Redis)
    # ─────────────────────────────────────────────────────────
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
