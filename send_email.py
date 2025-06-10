import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
import sys
import uuid

# === CONFIGURATION ===
smtp_user = "yaswanthkumarch2001@gmail.com"
smtp_password = "uqjcbszfdjfwbsor"  # Gmail App Password
to_email = "ramya@middlewaretalents.com"
public_url = "https://3f41-136-232-205-158.ngrok-free.app"  # Flask public URL
timeout_minutes = 10
poll_interval = 10  # in seconds

# === Generate unique pipeline ID ===
pipeline_id = str(uuid.uuid4())
print(f"🔐 Generated pipeline_id: {pipeline_id}")

# === Construct URLs ===
status_url = f"{public_url}/status?pipeline_id={pipeline_id}"
reset_url = f"{public_url}/reset?pipeline_id={pipeline_id}"
review_url = f"{public_url}/review?pipeline_id={pipeline_id}"

# === Reset status ===
try:
    requests.post(reset_url)
    print(f"🧹 Status reset to pending for pipeline_id: {pipeline_id}")
except Exception as e:
    print("❌ Error resetting status:", e)
    sys.exit(1)

# === Compose Email ===
subject = "🚀 Action Required: Pipeline Approval Needed"

html_body = f"""
<html>
  <body style="font-family: 'Segoe UI', sans-serif; background-color: #f0f4f8; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background: white; border-radius: 12px; padding: 35px; box-shadow: 0 8px 20px rgba(0,0,0,0.1);">
      <h2 style="color: #1a73e8; text-align: center;">🔧 Pipeline Approval Required</h2>
      <p style="font-size: 15px; color: #333;">
        Hello,<br><br>
        A CI/CD pipeline is awaiting your review. Please click the button below to approve or reject it.
      </p>
      <div style="text-align: center; margin: 30px 0;">
        <a href="{review_url}"
           style="display: inline-block; padding: 12px 28px; background-color: #6f42c1; color: white; text-decoration: none;
                  border-radius: 8px; font-size: 16px; font-weight: 600;">
          🔎 Review Request
        </a>
      </div>
      <p style="font-size: 13px; color: #888; text-align: center;">
        This link is valid for a one-time review.<br>
        Please respond within {timeout_minutes} minutes.
      </p>
      <hr style="margin-top: 20px;">
      <p style="font-size: 13px; color: #aaa; text-align: center;">
        – CI/CD Notification System
      </p>
    </div>
  </body>
</html>
"""

# === Send Email ===
msg = MIMEMultipart('alternative')
msg['From'] = smtp_user
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(html_body, 'html'))

try:
    print("📧 Sending email...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.quit()
    print("✅ Email successfully sent to:", to_email)
except Exception as e:
    print("❌ Failed to send email:", e)
    sys.exit(1)

# === Poll for Approval Status ===
print(f"⏳ Waiting for approval (pipeline_id: {pipeline_id})")
polls = int((timeout_minutes * 60) / poll_interval)

for i in range(polls):
    try:
        res = requests.get(status_url)
        res.raise_for_status()
        data = res.json()
        status = data.get("status", "").lower()
        reason = data.get("reason", "No reason provided")

        if status in ["approved", "rejected"]:
            print(f"\n🔔 Pipeline {status.upper()} received for ID {pipeline_id}")
            print(f"📄 Reason: {reason}")

            # Reset status after response
            try:
                requests.post(reset_url)
                print("🔄 Status reset to pending.")
            except Exception as e:
                print("⚠️ Failed to reset after response:", e)

            if status == "approved":
                print("✅ Proceeding with deployment...")
                sys.exit(0)
            else:
                print("🛑 Pipeline was rejected.")
                sys.exit(1)

        print(f"⌛ Poll {i+1}/{polls}: Waiting for response...")
    except Exception as err:
        print(f"🔁 Poll {i+1}/{polls} failed: {err}")

    time.sleep(poll_interval)

# === Timeout ===
print("\n⌛ Timeout reached. No approval received.")
sys.exit(1)
