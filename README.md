# 🎯 ShotTracker

**WORK IN PROGRESS** This is currently not a plug-and-play solution. The code is still being developed and tested.


**ShotTracker** is a Python server application for tracking air gun shots on a target using a USB webcam and printed markers.  
Tested on **Raspberry Pi 5** with a Logitech USB webcam.

---

## 📸 Features

- Detects and scores shots on a physical target using computer vision
- Web-based interface for live control and results
- Supports multiple players and shot history
- Adjustable camera focus via the web UI

---

## 🚀 Quick Start

### 1. Hardware Setup

- **Camera:** USB webcam (tested with Logitech models)
- **Target:** Print the markers from the `Markers` folder and attach them to the four corners of your target.  
  **Important:** Markers must be fully visible to the camera and oriented as shown in the sample image.

### 2. Software Installation (Raspberry Pi 5)

#### a. Install Dependencies

Open a terminal and run:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
pip3 install opencv-python flask numpy flask_socketio gevent
```

#### b. Clone the Repository

```bash
git clone https://github.com/Toiseo/ShotTracker.git ~/ShotTracker
cd ~/ShotTracker/ShotTracker
```

#### c. Find Your Raspberry Pi's IP Address

```bash
ifconfig
```
Look for the `inet` address under your network adapter (e.g., `wlan0` or `eth0`).  
**Save this IP address** for accessing the web interface.

#### d. Start the Server

```bash
python3 main.py
```

---

## 🌐 Access the Web Interface

On any device connected to the same network, open a browser and go to:

```
http://<raspberry_pi_ip>:1337
```
Replace `<raspberry_pi_ip>` with the IP address you found earlier.

---

## 🏹 Usage Instructions

1. **Set Up the Target:**  
   Place the target with attached markers in the camera's view. Ensure all markers are clearly visible. I recommend placing the camera below the target since that is how it has been tested.

2. **Adjust Camera:**  
   If your camera does not properly correct the perspective in the web view, try adjusting the camera angle and the camera settings like focus, auto-focus, and exposure for better results.

3. **Capture Reference Image:**  
   Click **"Capture Reference Image"** in the web UI. This sets the baseline for shot detection. If you are using this in an environment with changing light conditions I recommend that you capture a new reference image before each shot and discard any false positives that may occur due to changing light conditions. See "Review & Save" for more details.

4. **Take a Shot:**  
   Fire at the target. After each shot, click **"Capture Reference Image"** to detect and display the shot location.

5. **Review & Save:**  
   Accept or discard the detected shot. Accepted shots are saved and shown in the interface.

6. **Repeat:**  
   Next player can take their shot. Continue as needed.

---

## ⚠️ Known Issues

- **Camera Focus:**  
  If the target is blurry, adjust the focus slider in the web UI or reposition the camera.

- **Marker Detection:**  
  Markers must be fully visible and not obstructed. Avoid steep camera angles.

- **Camera Connection:**  
  The server will crash if no camera is connected or if you try to capture a shot before setting a reference image.

---

## 📂 Folder Structure

```
ShotTracker/
├── main.py
├── Markers/
│   └── [marker images]
├── static/
├── templates/
└── README.md
```

---

## 🛠️ Troubleshooting

- **Web Interface Not Loading:**  
  Double-check the IP address and ensure your device is on the same network as the Raspberry Pi.

- **No Camera Detected:**  
  Make sure your webcam is plugged in before starting the server.

- **Markers Not Detected:**  
  Reprint markers if faded. Ensure good lighting and clear visibility.

---

## 📧 Support

For issues or feature requests, open an [issue on GitHub](https://github.com/Toiseo/ShotTracker/issues).