from flask import Flask, request
import json
import os

app = Flask(__name__)
STATUS_FILE = "approval_status.json"

def update_status(pipeline_id, new_status):
    data = {
        "pipeline_id": pipeline_id,
        "status": new_status
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Updated status to {new_status} for pipeline_id={pipeline_id}")

@app.route("/approve")
def approve():
    pipeline_id = request.args.get("pipeline_id")
    update_status(pipeline_id, "approved")
    return f"<h2>You approved pipeline ID {pipeline_id}</h2>"

@app.route("/reject")
def reject():
    pipeline_id = request.args.get("pipeline_id")
    update_status(pipeline_id, "rejected")
    return f"<h2>You rejected pipeline ID {pipeline_id}</h2>"

if __name__ == "__main__":
    # Must bind to 0.0.0.0 for ngrok to reach it
    app.run(host="0.0.0.0", port=5000)
