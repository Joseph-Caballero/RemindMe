from flask import Flask

app = Flask(__name__)

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