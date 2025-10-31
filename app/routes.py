from flask import Flask, g, request
from db import SessionLocal, init_db
from models import Reminder
from datetime import datetime, timedelta

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

@app.post("/reminders")
def createReminder():
    data = request.get_json(force=True)
    now = datetime.utcnow()

    if "due_in" in data:
        due_at = now + timedelta(minutes=int(data["due_in"]))
    else:
        due_at = datetime.fromisoformat(data["due_at"])
    
    row = Reminder(title = data["title"], due_at = due_at)
    g.db.add(row)
    g.db.commit()
    g.db.refresh(row)

    return {"id": row.id, "due_at": due_at.isoformat()}, 201

@app.get("/reminders/<int:rid>")
def getReminder(rid: int):
    print(f"************ rid: {rid}")
    row = g.db.get(Reminder, rid)
    if not row:
        return {"error": "not found"}, 404
    return {
        "id": row.id,
        "title": row.title,
        "due_at": row.due_at.isoformat(),
        "sent": row.sent,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None
    }, 200


@app.route("/health")
def health():
    return {"status":"ok"}, 200

@app.errorhandler(404)
def page_not_found(error):
    return {"status": "404"}, 404