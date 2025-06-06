import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials and settings
sender_email = "yaswanthkumarch2001@gmail.com"
receiver_email = "ramya@middlewaretalents.com"
password = "uqjc bszf djfw bsor"  # Use Gmail App Password

subject = "Harness Approval Needed"

# URLs for approve/reject actions (no leading spaces!)
approve_url = "https://914e-136-232-205-158.ngrok-free.app/approve?pipeline_id=123"
reject_url = "https://914e-136-232-205-158.ngrok-free.app/reject?pipeline_id=123"

# HTML body with buttons
html_body = f"""
<html>
  <body>
    <p>Hi,<br><br>
       Please approve the pending pipeline run in Harness.<br><br>
       <a href="{approve_url}" style="
         background-color: #4CAF50; /* Green */
         color: white;
         padding: 10px 20px;
         text-align: center;
         text-decoration: none;
         display: inline-block;
         font-size: 16px;
         margin-right: 10px;
         border-radius: 5px;
       ">Approve</a>

       <a href="{reject_url}" style="
         background-color: #f44336; /* Red */
         color: white;
         padding: 10px 20px;
         text-align: center;
         text-decoration: none;
         display: inline-block;
         font-size: 16px;
         border-radius: 5px;
       ">Reject</a>
       <br><br>
       Thanks.
    </p>
  </body>
</html>
"""

# Set up the email message
message = MIMEMultipart("alternative")
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# Attach the HTML content to the email
message.attach(MIMEText(html_body, "html"))

# Send the email using Gmail SMTP
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
