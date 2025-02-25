# extensions.py

import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
socketio = None  # We will initialize it in init_extensions()

# Rate Limiting
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    strategy="fixed-window",
    default_limits=["200 per hour", "50 per minute"],
)


def init_extensions(app):
    """
    Initialize Flask extensions.
    """
    global socketio

    print("🔄 Initializing Flask extensions...")

    with app.app_context():
        try:
            db.init_app(app)
            migrate.init_app(app, db)
            mail.init_app(app)
            jwt.init_app(app)
            limiter.init_app(app)

            # ✅ Ensure `socketio` is initialized
            socketio = SocketIO(
                app,
                cors_allowed_origins="*",
                async_mode="eventlet",  # Use "threading" if eventlet is problematic
                message_queue=REDIS_URL if "redis" in REDIS_URL else None,
            )

            print("✅ socketio initialized:", socketio)  # Debugging line
            app.logger.info("✅ Flask extensions initialized successfully!")

        except Exception as e:
            print(f"❌ Error initializing extensions: {e}")
            raise e  # This will help us debug what's failing

