from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Reminder
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_reminder_email(reminder: Reminder):
    mailgun_api_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    from_email = f"RemindMe <postmaster@{mailgun_domain}>"
    
    if not mailgun_api_key:
        raise ValueError("MAILGUN_API_KEY environment variable is not set")

    if not mailgun_domain:
        raise ValueError("MAILGUN_DOMAIN environment variable is not set")
    
    url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
    
    response = requests.post(
        url,
        auth=("api", mailgun_api_key),
        data={
            "from": from_email,
            "to": reminder.email,
            "subject": f"Reminder: {reminder.title}",
            "text": reminder.title
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Mailgun API error: {response.status_code} - {response.text}")
    
    return response.json()

@celery_app.task(name="mark_reminder_sent")
def mark_reminder_sent(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = db.get(Reminder, reminder_id)
        
        if not reminder:
            print(f"Reminder {reminder_id} not found")
            return {"status": "error", "message": "Reminder not found"}
        
        try:
            send_reminder_email(reminder)
            print(f"Email sent successfully for reminder {reminder_id} to {reminder.email}")
        except Exception as e:
            print(f"Error sending email for reminder {reminder_id}: {e}")
        
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