# 🎯 ShotTracker

**WORK IN PROGRESS** This is currently not a plug-and-play solution. Some tinkering is required to get it working.


**ShotTracker** is a web application for tracking air gun shots on a target using a USB webcam and printed markers. 
Tested on **Raspberry Pi 5** with a Logitech USB webcam.

### You need:
- A Raspberry Pi 5 with a USB webcam or Raspberry Pi Camera Module, tested with 4 gb RAM.
- Access to a printer to print the target markers.
- A web browser to access the user interface.

### 1. Hardware Setup
- **Raspberry Pi 5 (Or any other computer):** Simply earn enough shells to buy one. 
- **Note:** A raspberry pi is not required! It is simply a great way to keep the setup protable and good for hosting small servers like this. The app is not tested on Raspberry Pi 4 or earlier models, but it may work. Give it a shot.
- **Camera:** USB webcam or Raspberry Pi Camera Module (tested with Logitech webcam)
- **Target:** Print the complete target image in the `markers` folder. Or follow the instructions in the same folder to create a custom target.
  **Important:** Markers must be fully visible to the camera and oriented as shown in the example setup image. See the readne `markers` for more details.

### 2. Software Installation (Raspberry Pi 5)

#### a. Install Dependencies

Use a venv if you wish. Open a terminal and run:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
pip3 install flask flask_socketio gevent opencv-python numpy pillow
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
Look for the `inet` address under your network adapter (like `wlan0` or `eth0`).  
**Save this IP address** for accessing the web interface.

#### d. Start the Server

Note: I really recommend using the ssh plugin for Visual Studio Code to run the server.

```bash
python3 main.py
```


---

##  Access the Web Interface

On any device connected to the same network, open a browser and go to:

```
http://<raspberry_pi_ip>:1337
```
Replace `<raspberry_pi_ip>` with the IP address you found earlier.

---

##  Usage Instructions

1. **Set Up the Target:**  
   Place the target with markers attached in the camera's view. Ensure all markers are clearly visible. I recommend placing the camera below the target since that is how it has been tested.

2. **Adjust Camera:**  
   If your camera does not properly correct the perspective in the web view (meaning the markers are still visible), try adjusting the camera angle and the camera settings like focus, auto-focus, and exposure for better results. These are available in the menu in the top left corner.

3. **Capture Reference Image:**  
   Click **"Capture Reference Image"** in the web UI. This sets the baseline for shot detection. If you are using this in an environment with changing lightning I recommend that you capture a new reference image before each shot and discard any false positives that may occur due to changing light conditions. See "Review & Save" for instruction.

4. **Take a Shot:**  
   Fire at the target. After each shot, click **"Capture Reference Image"** to detect and display the shot location. Be careful to not hit your equipment. It is also not my responsibility.

5. **Review & Save:**  
   Accept or discard the detected shot. Accepted shots are saved and shown on the interface.

6. **Repeat:**  
   Next player can take their shot. Continue as needed.

---

##  Known Issues

- **A lot**
This is a work in progress. Large parts of what makes this app ready to use are not yet implemented. If you know some js and python you can figure it out quite easily. Chances are you will find something that you would like to see added or fixed. If you do, please open an issue on GitHub.

---

##  Troubleshooting

- **Web Interface Not Loading:**  
  Double-check the IP address and ensure your device is on the same network as the Raspberry Pi. Check for server errors such as the camera not being detected. See below.

- **No Camera Detected:**  
  Make sure your webcam is plugged in before starting the server.

- **Markers Not Detected:**  
  Reprint markers if faded. Ensure good lighting and clear visibility. I have also found that if the markers reflect a lot of light they can be hard to detect. This makes the system often perform better in darker environments. Try playing with the exposure and focus in the menu.

---

##  Support

For issues or requests just open an [issue on GitHub](https://github.com/Toiseo/ShotTracker/issues).