<div align="center">

# 📷 AnyCam2Ros

**Turn Any Camera into ROS2 Image Topics — Unified Pipeline for Any Hardware**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ROS2](https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-green.svg)](https://docs.ros.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.md) | [中文文档](README_zh.md)

</div>

---

## 📖 Overview

### 🎯 What Problem Does This Solve?

When deploying **VLA models** (like [π₀ (pi-zero)](https://www.physicalintelligence.company/blog/pi0), [OpenVLA](https://openvla.github.io/)) on real robots, or collecting **SFT demonstration data** for robot learning, you need camera feeds as ROS2 image topics.

But here's the reality:

```
The Problem:
┌─────────────────────────────────────────────────────────────────────────┐
│  🔄 "I want to align with an existing dataset collected on different    │
│      hardware — how do I replicate the same camera setup?"              │
│                                                                         │
│  🎥 "My data was collected with Insta360 GO 3S, RealSense, USB webcams  │
│      on different machines — I need a unified way to configure them"   │
│                                                                         │
│  ⏰ "Writing cam2image launch files for each camera is tedious"         │
│                                                                         │
│  🔀 "Camera device IDs keep changing after every reboot!"               │
└─────────────────────────────────────────────────────────────────────────┘
```

**AnyCam2Ros provides a unified solution:**

```
The Solution:
┌─────────────────────────────────────────────────────────────────────────┐
│  🎥 Insta360 GO 3S    ─┐                                                │
│  📷 USB Webcam        ─┼──▶  /dev/video*  ──▶  AnyCam2Ros  ──▶  ROS2   │
│  🤖 Any V4L2 Device   ─┘                         CLI           Topics  │
│                                                                         │
│  ✅ Unified config across different hardware                            │
│  ✅ Stable device paths (no more reordering after reboot)              │
│  ✅ One command to configure everything                                 │
│  ✅ Shareable JSON config for dataset alignment                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**AnyCam2Ros = Any Camera → ROS2 Image Topics → VLA Training / Robot Deployment**

### 🤖 Use Cases

| Scenario | How AnyCam2Ros Helps |
|----------|---------------------|
| **Dataset Alignment** | Replicate camera setups from existing datasets on your hardware |
| **VLA Model Deployment** | Quickly configure cameras for π₀, OpenVLA, RT-2 deployment |
| **SFT Data Collection** | Unified pipeline for collecting manipulation demos |
| **Multi-Camera Setup** | Configure 2-4 cameras in minutes with consistent naming |
| **Cross-Machine Sharing** | Export/import JSON configs between different robots |

---

## 💡 Why "Any" Camera?

In Linux, **everything is a file**. If your device can produce video, it becomes `/dev/video*`.

| Device Type | Example | Works with AnyCam2Ros? |
|-------------|---------|------------------------|
| Action Camera | Insta360 GO 3S, GoPro (as webcam) | ✅ Yes |
| Depth Camera | RealSense (RGB stream) | ✅ Yes |
| USB Webcam | Logitech C920, generic UVC | ✅ Yes |
| Industrial Camera | FLIR, Basler (with V4L2 driver) | ✅ Yes |
| Phone as Webcam | Android USB Webcam mode, DroidCam | ✅ Yes |
| Capture Card | Elgato, HDMI grabbers | ✅ Yes |
| Virtual Camera | OBS Virtual Cam, v4l2loopback | ✅ Yes |

**If it shows up in `/dev/video*`, we can publish it to ROS2.**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Auto-Discovery** | Scans all `/dev/video*` devices and shows hardware info |
| 🛡️ **Stable Paths** | Uses `/dev/v4l/by-id` so camera order survives reboots |
| 🎨 **Beautiful CLI** | Rich interactive TUI with tables, spinners, and colors |
| ⚡ **Zero Boilerplate** | Generates optimized `cam2image` scripts instantly |
| 📦 **Shareable Config** | JSON config for team collaboration and dataset alignment |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ly-geming/AnyCam2Ros.git
cd AnyCam2Ros

# Install dependencies
pip install rich
```

### Prerequisites

```bash
# Install v4l-utils for camera detection
sudo apt install v4l-utils

# Install ROS2 image_tools
sudo apt install ros-${ROS_DISTRO}-image-tools
```

### Running

```bash
python3 scripts/camera_cli.py
```

The interactive wizard will:
1. **Scan** — Detect all connected cameras
2. **Select** — Choose which cameras to configure
3. **Configure** — Set resolution, FPS, ROS namespace
4. **Generate** — Create ready-to-run launch scripts

---

## 📂 Output Structure

```
generated_cameras/
├── start_cam_front.sh      # Individual camera script
├── start_cam_wrist.sh      # Individual camera script  
└── start_all_cams.sh       # Launch everything with one command
```

**Start all cameras:**
```bash
./generated_cameras/start_all_cams.sh
```

**Verify with image_view:**
```bash
ros2 run image_view image_view --ros-args -r image:=/hdas/camera_front/color/image_raw
```

---

## 🛠️ Usage Modes

### Interactive Mode (Recommended)

```bash
python3 scripts/camera_cli.py
```

### Regenerate from Config

Share your `cameras.json` with teammates or across machines:

```bash
python3 scripts/camera_cli.py --from-config
```

### Custom Paths

```bash
python3 scripts/camera_cli.py \
  --config /path/to/cameras.json \
  --output-dir /path/to/scripts/
```

---

## 📦 Requirements

| Dependency | Description |
|------------|-------------|
| **Linux** | Required for V4L2 device handling |
| **Python 3.8+** | CLI runtime |
| **ROS2** | `image_tools` package |
| **v4l-utils** | Camera detection (`v4l2-ctl`) |

---

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

---

## 📄 License

MIT © [ly-geming](https://github.com/ly-geming)

---

<div align="center">

**⭐ Star this repo if it helps your robot project! ⭐**

</div>
