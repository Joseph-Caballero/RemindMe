import os
import json
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

USE_CELERY = os.getenv("USE_CELERY", "False") == "True"

def schedule_reminder(reminder_id: int, due_at: datetime):

    if USE_CELERY:
        return _schedule_with_celery(reminder_id, due_at)
    else:
        return _schedule_with_qstash(reminder_id, due_at)

def _schedule_with_celery(reminder_id: int, due_at: datetime):

    from app.tasks import mark_reminder_sent
    
    now = datetime.now(timezone.utc)
    
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)
    
    if due_at <= now:
        mark_reminder_sent.apply_async(args=[reminder_id])
    else:
        mark_reminder_sent.apply_async(args=[reminder_id], eta=due_at)
    
    return {"scheduler": "celery", "reminder_id": reminder_id, "due_at": due_at.isoformat()}

def _schedule_with_qstash(reminder_id: int, due_at: datetime):
    from qstash import QStash
    
    qstash_token = os.getenv("QSTASH_TOKEN")
    if not qstash_token:
        raise ValueError("QSTASH_TOKEN environment variable is not set (required for QStash scheduling)")
    
    app_url = os.getenv("APP_URL")
    if not app_url:
        raise ValueError("APP_URL environment variable is not set (required for QStash webhook URL)")
    
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)
    else:
        due_at = due_at.astimezone(timezone.utc)
    
    webhook_url = f"{app_url.rstrip('/')}/webhook/qstash/reminder"
    
    client = QStash(qstash_token)
    
    now = datetime.now(timezone.utc)
    delay_seconds = int((due_at - now).total_seconds())
    
    body_json = json.dumps({"reminder_id": reminder_id})
    
    if delay_seconds <= 0:
        client.message.publish(
            url=webhook_url,
            body=body_json,
            headers={"Content-Type": "application/json"},
            content_type="application/json"
        )
    else:
        client.message.publish(
            url=webhook_url,
            body=body_json,
            headers={"Content-Type": "application/json"},
            content_type="application/json",
            delay=f"{delay_seconds}s"
        )
    
    return {"scheduler": "qstash", "reminder_id": reminder_id, "due_at": due_at.isoformat()}

