from celery import Celery
from dotenv import load_dotenv
import os
import platform

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

# Configure Celery
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['core.celery.tasks']
)

# Windows-specific settings
if platform.system() == 'Windows':
    celery_app.conf.update(
        broker_connection_retry_on_startup=True,
        worker_pool_restarts=True,
        worker_pool='solo',  # Use solo pool on Windows
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
else:
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
