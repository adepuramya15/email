import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email settings
sender_email = "yaswanthkumarch2001@gmail.com"
receiver_email = "ramya@middlewaretalents.com"
password = "uqjc bszf djfw bsor"
pipeline_id = "123"
status_file = "approval_status.json"
base_url = "https://64ef-136-232-205-158.ngrok-free.app"

# Set initial status
status_data = {"pipeline_id": pipeline_id, "status": "pending"}
with open(status_file, "w") as f:
    json.dump(status_data, f, indent=2)

# Generate links
approve_url = f"{base_url}/approve?pipeline_id={pipeline_id}"
reject_url = f"{base_url}/reject?pipeline_id={pipeline_id}"

# Build email
subject = "Harness Approval Needed"
html_body = f"""
<html><body>
<p>Hi,<br><br>
Status: <b>Pending</b><br><br>
<a href="{approve_url}" style="background:#4CAF50;color:white;padding:10px 20px;border-radius:5px;">Approve</a>
<a href="{reject_url}" style="background:#f44336;color:white;padding:10px 20px;border-radius:5px;">Reject</a><br><br>
Thanks.
</p></body></html>
"""

message = MIMEMultipart("alternative")
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(html_body, "html"))

# Send email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    print("Email sent.")
except Exception as e:
    print(f"Failed to send email: {e}")
    exit(1)

# Wait for approval or rejection
print("Waiting for user action...")
start_time = time.time()
timeout = 120  # 2 minutes max wait

while time.time() - start_time < timeout:
    with open(status_file) as f:
        status = json.load(f).get("status")
        if status in ["approved", "rejected"]:
            print(f"Status received: {status}")
            break
    time.sleep(5)
else:
    print("No response received. Timeout.")

# Reset back to pending after 2 minutes
print("Resetting status to pending after 2 minutes...")
time.sleep(120)
with open(status_file, "w") as f:
    json.dump({"pipeline_id": pipeline_id, "status": "pending"}, f, indent=2)
print("Status reset to pending.")
