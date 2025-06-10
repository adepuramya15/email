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
    return {"status": "pending", "pipeline_id": "", "reason": ""}

def save_status(new_status, pipeline_id=None, reason=""):
    with lock:
        try:
            status_data = {
                "status": new_status,
                "reason": reason
            }
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
    return "🟢 Approval system is active and awaiting instructions."

@app.route('/approve', methods=['POST'])
def approve():
    pipeline_id = request.args.get("pipeline_id", "")
    reason = request.form.get("reason", "Approved without comment")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string("""
            <h2 style="color: #ff9800;">⚠️ Invalid or Expired Approval</h2>
            <p>This approval link has either expired or does not match the current request.</p>
        """)
    save_status("approved", pipeline_id, reason)
    print("🔔 Approved. Will reset to pending in 5 minutes...")
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string("""
        <h2 style="color: #2e7d32;">🎉 Approval Confirmed</h2>
        <p>The pipeline has been approved with reason: {{ reason }}</p>
    """, reason=reason)

@app.route('/reject', methods=['POST'])
def reject():
    pipeline_id = request.args.get("pipeline_id", "")
    reason = request.form.get("reason", "Rejected without comment")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string("""
            <h2 style="color: #ff9800;">⚠️ Invalid or Expired Rejection</h2>
            <p>This rejection link has either expired or is no longer valid.</p>
        """)
    save_status("rejected", pipeline_id, reason)
    print("❌ Rejected. Will reset to pending in 5 minutes...")
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string("""
        <h2 style="color: #c62828;">❌ Rejection Recorded</h2>
        <p>The pipeline has been rejected with reason: {{ reason }}</p>
    """, reason=reason)

@app.route('/status')
def status():
    expected_id = request.args.get("pipeline_id", "")
    current = load_status()
    if current.get("pipeline_id", "") != expected_id:
        return jsonify({"status": "pending", "reason": ""})
    return jsonify({"status": current["status"], "reason": current.get("reason", "")})

@app.route('/reset', methods=['POST'])
def reset():
    pipeline_id = request.args.get("pipeline_id", "")
    save_status("pending", pipeline_id, "")
    return "🔁 Pipeline status reset to pending.", 200

@app.route('/review')
def review():
    pipeline_id = request.args.get("pipeline_id", "")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string("""
            <h2 style="color: #ff9800;">⚠️ Invalid or Expired Link</h2>
            <p>This review link is invalid or expired.</p>
        """)

    approve_action = f"/approve?pipeline_id={pipeline_id}"
    reject_action = f"/reject?pipeline_id={pipeline_id}"

    return render_template_string(f"""
        <html>
        <body style="font-family: sans-serif; text-align: center; padding: 40px;">
            <h2 style="color: #4a90e2;">Review Required for Pipeline</h2>
            <form method="post" action="{approve_action}" style="margin-bottom: 20px;">
                <textarea name="reason" rows="4" cols="50" placeholder="Enter reason for approval..." required></textarea><br><br>
                <button type="submit" style="padding: 12px 24px; background-color: #00c853; color: white; border: none; border-radius: 5px; font-size: 16px;">✅ Approve</button>
            </form>
            <form method="post" action="{reject_action}">
                <textarea name="reason" rows="4" cols="50" placeholder="Enter reason for rejection..." required></textarea><br><br>
                <button type="submit" style="padding: 12px 24px; background-color: #d50000; color: white; border: none; border-radius: 5px; font-size: 16px;">❌ Reject</button>
            </form>
        </body>
        </html>
    """)

if __name__ == "__main__":
    save_status("pending", "")
    app.run(host="0.0.0.0", port=5000)
