from flask import Flask, render_template_string, jsonify, request
import threading
import time
import json
import os

app = Flask(__name__)
status_file = "approval_status.json"
lock = threading.Lock()

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
        return render_template_string(expired_template())
    save_status("approved", pipeline_id, reason)
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string(success_template("approved", reason))

@app.route('/reject', methods=['POST'])
def reject():
    pipeline_id = request.args.get("pipeline_id", "")
    reason = request.form.get("reason", "Rejected without comment")
    current = load_status()
    if pipeline_id != current.get("pipeline_id", ""):
        return render_template_string(expired_template())
    save_status("rejected", pipeline_id, reason)
    threading.Timer(300.0, lambda: save_status("pending", pipeline_id)).start()
    return render_template_string(success_template("rejected", reason))

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
        return render_template_string(expired_template())

    return render_template_string(review_template(pipeline_id))

def expired_template():
    return """
    <html>
    <head><title>Link Expired</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #ffe6e6;
            text-align: center;
            padding: 100px;
        }}
        .card {{
            background: white;
            padding: 30px;
            margin: auto;
            width: 400px;
            box-shadow: 0px 4px 10px rgba(255, 0, 0, 0.3);
            border-radius: 12px;
            border: 2px solid #ff4d4d;
        }}
        h2 {{
            color: #d32f2f;
        }}
    </style>
    </head>
    <body>
        <div class="card">
            <h2>⚠️ Link Expired</h2>
            <p>The approval link you used is no longer valid.</p>
        </div>
    </body>
    </html>
    """

def success_template(status, reason):
    color = "#2e7d32" if status == "approved" else "#c62828"
    title = "🎉 Approval Confirmed" if status == "approved" else "❌ Rejection Recorded"
    return f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{
                background-color: #f0f4f8;
                font-family: 'Segoe UI', sans-serif;
                text-align: center;
                padding: 100px;
            }}
            .card {{
                background: white;
                padding: 30px;
                width: 450px;
                margin: auto;
                box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
                border-radius: 12px;
            }}
            h2 {{
                color: {color};
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>{title}</h2>
            <p>The pipeline was <strong>{status}</strong> for the following reason:</p>
            <blockquote>{reason}</blockquote>
        </div>
    </body>
    </html>
    """

def review_template(pipeline_id):
    return f"""
    <html>
    <head>
        <title>Review Pipeline</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background-color: #f9fbfd;
                text-align: center;
                padding: 60px;
            }}
            .card {{
                background: #fff;
                padding: 30px;
                margin: auto;
                width: 520px;
                box-shadow: 0px 5px 15px rgba(0,0,0,0.1);
                border-radius: 16px;
            }}
            button {{
                padding: 10px 25px;
                font-size: 16px;
                margin: 10px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }}
            .approve-btn {{ background-color: #28a745; color: white; }}
            .reject-btn {{ background-color: #dc3545; color: white; }}
            .submit-btn {{ padding: 12px 30px; margin-top: 15px; }}
            textarea {{
                width: 90%;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                margin-top: 10px;
            }}
        </style>
        <script>
            function showForm(type) {{
                document.getElementById('approve-form').style.display = 'none';
                document.getElementById('reject-form').style.display = 'none';
                document.getElementById(type + '-form').style.display = 'block';
            }}
        </script>
    </head>
    <body>
        <div class="card">
            <h2 style="color: #0d6efd;">🔍 Review Pipeline Request</h2>
            <p>Choose to approve or reject the pipeline:</p>

            <button class="approve-btn" onclick="showForm('approve')">✅ Approve</button>
            <button class="reject-btn" onclick="showForm('reject')">❌ Reject</button>

            <div id="approve-form" style="display:none;">
                <form method="post" action="/approve?pipeline_id={pipeline_id}">
                    <textarea name="reason" rows="4" placeholder="Reason for approval..." required></textarea><br>
                    <button type="submit" class="submit-btn approve-btn">Submit Approval</button>
                </form>
            </div>

            <div id="reject-form" style="display:none;">
                <form method="post" action="/reject?pipeline_id={pipeline_id}">
                    <textarea name="reason" rows="4" placeholder="Reason for rejection..." required></textarea><br>
                    <button type="submit" class="submit-btn reject-btn">Submit Rejection</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    save_status("pending", "")
    app.run(host="0.0.0.0", port=5000)
