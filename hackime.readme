# AI-Powered Accident Detection & Video Upload System

## 📌 Project Overview
This project is an **AI-powered accident detection system** that continuously records video, detects accidents using a **sound sensor (ESP32)**, and uploads **1-minute pre/post accident footage** to **Google Drive** for evidence storage. It is designed to enhance emergency response efficiency by providing real-time incident footage.

## 🚀 Features
- 📷 **Continuous video recording** stored locally.
- 🎙️ **Sound sensor-based accident detection** using an ESP32.
- ⏳ **Retrieves 1-minute before & after** accident footage.
- ☁️ **Uploads footage to Google Drive** using Drive API.
- 🔄 **Automated & real-time response**.

## 🛠️ Tech Stack
- **Hardware:** ESP32, Sound Sensor, Laptop (for processing)
- **Software:** Python, OpenCV, Google Drive API
- **Libraries:** `cv2`, `serial`, `google-auth`, `googleapiclient`

## 📂 Folder Structure
```
├── recordings/            # Stores locally recorded videos
├── main.py                # Main script (sensor reading, recording, uploading)
├── google_drive.py        # Google Drive upload logic
├── requirements.txt       # Dependencies
├── README.md              # Project documentation
```

## 🔧 Setup Instructions
### 1️⃣ Install Dependencies
Ensure you have **Python 3.10+** installed.
```sh
pip install -r requirements.txt
```

### 2️⃣ Connect ESP32 to Serial Port
- Update the **`SERIAL_PORT`** value in `main.py` to match your system's port.

### 3️⃣ Set Up Google Drive API
- Create a **Google Cloud Project**.
- Enable **Google Drive API**.
- Generate a **Service Account JSON key**.
- Replace `your-google-api-file.json` with the actual filename.
- Update `FOLDER_ID` with your **Google Drive folder ID**.

### 4️⃣ Run the Project
```sh
python main.py
```

## ⚙️ How It Works
1️⃣ The script **continuously records video** and saves it locally.
2️⃣ **ESP32 reads sound levels** via the serial port.
3️⃣ If the **sound level exceeds the threshold** (accident detected):
   - Retrieves **1-minute pre-event footage** from buffer.
   - Records **1-minute post-event footage**.
   - Saves & **uploads the footage to Google Drive**.

## 📌 Future Enhancements
- 📡 **Automated emergency alert** to nearest police station.
- 🎯 **AI-based accident verification** to reduce false triggers.
- 🌍 **Cloud integration with AWS for scalability**.

## 📝 Commands Summary
| Command | Description |
|---------|-------------|
| `pip install -r requirements.txt` | Install dependencies |
| `python main.py` | Run the project |

---
🚀 *This project is built for **Hackathons & Smart City Solutions**!*

