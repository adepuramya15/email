from flask import Flask, request, jsonify, abort
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
    app.logger.info(f"Updated status to '{new_status}' for pipeline_id={pipeline_id}")

@app.route("/approve")
def approve():
    pipeline_id = request.args.get("pipeline_id")
    if not pipeline_id:
        return jsonify({"error": "Missing pipeline_id"}), 400

    update_status(pipeline_id, "approved")
    return f"""
    <html>
        <body>
            <h2>You approved pipeline ID {pipeline_id}</h2>
            <p>You can now return to the pipeline system.</p>
        </body>
    </html>
    """

@app.route("/reject")
def reject():
    pipeline_id = request.args.get("pipeline_id")
    if not pipeline_id:
        return jsonify({"error": "Missing pipeline_id"}), 400

    update_status(pipeline_id, "rejected")
    return f"""
    <html>
        <body>
            <h2>You rejected pipeline ID {pipeline_id}</h2>
            <p>You can now return to the pipeline system.</p>
        </body>
    </html>
    """

@app.route("/status")
def status():
    # Optional: API to check current status
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Status not found"}), 404

if __name__ == "__main__":
    # Bind to all IPs so ngrok or external services can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
