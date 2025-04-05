import cv2
import serial
import time
import threading
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 
from datetime import datetime
from collections import deque
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account
from math import radians, sin, cos, sqrt, atan2

# 🔄 Constants & Configurations
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SOUND_THRESHOLD = 100
VIDEO_STORAGE = "recordings/"
PRE_EVENT_DURATION = 10
POST_EVENT_DURATION = 10
FRAME_RATE = 30
BANNER_IMAGE_PATH = "download.jpeg"
BUFFER_SIZE = PRE_EVENT_DURATION * FRAME_RATE
video_buffer = deque(maxlen=BUFFER_SIZE)

# 📍 Predefined Police Station Locations & Emails
predefined_locations = {
    "Police Station 1": {"coords": (12.9716, 77.5946), "email": "vysh7561@gmail.com"},
    "Police Station 2": {"coords": (12.2958, 76.6394), "email": "vyshnavps47@gmail.com"},
    "Police Station 3": {"coords": (12.9081, 77.6515), "email": "vishnu.ps0703@gmail.com"},
}

# 📷 Initialize Camera
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# 🎙️ Initialize Serial Communication
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# 🗂️ Google Drive API Setup
SERVICE_ACCOUNT_FILE = "hackify-cloud-de0a0c13ec0a.json"
FOLDER_ID = "1zX4ACD5cF-uqWlWwujadlz2TMDq8R4tC"

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# ✉️ Email Configuration
SENDER_EMAIL = "nath73065@gmail.com"
SENDER_PASSWORD = "dsbkhypstjzqujhs"

# 📍 Function to Find Nearest Police Station
def haversine(coord1, coord2):
    R = 6371  # Earth radius in km
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c  # Distance in km

def find_nearest_police_station(accident_location):
    nearest = min(predefined_locations, key=lambda loc: haversine(accident_location, predefined_locations[loc]["coords"]))
    return nearest, predefined_locations[nearest]["email"]

# 📤 Function to Send Email to Nearest Police Station
# 📤 Function to Send Email to Nearest Police Station
def send_email(drive_link, nearest_location, police_email, lat, lon):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = police_email
        msg["Subject"] = "🚨 Accident Alert: Video Available"

        # Email Body with HTML Formatting
        body = f"""
        <html>
        <body>
            <img src="cid:company_logo" width="200"><br><br>
            <h2>🚨 Accident Detected Near: {nearest_location}</h2>
            <p><b>📍 Location:</b> {lat}, {lon}</p>
            <p><b>🔗 Google Maps:</b> <a href="https://www.google.com/maps/search/?api=1&query={lat},{lon}">View Location</a></p>
            <p><b>🎥 Video Evidence:</b> <a href="{drive_link}">Watch on Google Drive</a></p>
            <br>
            <p>Please take necessary action immediately.</p>
            <hr>
            <p>Regards, <br> Team SafeDrive</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html"))

        # 📌 Attach Company Logo
        logo_path = "safedrive.jpg"  # Ensure 'logo.png' is available in the working directory
        with open(logo_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header("Content-ID", "<company_logo>")
            img.add_header("Content-Disposition", "inline", filename="safedrive.jpg")
            msg.attach(img)

        # 📧 Send Email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, police_email, msg.as_string())
        server.quit()

        print(f"✅ Alert sent to {nearest_location} ({police_email})!")
    except Exception as e:
        print(f"❌ Email Sending Failed: {e}")

# 🎬 Function to Save 10 Sec Before & After Accident
def save_accident_video():
    event_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(VIDEO_STORAGE, f"accident_{event_timestamp}.mp4")
    print(f"Saving accident video to: {filename}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, FRAME_RATE, (frame_width, frame_height))

    frames_to_save = list(video_buffer)

    print("Writing pre-event frames...")
    for frame in frames_to_save:
        out.write(frame)

    print("Recording post-event frames...")
    for _ in range(POST_EVENT_DURATION * FRAME_RATE):
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    out.release()
    print(f"✅ Accident video saved: {filename}")

    upload_to_drive(filename)

# 📤 Function to Upload Video to Google Drive & Send Email
def upload_to_drive(filepath):
    filename = os.path.basename(filepath)
    file_metadata = {"name": filename, "parents": [FOLDER_ID]}
    media = MediaFileUpload(filepath, mimetype="video/mp4")

    try:
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        file_id = file.get("id")
        drive_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        print(f"🚀 Video uploaded successfully! Link: {drive_link}")

        # 📍 Accident location (Modify to fetch dynamically if needed)
        accident_location = (12.9000, 77.6000)

        # 🔍 Find nearest police station & email
        nearest_location, police_email = find_nearest_police_station(accident_location)

        # 📤 Send Email to nearest police station
        send_email(drive_link, nearest_location, police_email, *accident_location)
    except Exception as e:
        print(f"❌ Upload Error: {e}")

# 🎤 Function to Monitor Sound Sensor & Trigger Accident Event
def monitor_sound():
    while True:
        if ser.in_waiting > 0:
            try:
                sound_data = ser.readline().decode().strip()
                if sound_data.isdigit():
                    sound_level = int(sound_data)
                    print(f"impact Level: {sound_level}")

                    if sound_level > SOUND_THRESHOLD:
                        print("🚨 Accident Detected! Saving event video...")
                        save_accident_video()
            except Exception as e:
                print(f"Serial Read Error: {e}")

# 🎥 Function to Continuously Record & Store in Local Storage
def record_video():
    while True:
        ret, frame = cap.read()
        if ret:
            video_buffer.append(frame)  # Store frames in buffer
            cv2.imshow("Live CCTV Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return
        
        time.sleep(1 / FRAME_RATE)

# 🏃 Start Threads for Continuous Video & Sound Monitoring
threading.Thread(target=record_video, daemon=True).start()
threading.Thread(target=monitor_sound, daemon=True).start()

# ✅ Keep Script Running
while True:
    time.sleep(1)
