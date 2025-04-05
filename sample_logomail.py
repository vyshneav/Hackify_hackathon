import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Email sender & receiver
SMTP_SERVER = "smtp.gmail.com"  # Change for Outlook/Yahoo
SMTP_PORT = 587
SENDER_EMAIL = "nath73065@gmail.com"
SENDER_PASSWORD = "dsbkhypstjzqujhs"
RECEIVER_EMAIL = "vysh7561@gmail.com"

# Accident Details (Modify as needed)
location_lat = "12.9716"
location_lon = "77.5946"
video_link = "https://drive.google.com/sample"

# Create Email
msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = "🚨 SafeDrive Alert: Accident Detected!"

# Attach Company Logo (Inline)
with open("download.jpeg", "rb") as img_file:
    img = MIMEImage(img_file.read())
    img.add_header("Content-ID", "<logo>")  # Referenced in HTML
    msg.attach(img)

# Email Body (HTML)
html_body = f"""\
<html>
  <body>
    <p>
      <img src="cid:logo" width="150"/><br><br>
      🚨 <b>Accident Detected!</b><br>
      📍 <b>Location:</b> {location_lat}, {location_lon} <br>
      🔗 <a href="https://www.google.com/maps/search/?api=1&query={location_lat},{location_lon}">View on Google Maps</a><br>
      🎥 <a href="{video_link}">Surveillance Video</a>
    </p>
  </body>
</html>
"""

msg.attach(MIMEText(html_body, "html"))

# Send Email via SMTP
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Secure Connection
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    print("✅ Email Sent Successfully!")
except Exception as e:
    print(f"❌ Error Sending Email: {e}")
