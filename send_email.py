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

# === Generate unique pipeline ID ===
pipeline_id = str(uuid.uuid4())

# === Construct endpoint URLs ===
status_url = f"{public_url}/status?pipeline_id={pipeline_id}"
reset_url = f"{public_url}/reset?pipeline_id={pipeline_id}"
approve_url = f"{public_url}/approve?pipeline_id={pipeline_id}"
reject_url = f"{public_url}/reject?pipeline_id={pipeline_id}"

# === Reset status ===
try:
    requests.post(reset_url)
    print(f"🔄 Status reset to pending for pipeline_id: {pipeline_id}")
except Exception as e:
    print("❌ Failed to reset status:", e)
    sys.exit(1)

# === Compose the colorful HTML Email with Approve/Reject buttons ===
subject = "🚀 Action Required: Pipeline Approval Needed"

html_body = f"""
<html>
  <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f9fbfc; padding: 20px;">
    <div style="max-width: 650px; margin: auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1); padding: 35px;">
      <h2 style="color: #0d6efd; text-align: center;">🧪 Review & Approve Pipeline Task</h2>
      <p style="font-size: 16px; color: #333333; line-height: 1.5;">
        Hello Reviewer,<br><br>
        A pipeline task requires your attention.<br>
        Please choose one of the options below to approve or reject with feedback.
      </p>

      <div style="text-align: center; margin: 30px 0;">
        <a href="{approve_url}" 
           style="margin-right: 15px; display: inline-block; padding: 14px 28px; background-color: #28a745; color: white; text-decoration: none; border-radius: 8px; font-size: 16px;">
          ✅ Approve
        </a>

        <a href="{reject_url}" 
           style="display: inline-block; padding: 14px 28px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 8px; font-size: 16px;">
          ❌ Reject
        </a>
      </div>

      <p style="font-size: 14px; color: #888888; text-align: center;">
        This request will expire after the first response is submitted.<br>
        <strong>– CI/CD Notification System</strong>
      </p>
    </div>
  </body>
</html>
"""

# === Build Email Message ===
msg = MIMEMultipart('alternative')
msg['From'] = smtp_user
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(html_body, 'html'))

# === Send Email ===
try:
    print("📧 Sending email...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, to_email, msg.as_string())
    server.quit()
    print("✅ Email sent.")
except Exception as e:
    print("❌ Failed to send email:", e)
    sys.exit(1)

# === Poll for Approval Status ===
print(f"⏳ Waiting for approval (pipeline_id: {pipeline_id}) (10 minutes max)...")
for i in range(60):  # 60 polls × 10 seconds = 10 minutes
    try:
        res = requests.get(status_url)
        res.raise_for_status()
        data = res.json()
        status = data.get("status", "").lower()
        reason = data.get("reason", "No reason provided")

        if status in ["approved", "rejected"]:
            print(f"🔔 Pipeline {status.upper()} received for ID {pipeline_id}.")
            print(f"📄 Reason: {reason}")

            try:
                requests.post(reset_url)
                print("🔄 Status reset to pending.")
            except Exception as e:
                print("⚠️ Failed to reset after response:", e)

            if status == "approved":
                print("✅ Proceeding with pipeline...")
                sys.exit(0)
            else:
                print("🛑 Pipeline rejected.")
                sys.exit(1)
        else:
            print(f"⌛ Current status: {status}. Waiting...")
    except Exception as err:
        print(f"🔁 Poll {i+1}/60 failed:", err)

    time.sleep(10)

# Timeout handling
print("⌛ Timeout reached. No approval received.")
sys.exit(1)
