from flask import Flask, g, request
from .db import SessionLocal, init_db
from .models import Reminder

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

@app.route("/health")
def health():
    return {
        "status": 200
    }

@app.errorhandler(404)
def page_not_found(error):
    return {
        "status": 404
    }