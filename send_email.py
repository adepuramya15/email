import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials and settings
sender_email = "yaswanthkumarch2001@gmail.com"
receiver_email = "ramya@middlewaretalents.com"
password = "uqjc bszf djfw bsor"  # Use Gmail App Password

subject = "Harness Approval Needed"

# Pipeline and endpoint URLs
pipeline_id = "123"
base_url = "https://64ef-136-232-205-158.ngrok-free.app"
approve_url = f"{base_url}/approve?pipeline_id={pipeline_id}"
reject_url = f"{base_url}/reject?pipeline_id={pipeline_id}"

# Save initial status as "pending" in a JSON file
status_data = {
    "pipeline_id": pipeline_id,
    "status": "pending"
}
with open("approval_status.json", "w") as f:
    json.dump(status_data, f, indent=2)

# HTML content with buttons and status
html_body = f"""
<html>
  <body>
    <p>Hi,<br><br>
       Please approve the pending pipeline run in Harness.<br><br>
       <b>Status:</b> Pending<br><br>
       <a href="{approve_url}" style="
         background-color: #4CAF50;
         color: white;
         padding: 10px 20px;
         text-align: center;
         text-decoration: none;
         display: inline-block;
         font-size: 16px;
         margin-right: 10px;
         border-radius: 5px;">Approve</a>
       <a href="{reject_url}" style="
         background-color: #f44336;
         color: white;
         padding: 10px 20px;
         text-align: center;
         text-decoration: none;
         display: inline-block;
         font-size: 16px;
         border-radius: 5px;">Reject</a><br><br>
       Thanks.
    </p>
  </body>
</html>
"""

# Build email
message = MIMEMultipart("alternative")
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(html_body, "html"))

# Send the email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
