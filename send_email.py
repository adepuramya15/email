import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

# Configurations
sender_email = "yaswanthkumarch2001@gmail.com"
receiver_email = "ramya@middlewaretalents.com"
password = "uqjc bszf djfw bsor"  # App Password only
pipeline_id = "123"
status_file = "approval_status.json"
base_url = "https://64ef-136-232-205-158.ngrok-free.app"
timeout = 120  # 2 minutes wait for approval

# Step 1: Write initial status
status_data = {"pipeline_id": pipeline_id, "status": "pending"}
with open(status_file, "w") as f:
    json.dump(status_data, f, indent=2)

# Step 2: Email content with approval/rejection buttons
approve_url = f"{base_url}/approve?pipeline_id={pipeline_id}"
reject_url = f"{base_url}/reject?pipeline_id={pipeline_id}"

plain_text = f"""
Pipeline Approval Needed

Status: Pending

Click below to respond:

Approve: {approve_url}
Reject: {reject_url}
"""

html_body = f"""
<html>
  <body>
    <p>Hi,<br><br>
       Please approve the pending pipeline run.<br><br>
       <b>Status:</b> Pending<br><br>
       <a href="{approve_url}" style="
         background-color: #4CAF50;
         color: white;
         padding: 10px 20px;
         text-decoration: none;
         border-radius: 5px;">Approve</a>&nbsp;&nbsp;
       <a href="{reject_url}" style="
         background-color: #f44336;
         color: white;
         padding: 10px 20px;
         text-decoration: none;
         border-radius: 5px;">Reject</a><br><br>
       Thanks.
    </p>
  </body>
</html>
"""

# Step 3: Send Email
message = MIMEMultipart("alternative")
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Harness Approval Needed"
message.attach(MIMEText(plain_text, "plain"))
message.attach(MIMEText(html_body, "html"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    sys.exit(1)

# Step 4: Wait for approval/rejection
print("⏳ Waiting for user action (up to 2 minutes)...")
start_time = time.time()
final_status = "pending"

while time.time() - start_time < timeout:
    try:
        with open(status_file) as f:
            current_status = json.load(f).get("status", "pending")
        if current_status in ["approved", "rejected"]:
            print(f"✅ Status received: {current_status.upper()}")
            final_status = current_status
            break
    except Exception as e:
        print(f"⚠️ Warning reading status: {e}")
    time.sleep(5)

if final_status == "pending":
    print("⚠️ No response received within 2 minutes. Timeout.")
    sys.exit(2)  # Exit with code 2 on timeout

# Step 5: Exit based on approval status
if final_status == "approved":
    print("✅ Approval granted. Proceeding.")
    sys.exit(0)  # Success exit code
elif final_status == "rejected":
    print("❌ Approval rejected. Exiting with failure.")
    sys.exit(3)  # Failure exit code

# Optional: Reset status after 2 mins if needed (can remove this if not required)
#print("⏳ Waiting 2 minutes before resetting status...")
#time.sleep(120)
#with open(status_file, "w") as f:
#    json.dump({"pipeline_id": pipeline_id, "status": "pending"}, f, indent=2)
#print("🔄 Status reset to 'pending'.")
