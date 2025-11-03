from flask import Flask, g, render_template, request, jsonify
from app.db import SessionLocal, init_db
from app.models import Reminder
from app.scheduler import schedule_reminder
from app.tasks import process_reminder
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

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

    schedule_reminder(row.id, due_at)

    return {"id": row.id, "due_at": due_at.isoformat()}, 201

@app.post("/webhook/qstash/reminder")
def qstash_webhook():
    qstash_current_signing_key = os.getenv("QSTASH_CURRENT_SIGNING_KEY")
    if qstash_current_signing_key:
        try:
            from qstash import verify_signature
            
            signature = request.headers.get("Upstash-Signature")
            body = request.get_data()
            
            if not signature or not verify_signature(
                signature=signature,
                body=body,
                signing_key=qstash_current_signing_key
            ):
                print("Invalid QStash signature")
                return jsonify({"error": "Invalid signature"}), 401
        except ImportError:
            print("Warning: qstash not available for signature verification")
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return jsonify({"error": "Signature verification failed"}), 401
    
    try:
        data = request.get_json(force=True)
        reminder_id = data.get("reminder_id")
        
        if not reminder_id:
            return jsonify({"error": "reminder_id is required"}), 400
        
        result = process_reminder(int(reminder_id))
        
        if result.get("status") == "success":
            return jsonify(result), 200
        elif result.get("status") == "skipped":
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        print(f"Error processing QStash webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return {"status":"ok"}, 200

@app.errorhandler(404)
def page_not_found(error):
    return {"status": "404"}, 404