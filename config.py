import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for environment variables and app settings."""

    # ✅ Security Keys
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(24).hex())

    # ✅ Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:12345@localhost/library_db")

    # ✅ Ensure compatibility with PostgreSQL URLs (Heroku fix)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Rate Limiting (Prevents API Abuse)
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")  # Default: in-memory
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per minute")  # Default rate limit

    # ✅ CORS Configuration
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")  # Default: Allow all origins

    # ✅ Debug Mode (Configurable from .env)
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # ✅ Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # ✅ WebSocket Support
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")

    # ✅ Payment Gateway (Razorpay)
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_SECRET_KEY = os.getenv("RAZORPAY_SECRET_KEY")

    # ✅ Celery Configuration (Task Queue)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
