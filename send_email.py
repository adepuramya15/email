import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
import sys
import uuid

# === CONFIGURATION ===
smtp_user = "yaswanthkumarch2001@gmail.com"
smtp_password = "uqjcbszfdjfwbsor"  # Use Gmail App Password (no spaces)
to_email = "ramya@middlewaretalents.com"
public_url = "https://dfa3-136-232-205-158.ngrok-free.app"  # Your Flask app ngrok URL

# === Generate unique pipeline ID ===
pipeline_id = str(uuid.uuid4())

# Flask endpoint URLs with pipeline_id query param
status_url = f"{public_url}/status?pipeline_id={pipeline_id}"
approve_url = f"{public_url}/approve?pipeline_id={pipeline_id}"
reject_url = f"{public_url}/reject?pipeline_id={pipeline_id}"
reset_url = f"{public_url}/reset?pipeline_id={pipeline_id}"

# === Reset status for this pipeline ID ===
try:
    requests.post(reset_url)
    print(f"🔄 Status reset to pending for pipeline_id: {pipeline_id}")
except Exception as e:
    print("❌ Failed to reset status:", e)
    sys.exit(1)

# === Compose the email ===
subject = "Action Required: Harness Pipeline Approval"

html_body = f"""
<html>
  <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f8ff; padding: 25px;">
    <div style="max-width: 640px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 35px;">
      <h2 style="color: #4a90e2; text-align: center;">🌟 Approval Needed: Pipeline is on Hold</h2>
      <p style="font-size: 16px; color: #333; line-height: 1.6;">
        Dear Reviewer,<br><br>
        Your input is requested to proceed with a pipeline task.<br>
        Kindly select one of the actions below to continue.
      </p>

      <div style="text-align: center; margin: 35px 0;">
        <a href="{approve_url}" 
           style="display: inline-block; padding: 14px 30px; background-color: #00c853; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; margin: 0 10px; font-weight: 600;">
          ✅ Approve
        </a>
        <a href="{reject_url}" 
           style="display: inline-block; padding: 14px 30px; background-color: #d50000; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; margin: 0 10px; font-weight: 600;">
          ❌ Reject
        </a>
      </div>

      <p style="font-size: 14px; color: #666; text-align: center;">
        If no action is taken within 10 minutes, the request will timeout automatically.<br><br>
        <strong>– Automated CI/CD Notification System</strong>
      </p>
    </div>
  </body>
</html>
"""


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

# === Poll for Approval ===
print(f"⏳ Waiting for approval (pipeline_id: {pipeline_id}) (10 minutes max)...")
for i in range(60):  # Poll every 10 seconds (60 × 10s = 10 min)
    try:
        res = requests.get(status_url)
        res.raise_for_status()
        data = res.json()
        status = data.get("status", "").lower()

        if status in ["approved", "rejected"]:
            print(f"🔔 Pipeline {status.upper()} received for ID {pipeline_id}.")

            # Reset again after response
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

# Timeout after 10 minutes
print("⌛ Timeout reached. No approval received.")
sys.exit(1)
