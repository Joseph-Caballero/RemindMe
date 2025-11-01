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

@app.get("/reminders/all")
def get_all_reminders():
    reminders = g.db.query(Reminder).order_by(Reminder.due_at.desc()).all()

    if len(reminders) == 0:
        return {"error": "You currently have no reminders"}

    response = []

    for reminder in reminders:
        response.append({
            "id": reminder.id,
            "title": reminder.title,
            "due_at": reminder.due_at.isoformat() if reminder.due_at else None,
            "sent": reminder.sent
        })
    
    return response, 200

@app.patch("/reminders/<int:rid>")
def update_reminder(rid: int):
    data = request.get_json(force=True)
    r = g.db.get(Reminder, rid)
    if not r:
        return {"error": "not found"}, 404

    due_at_changed = False

    if "title" in data:
        r.title = data["title"]

    if "due_at" in data:
        old_due_at = r.due_at

        try:
            new_due_at = datetime.fromisoformat(data["due_at"])
        except ValueError:
            return {"error": "invalid due_at format"}, 400

        if new_due_at != old_due_at:
            r.due_at = new_due_at
            due_at_changed = True

    g.db.commit()

    return {"ok": True, "due_at_changed": due_at_changed}, 200

@app.delete("/reminder/<int:rid>")
def delete_reminder(rid: int):
    r = g.db.get(Reminder, rid)
    if not r:
        return {"error": "not found"}, 404
    
    g.db.delete(r)
    g.db.commit()
    return {"ok": True, "deleted_id": rid}, 200

@app.route("/health")
def health():
    return {"status":"ok"}, 200

@app.errorhandler(404)
def page_not_found(error):
    return {"status": "404"}, 404