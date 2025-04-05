import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender's email credentials
SENDER_EMAIL = "nath73065@gmail.com"  # Replace with your sender email
SENDER_PASSWORD = "dsbkhypstjzqujhs"  # Replace with your generated app password

# Receiver email
RECEIVER_EMAIL = "vysh7561@gmail.com"  # Replace with your actual email

# Email content
subject = "Test Email from Python"
body = "This is a test email to verify if the setup is working."

# Setting up email structure
msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Sending email
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)  # Connect to Gmail's SMTP server
    server.starttls()  # Secure the connection
    server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login with credentials
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())  # Send email
    server.quit()  # Close the connection
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
