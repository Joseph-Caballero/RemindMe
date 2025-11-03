import os
from dotenv import load_dotenv

load_dotenv()

USE_CELERY = os.getenv("USE_CELERY", "False") == "True"

if USE_CELERY:
    from celery import Celery
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise ValueError("REDIS_URL is required when USE_CELERY=true")
    
    celery_app = Celery(
        "remindme", 
        broker=redis_url, 
    )
    
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_ignore_result=True,
        broker_connection_retry_on_startup=True,
    )
    

    from app import tasks
else:
    celery_app = None

celery = celery_app