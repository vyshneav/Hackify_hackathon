import cv2
import serial
import time
import threading
import os
from datetime import datetime
from collections import deque
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2 import service_account

# 🔄 Constants & Configurations
SERIAL_PORT = "COM3"  # Change based on your system
BAUD_RATE = 115200
SOUND_THRESHOLD = 1400  # Trigger level for accident detection
VIDEO_STORAGE = "recordings/"
PRE_EVENT_DURATION = 10  # 5 minutes before (seconds)
POST_EVENT_DURATION = 10  # 5 minutes after (seconds)
FRAME_RATE = 30  # FPS
BUFFER_SIZE = PRE_EVENT_DURATION * FRAME_RATE  # Number of frames stored
video_buffer = deque(maxlen=BUFFER_SIZE)

# 📷 Initialize Camera
cap = cv2.VideoCapture(0)  # 0 for the default webcam
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# 🎙️ Initialize Serial Communication
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# 🗂️ Google Drive API Setup
SERVICE_ACCOUNT_FILE = "sample_api.json"  # Replace with your API file
FOLDER_ID = "sample_id"  # Replace with your Google Drive Folder ID

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=creds)

# 🎥 Function to Continuously Record & Store in Local Storage
def record_video():
    while True:
        event_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = os.path.join(VIDEO_STORAGE, f"video_{event_timestamp}.mp4")
        
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(local_filename, fourcc, FRAME_RATE, (frame_width, frame_height))
        
        print(f"🎥 Recording video: {local_filename}")
        for _ in range(POST_EVENT_DURATION * FRAME_RATE):  # Save in 5-minute chunks
            ret, frame = cap.read()
            if ret:
                video_buffer.append(frame)  # Store frames in buffer
                out.write(frame)
                cv2.imshow("Live CCTV Feed", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                out.release()
                cap.release()
                cv2.destroyAllWindows()
                return
            
            time.sleep(1 / FRAME_RATE)
        
        out.release()

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

# 🎬 Function to Save 5 Min Before & 5 Min After Accident
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

    # Continue recording for 5 minutes after detection
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
        "parents": [FOLDER_ID]  # Upload to specific Google Drive folder
    }
    media = MediaFileUpload(filepath, mimetype="video/mp4")

    try:
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        print(f"🚀 Video uploaded successfully! File ID: {file.get('id')}")
    except Exception as e:
        print(f"❌ Upload Error: {e}")

# 🏃 Start Threads for Continuous Video & Sound Monitoring
threading.Thread(target=record_video, daemon=True).start()
threading.Thread(target=monitor_sound, daemon=True).start()

# ✅ Keep Script Running
while True:
    time.sleep(1)
