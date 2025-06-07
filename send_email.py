import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
import sys

# === CONFIGURATION ===
smtp_user = "yaswanthkumarch2001@gmail.com"
smtp_password = "uqjcbszfdjfwbsor"  # Use Gmail App Password (no spaces)
to_email = "ramya@middlewaretalents.com"
public_url = "https://dfa3-136-232-205-158.ngrok-free.app"  # Your Flask app ngrok URL

# Flask endpoint URLs
status_url = f"{public_url}/status"
approve_url = f"{public_url}/approve"
reject_url = f"{public_url}/reject"
reset_url = f"{public_url}/reset"

# === Reset status to "pending" at the beginning ===
try:
    requests.post(reset_url)
    print("🔄 Initial status reset to pending.")
except Exception as e:
    print("❌ Failed to reset status:", e)
    sys.exit(1)

# === Compose the email ===
subject = "Action Required: Harness Pipeline Approval"

html_body = f"""
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px;">
      <h2 style="color: #333333;">🚀 Pipeline Action Required</h2>
      <p style="font-size: 15px; color: #444444;">
        Hello,<br><br>
        A new pipeline execution is waiting for your response.<br>
        Please select one of the options below to continue:
      </p>

      <div style="margin: 30px 0;">
        <a href="{approve_url}" 
           style="padding: 12px 25px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          ✅ Approve
        </a>
        &nbsp;&nbsp;
        <a href="{reject_url}" 
           style="padding: 12px 25px; background-color: #dc3545; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          ❌ Reject
        </a>
      </div>

      <p style="font-size: 14px; color: #666666;">
        Thank you,<br>
        <strong>CI/CD Automation Bot</strong>
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
print("⏳ Waiting for approval (10 minutes max)...")
for i in range(60):  # Poll every 10 seconds (60 × 10s = 10 min)
    try:
        res = requests.get(status_url)
        res.raise_for_status()
        data = res.json()
        status = data.get("status", "").lower()

        if status in ["approved", "rejected"]:
            print(f"🔔 Pipeline {status.upper()} received.")

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
