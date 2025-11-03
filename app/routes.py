from flask import Flask, g, render_template, request
from app.db import SessionLocal, init_db
from app.models import Reminder
from app.tasks import mark_reminder_sent
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

init_db()

@app.before_request
def open_session():
    g.db = SessionLocal()

@app.teardown_request
def close_session(exc):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()

@app.route('/')
def homepage():
    return render_template('index.html')

@app.post("/reminder")
def create_reminder():
    data = request.get_json(force=True)
    now = datetime.now(timezone.utc) 

    due_in_minutes = int(data["due_in"])
    if due_in_minutes not in [1, 3, 5]:
        return {"error": "due_in must be 1, 3, or 5 minutes"}, 400
    due_at = now + timedelta(minutes=due_in_minutes)
    
    row = Reminder(title = data["title"], email = data["email"], due_at = due_at)
    g.db.add(row)
    g.db.commit()
    g.db.refresh(row)

    if due_at <= now:
        mark_reminder_sent.apply_async(args=[row.id])
    else:
        mark_reminder_sent.apply_async(args=[row.id], eta=due_at)

    return {"id": row.id, "due_at": due_at.isoformat()}, 201

@app.route("/health")
def health():
    return {"status":"ok"}, 200

@app.errorhandler(404)
def page_not_found(error):
    return {"status": "404"}, 404