from flask import Flask, render_template_string, jsonify, request
import threading
import time
import json
import os

app = Flask(__name__)
status_file = "approval_status.json"
lock = threading.Lock()

# === Load or initialize status ===
def load_status():
    if os.path.exists(status_file):
        try:
            with open(status_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read status: {e}")
    return {"status": "pending", "pipeline_id": ""}

def save_status(new_status, pipeline_id=None):
    with lock:
        try:
            status_data = {"status": new_status}
            if pipeline_id is not None:
                status_data["pipeline_id"] = pipeline_id
            else:
                current = load_status()
                status_data["pipeline_id"] = current.get("pipeline_id", "")
            with open(status_file, "w") as f:
                json.dump(status_data, f)
            print(f"🔁 Status updated to: {status_data}")
        except Exception as e:
            print(f"❌ Failed to write status: {e}")

@app.route('/')
def index():
    return "✅ Approval server is running."

@app.route('/approve')
def approve():
    pipeline_id = request.args.get("pipeline_id", "")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string("""
            <h2 style="color: orange;">⚠️ Approval Expired or Invalid</h2>
            <p>This link is no longer valid or has already been used.</p>
        """)
    save_status("approved", pipeline_id)
    print("🔔 Approved. Resetting to pending in 5 minutes...")
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string("""
        <h2 style="color: green;">✅ Pipeline Approved</h2>
        <p>You’re all set! The approval will expire in 5 minutes and reset.</p>
    """)

@app.route('/reject')
def reject():
    pipeline_id = request.args.get("pipeline_id", "")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string("""
            <h2 style="color: orange;">⚠️ Rejection Expired or Invalid</h2>
            <p>This link is no longer valid or has already been used.</p>
        """)
    save_status("rejected", pipeline_id)
    print("❌ Rejected. Resetting to pending in 5 minutes...")
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string("""
        <h2 style="color: red;">❌ Pipeline Rejected</h2>
        <p>You’re all set! The approval will expire in 5 minutes and reset.</p>
    """)

@app.route('/status')
def status():
    expected_id = request.args.get("pipeline_id", "")
    current = load_status()
    if current.get("pipeline_id", "") != expected_id:
        return jsonify({"status": "pending"})
    return jsonify({"status": current["status"]})

@app.route('/reset', methods=['POST'])
def reset():
    pipeline_id = request.args.get("pipeline_id", "")
    save_status("pending", pipeline_id)
    return "🔄 Status manually reset to pending.", 200

if __name__ == "__main__":
    save_status("pending", "")
    app.run(host="0.0.0.0", port=5000)
