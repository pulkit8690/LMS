from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

# ✅ Initialize extensions (Not attached to app yet)
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")
jwt = JWTManager()
