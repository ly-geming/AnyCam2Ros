<div align="center">

# 📷 AnyCam2Ros

**将任意摄像头变成 ROS2 图像话题 — 统一的硬件配置流程**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![ROS2](https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-green.svg)](https://docs.ros.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.md) | [中文文档](README_zh.md)

</div>

---

## 📖 概述

### 🎯 解决什么问题？

当你想在真实机器人上部署 **VLA 模型**（如 [π₀ (pi-zero)](https://www.physicalintelligence.company/blog/pi0)、[OpenVLA](https://openvla.github.io/)），或者为机器人学习采集 **SFT 演示数据** 时，你需要将摄像头画面作为 ROS2 图像话题发布。

但现实情况是：

```
痛点问题：
┌─────────────────────────────────────────────────────────────────────────┐
│  🔄 "我想对齐一个用不同硬件采集的数据集                                     │
│      — 如何复现相同的相机配置？"                                           │
│                                                                         │
│  🎥 "我的数据是用 Insta360 GO 3S、RealSense、USB 摄像头                   │
│      在不同机器上采集的 — 需要一个统一的配置方式"                            │
│                                                                         │
│  ⏰ "给每个摄像头写 cam2image 启动文件太繁琐了"                             │
│                                                                         │
│  🔀 "每次重启后摄像头设备号都会变！"                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**AnyCam2Ros 提供统一的解决方案：**

```
解决方案：
┌─────────────────────────────────────────────────────────────────────────┐
│  🎥 Insta360 GO 3S    ─┐                                                │
│  📷 USB 摄像头        ─┼──▶  /dev/video*  ──▶  AnyCam2Ros  ──▶  ROS2   │
│  🤖 任何 V4L2 设备    ─┘                         CLI           Topics  │
│                                                                         │
│  ✅ 跨硬件统一配置                                                       │
│  ✅ 稳定设备路径（重启后不再乱序）                                         │
│  ✅ 一条命令搞定所有配置                                                  │
│  ✅ 可分享的 JSON 配置，便于数据集对齐                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

**AnyCam2Ros = 任意摄像头 → ROS2 图像话题 → VLA 训练 / 机器人部署**

### 🤖 应用场景

| 场景 | AnyCam2Ros 如何帮助 |
|------|---------------------|
| **数据集对齐** | 在你的硬件上复现已有数据集的相机配置 |
| **VLA 模型部署** | 快速配置相机用于 π₀、OpenVLA、RT-2 部署 |
| **SFT 数据采集** | 统一的流程采集操作演示数据 |
| **多相机配置** | 几分钟内配置 2-4 个相机，命名一致 |
| **跨机器共享** | 在不同机器人之间导入/导出 JSON 配置 |

---

## 💡 为什么是 "Any" Camera？

在 Linux 中，**一切皆文件**。如果你的设备能产生视频，它就会变成 `/dev/video*`。

| 设备类型 | 示例 | 支持 AnyCam2Ros？ |
|----------|------|-------------------|
| 运动相机 | Insta360 GO 3S, GoPro (作为摄像头) | ✅ 支持 |
| 深度相机 | RealSense (RGB 流) | ✅ 支持 |
| USB 摄像头 | 罗技 C920, 通用 UVC | ✅ 支持 |
| 工业相机 | FLIR, Basler (带 V4L2 驱动) | ✅ 支持 |
| 手机作为摄像头 | Android USB Webcam 模式, DroidCam | ✅ 支持 |
| 采集卡 | Elgato, HDMI 采集器 | ✅ 支持 |
| 虚拟摄像头 | OBS Virtual Cam, v4l2loopback | ✅ 支持 |

**只要它出现在 `/dev/video*`，我们就能把它发布到 ROS2。**

---

## ✨ 特性

| 特性 | 描述 |
|------|------|
| 🔍 **自动发现** | 扫描所有 `/dev/video*` 设备并显示硬件信息 |
| 🛡️ **稳定路径** | 使用 `/dev/v4l/by-id`，重启后摄像头顺序不变 |
| 🎨 **精美 CLI** | 基于 Rich 的交互式界面，带表格、动画和彩色输出 |
| ⚡ **零样板代码** | 即时生成优化的 `cam2image` 脚本 |
| 📦 **可分享配置** | JSON 配置文件便于团队协作和数据集对齐 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/ly-geming/AnyCam2Ros.git
cd AnyCam2Ros

# 安装（包含 Rich 精美 CLI）
pip install -e .
```

### 前置依赖

```bash
# 安装 v4l-utils 用于摄像头检测
sudo apt install v4l-utils

# 安装 ROS2 image_tools
sudo apt install ros-${ROS_DISTRO}-image-tools
```

### 运行

```bash
python3 scripts/camera_cli.py
```

交互式向导将引导你：
1. **扫描** — 检测所有已连接的摄像头
2. **选择** — 选择要配置的摄像头
3. **配置** — 设置分辨率、帧率、ROS 命名空间
4. **生成** — 创建开箱即用的启动脚本

---

## 📂 输出结构

```
generated_cameras/
├── start_cam_front.sh      # 单个摄像头脚本
├── start_cam_wrist.sh      # 单个摄像头脚本
└── start_all_cams.sh       # 一键启动所有
```

**启动所有摄像头：**
```bash
./generated_cameras/start_all_cams.sh
```

**用 image_view 验证：**
```bash
ros2 run image_view image_view --ros-args -r image:=/hdas/camera_front/color/image_raw
```

---

## 🛠️ 使用模式

### 交互模式（推荐）

```bash
python3 scripts/camera_cli.py
```

### 从配置重新生成

与队友分享你的 `cameras.json`，或在不同机器间共享：

```bash
python3 scripts/camera_cli.py --from-config
```

### 自定义路径

```bash
python3 scripts/camera_cli.py \
  --config /path/to/cameras.json \
  --output-dir /path/to/scripts/
```

---

## 📦 环境要求

| 依赖 | 描述 |
|------|------|
| **Linux** | 需要 V4L2 设备支持 |
| **Python 3.8+** | CLI 运行环境 |
| **ROS2** | `image_tools` 包 |
| **v4l-utils** | 摄像头检测 (`v4l2-ctl`) |

---

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

---

## 📄 许可证

MIT © [ly-geming](https://github.com/ly-geming)

---

<div align="center">

**⭐ 如果这个项目对你的机器人项目有帮助，请点个 Star！⭐**

</div>
