from app.db import SessionLocal
from app.models import Reminder
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_reminder_email(reminder: Reminder):
    mailgun_api_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    from_email = f"RemindMeSoon <postmaster@{mailgun_domain}>"
    
    if not mailgun_api_key:
        raise ValueError("MAILGUN_API_KEY environment variable is not set")

    if not mailgun_domain:
        raise ValueError("MAILGUN_DOMAIN environment variable is not set")
    
    url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
    
    # Create a fun email template
    email_text = f"""
    🎉 Reminder Alert! 🎉

    Hey there! This is your friendly reminder:

    ✨ {reminder.title} ✨

    ---
    Sent by RemindMeSoon
    """
    
    response = requests.post(
        url,
        auth=("api", mailgun_api_key),
        data={
            "from": from_email,
            "to": reminder.email,
            "subject": f"Reminder: {reminder.title}",
            "text": email_text.strip()
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Mailgun API error: {response.status_code} - {response.text}")
    
    return response.json()

def process_reminder(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = db.get(Reminder, reminder_id)
        
        if not reminder:
            print(f"Reminder {reminder_id} not found")
            return {"status": "error", "message": "Reminder not found"}
        
        if reminder.sent:
            print(f"Reminder {reminder_id} already sent, skipping")
            return {"status": "skipped", "reminder_id": reminder_id}
        
        try:
            send_reminder_email(reminder)
            print(f"Email sent successfully for reminder {reminder_id} to {reminder.email}")
        except Exception as e:
            raise Exception(f"Error sending email for reminder {reminder_id}: {e}")
        
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

try:
    from app.celery_app import celery_app
    
    if celery_app is not None:
        @celery_app.task(name="mark_reminder_sent")
        def mark_reminder_sent(reminder_id: int):
            return process_reminder(reminder_id)
except (ImportError, AttributeError):
    pass