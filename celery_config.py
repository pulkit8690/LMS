import os
import logging
from celery import Celery
from flask import Flask

# Configure logging for Celery
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

celery = Celery(__name__)

def init_celery(app: Flask):
    """Initialize Celery with Flask application context."""
    try:
        celery.conf.update(
            broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
            result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
            task_serializer="json",
            accept_content=["json"],
            timezone="UTC",
        )
        logging.info("✅ Celery successfully configured with Redis broker.")
    except Exception as e:
        logging.error(f"❌ ERROR: Failed to configure Celery - {e}")
        raise

    class ContextTask(celery.Task):
        """Ensures Celery tasks run within Flask's app context."""
        def __call__(self, *args, **kwargs):
            try:
                with app.app_context():
                    return self.run(*args, **kwargs)
            except Exception as e:
                logging.error(f"❌ Celery Task Error: {e}")
                raise

    celery.Task = ContextTask
