from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Reminder

@celery_app.task(name="mark_reminder_sent")
def mark_reminder_sent(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = db.get(Reminder, reminder_id)
        
        if not reminder:
            print(f"Reminder {reminder_id} not found")
            return {"status": "error", "message": "Reminder not found"}
        
        reminder.sent = True
        db.commit()
        
        print(f"Marked reminder {reminder_id} as sent!")
        return {"status": "success", "reminder_id": reminder_id}
    except Exception as e:
        db.rollback()
        print(f"Error marking reminder as sent: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()