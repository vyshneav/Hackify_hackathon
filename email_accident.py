import cv2
import serial
import time
import threading
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from collections import deque
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 🔄 Constants & Configurations
SERIAL_PORT = "COM3"  # Change based on your system
BAUD_RATE = 115200
SOUND_THRESHOLD = 400  # Trigger level for accident detection
VIDEO_STORAGE = "recordings/"
PRE_EVENT_DURATION = 10  # 10 seconds before
POST_EVENT_DURATION = 10  # 10 seconds after
FRAME_RATE = 30  # FPS
BUFFER_SIZE = PRE_EVENT_DURATION * FRAME_RATE  # Number of frames stored
video_buffer = deque(maxlen=BUFFER_SIZE)

# 📷 Initialize Camera
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# 🎙️ Initialize Serial Communication
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# 🗂️ Google Drive API Setup
SERVICE_ACCOUNT_FILE = "hackify-cloud-de0a0c13ec0a.json"  # Replace with your file
FOLDER_ID = "1zX4ACD5cF-uqWlWwujadlz2TMDq8R4tC"  # Replace with your folder ID

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# ✉️ Email Configuration
SENDER_EMAIL = "nath73065@gmail.com"  # Replace with sender email
SENDER_PASSWORD = "dsbkhypstjzqujhs"  # Replace with App Password
RECEIVER_EMAIL = "vysh7561@gmail.com"  # Replace with receiver email

# 📤 Function to Send Email
def send_email(drive_link):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = "🚨 Accident Alert: Video Available"

        body = f"""
        An accident has been detected. The recorded video has been uploaded to Google Drive. 

        🔗 Video Link: {drive_link}

        Please take necessary action.

        Regards, 
        Accident Detection System
        """
        msg.attach(MIMEText(body, "plain"))

        # Setup the SMTP Server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email Sending Failed: {e}")

# 🎬 Function to Save 10 Sec Before & After Accident
def save_accident_video():
    event_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(VIDEO_STORAGE, f"accident_{event_timestamp}.mp4")
    print(f"Saving accident video to: {filename}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(filename, fourcc, FRAME_RATE, (frame_width, frame_height))

    # ✅ Fix: Copy buffer to avoid mutation error
    frames_to_save = list(video_buffer)

    print("Writing pre-event frames...")
    for frame in frames_to_save:
        out.write(frame)

    # Continue recording for 10 seconds after detection
    print("Recording post-event frames...")
    for _ in range(POST_EVENT_DURATION * FRAME_RATE):
        ret, frame = cap.read()
        if ret:
            out.write(frame)

    out.release()
    print(f"✅ Accident video saved: {filename}")

    # Upload to Google Drive
    upload_to_drive(filename)

# 📤 Function to Upload Video to Google Drive
def upload_to_drive(filepath):
    filename = os.path.basename(filepath)
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(filepath, mimetype="video/mp4")

    try:
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        file_id = file.get("id")
        drive_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        print(f"🚀 Video uploaded successfully! Link: {drive_link}")

        # Send Email with Drive Link
        send_email(drive_link)
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
                    print(f"Sound Level: {sound_level}")

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
