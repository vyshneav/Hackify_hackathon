# Safe Drive 🚗📹

**Safe Drive** is a safety-enhancing system integrated with the dash cam of vehicles to detect accidents and automatically send visual evidence to the nearest police station. The system helps in timely assistance and better traffic incident management.

## 🔧 Features

- Accident detection using sensor input (e.g., crash detection).
- Captures real-time video and images from dash cam.
- Uploads visuals to Google Drive using the Google Drive API.
- Sends an alert email with the visuals link to the nearest police station using Python's email modules.

## 🛠️ Tech Stack

- **Programming Language**: Python  
- **Email Integration**: `smtplib`, `email`  
- **Cloud Storage**: Google Drive API  
- **Hardware**: Dash cam integrated with controller (e.g., Raspberry Pi or ESP32 with a connected system)

## 📝 How It Works

1. The system continuously monitors the vehicle status.
2. On detecting a crash, it:
   - Captures dash cam footage.
   - Uploads the footage to Google Drive.
   - Sends an automated email with the video link to the nearest police station.
