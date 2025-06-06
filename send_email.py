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
public_url = "https://64ef-136-232-205-158.ngrok-free.app"  # Your Flask app ngrok URL

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
subject = "Harness Pipeline Approval Needed"
html_body = f"""
<html>
  <body style="font-family: Arial;">
    <p>Hi,<br><br>
       Please review and take action on the pipeline.<br><br>
       <a href="{approve_url}" style="padding: 10px 20px; background-color: green; color: white; text-decoration: none;">Approve</a>
       &nbsp;
       <a href="{reject_url}" style="padding: 10px 20px; background-color: red; color: white; text-decoration: none;">Reject</a><br><br>
       Thanks,<br>CI Bot
    </p>
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
sys.exit(0)
