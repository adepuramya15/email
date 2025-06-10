import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
import sys
import uuid

# === CONFIGURATION ===
smtp_user = "yaswanthkumarch2001@gmail.com"
smtp_password = "uqjcbszfdjfwbsor"  # Use Gmail App Password
to_email = "ramya@middlewaretalents.com"
public_url = "https://3f41-136-232-205-158.ngrok-free.app"  # Your Flask app public URL

# === Generate unique pipeline ID ===
pipeline_id = str(uuid.uuid4())

# === Construct endpoint URLs ===
status_url = f"{public_url}/status?pipeline_id={pipeline_id}"
reset_url = f"{public_url}/reset?pipeline_id={pipeline_id}"
review_url = f"{public_url}/review?pipeline_id={pipeline_id}"

# === Reset status for this pipeline ID ===
try:
    requests.post(reset_url)
    print(f"🔄 Status reset to pending for pipeline_id: {pipeline_id}")
except Exception as e:
    print("❌ Failed to reset status:", e)
    sys.exit(1)

# === Compose the HTML Email ===
subject = "Action Required: Pipeline Review Needed"

html_body = f"""
<html>
  <body style="font-family: Arial; background-color: #f0f8ff; padding: 25px;">
    <div style="max-width: 640px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 35px;">
      <h2 style="color: #4a90e2; text-align: center;">🔍 Review Pipeline Request</h2>
      <p style="font-size: 16px; color: #333; line-height: 1.6;">
        Dear Reviewer,<br><br>
        A pipeline task is waiting for your action.<br><br>
        Click the button below to review and take action.
      </p>

      <div style="text-align: center; margin: 35px 0;">
        <a href="{review_url}" 
           style="display: inline-block; padding: 14px 30px; background-color: #007bff; color: white; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: bold;">
          🔗 Review Request
        </a>
      </div>

      <p style="font-size: 14px; color: #666; text-align: center;">
        This link is valid for one request and will expire after use.<br><br>
        <strong>– Automated CI/CD Notification System</strong>
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
for i in range(60):  # Poll every 10 seconds (10 minutes)
    try:
        res = requests.get(status_url)
        res.raise_for_status()
        data = res.json()
        status = data.get("status", "").lower()

        if status in ["approved", "rejected"]:
            print(f"🔔 Pipeline {status.upper()} received for ID {pipeline_id}.")

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
