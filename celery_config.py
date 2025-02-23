from celery import Celery
from config import Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)

def init_celery(app):
    """Initialize Celery with Flask application context."""
    celery.conf.update(app.config)
    celery.Task = ContextTask(app)

class ContextTask(celery.Task):
    """Ensure Celery runs within Flask's app context."""
    def __call__(self, *args, **kwargs):
        with self.app.app_context():
            return self.run(*args, **kwargs)
