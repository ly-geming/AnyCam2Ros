<h1 align="center">
  <br>
  AnyCam2Ros
  <br>
</h1>

<p align="center">
  <strong>Connect  <i>Any</i> Camera to ROS2 instantly</strong>
</p>

<p align="center">
  Turn your <b>Industrial Cameras</b>, <b>USB Webcams</b>, or even your <b>Android Phone</b> into ROS2 nodes in seconds.
</p>

<p align="center">
  <a href="#why-anycam">Why AnyCam?</a> •
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#android-as-webcam">Phone as Camera</a> •
  <a href="./README_zh.md">中文文档</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-green.svg" alt="ROS2">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/AnyCam-Universal-purple.svg" alt="AnyCam">
</p>

---

<p align="center">
  <i>No more writing repetitive launch files. <br>Auto-discovery, Interactive Configuration, and One-Click Launch.</i>
</p>

---

```mermaid
graph LR
    A[📱 Phone / 📷 USB Cam] -->|USB/WiFi| B[Linux /dev/video*]
    B --> C[AnyCam2Ros]
    C -->|Generate| D[Startup Scripts]
    D -->|Run| E[ROS 2 Topic]
```

## 🚀 Why "AnyCam"?

In the Linux world, **everything is a file**. 

If your device can produce a video stream, there is a 99% chance it can be mapped to a `/dev/video*` file. 
**AnyCam2Ros** doesn't care if you spent $5000 on a global-shutter machine vision camera or $0 using your old Android phone. 

**If it's in `/dev/video*`, we can make it a ROS topic.**

## ✨ Features

- **📱 Universal Support** — Works with USB cams, potential virtual cams, and phone-based webcams.
- **🔍 Auto-Discovery** — Instantly scans `/dev/video*` and identifies your hardware.
- **🛡️ Stable Paths** — Automatically resolves stable paths (`/dev/v4l/by-id`) so your camera order never swaps after a reboot.
- **🎨 Beautiful CLI** — A rich, interactive terminal experience to guide you through setup.
- **⚡ Zero-Boilerplate** — Generates optimized `cam2image` launch scripts ready for production.

## 📱 Making an Android Phone a ROS Camera

You don't need expensive hardware to start developing computer vision algorithms. Your phone is likely a better camera than most webcams!

1. **USB Webcam Mode (Easiest)**
   - Many modern Android phones (Google Pixel, Samsung, etc.) have a native "Webcam" mode when you plug them into USB.
   - Select "Webcam" instead of "File Transfer".
   - It will appear as `/dev/videoX` on your computer. Done!

2. **Apps (Universal)**
   - Install apps like **DroidCam**, **IP Webcam**, or **Iriun**.
   - Connect via USB (recommended for low latency) or WiFi.
   - These tools create a virtual video device (e.g. via `v4l2loopback`) or exposed standard UVC interfaces.

Once your phone is connected, just run `AnyCam2Ros` and it will detect it like any other camera.

## 📦 Requirements

| Dependency | Description |
|------------|-------------|
| **Linux** | Required for V4L2 device handling |
| **Python 3.8+** | CLI runtime |
| **ROS2** | Needs `image_tools` package (`sudo apt install ros-<distro>-image-tools`) |
| **v4l-utils** | For hardware probing (`sudo apt install v4l-utils`) |

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AnyCam2Ros.git
cd AnyCam2Ros

# 2. Install dependencies (Rich for beautiful UI)
pip install -e .

# 3. Run the Magic CLI
python3 scripts/camera_cli.py
```

Follow the interactive wizard:
1. View detected cameras (Phone, Webcam, etc.)
2. Select which ones to use
3. Name them (e.g., `front_cam`, `robot_eye`)
4. **Launch!**

## 🛠️ Usage

### Interactive Mode (Recommended)

```bash
python3 scripts/camera_cli.py
```

This launches the TUI (Text User Interface). It will guide you through selecting resolution, FPS, and naming your ROS topics.

### Regenerate from Config

Shared your project with a teammate? They can generate the same launch scripts from the config file:

```bash
python3 scripts/camera_cli.py --from-config
```

## 📂 Generated Structure

Your output is clean and ready to deploy:

```text
generated_cameras/
├── start_cam_front.sh      # Individual launch script (chmod +x)
├── start_cam_wrist.sh      # Individual launch script
└── start_all_cams.sh       # Master switch to launch EVERYTHING
```

## 📄 License

MIT © [Your Name]
