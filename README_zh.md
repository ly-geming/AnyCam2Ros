<h1 align="center">
  <br>
  AnyCam2Ros
  <br>
</h1>

<p align="center">
  <strong>将 <i>任意</i> 摄像头瞬间接入 ROS2</strong>
</p>

<p align="center">
  无论是<b>工业相机</b>、<b>USB 摄像头</b>，还是你的<b>旧安卓手机</b>，几秒钟内即可变身为 ROS2 节点。
</p>

<p align="center">
  <a href="#为什么选择-anycam">为什么选择 AnyCam?</a> •
  <a href="#特性">特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#手机变摄像头">手机变摄像头</a> •
  <a href="./README.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-green.svg" alt="ROS2">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/AnyCam-Universal-purple.svg" alt="AnyCam">
</p>

---

<p align="center">
  <i>告别手写重复的启动文件。<br>自动发现、交互式配置、一键启动。</i>
</p>

---

```mermaid
graph LR
    A[📱 手机 / 📷 USB 摄像头] -->|USB/WiFi| B[Linux /dev/video*]
    B --> C[AnyCam2Ros]
    C -->|生成| D[启动脚本]
    D -->|运行| E[ROS 2 Topic]
```

## 🚀 为什么选择 "AnyCam"?

在 Linux 的世界里，**一切皆文件**。

只要你的设备能产生视频流，它就有 99% 的概率能映射为 `/dev/video*` 文件。
**AnyCam2Ros** 并不在乎你使用的是价值 5000 美元的全局快门工业相机，还是你抽屉里闲置的旧安卓手机。

**只要它能在 `/dev/video*` 中出现，我们就能让它变成 ROS 话题。**

## ✨ 特性

- **📱 通用支持** — 支持 USB 摄像头、虚拟摄像头以及手机摄像头。
- **🔍 自动发现** — 瞬间扫描 `/dev/video*` 并识别硬件信息。
- **🛡️ 稳定路径** — 自动解析稳定路径（`/dev/v4l/by-id`），确保重启后摄像头顺序不乱。
- **🎨 精美 CLI** — 丰富多彩的交互式终端体验，引导你轻松完成配置。
- **⚡ 零样板代码** — 生成优化过的 `cam2image` 启动脚本，直接用于生产环境。

## 📱 将安卓手机变成 ROS 摄像头

你不需要昂贵的硬件也能开始开发计算机视觉算法。现在的手机摄像头往往比大多数网络摄像头都要好！

1. **USB 网络摄像头模式（最简单）**
   - 许多现代安卓手机（Google Pixel, 三星等）在插入 USB 时有原生的“网络摄像头”模式。
   - 在 USB 选项中选择“网络摄像头” (Webcam) 而不是“文件传输”。
   - 它会直接作为 `/dev/videoX` 出现在你的电脑上。搞定！

2. **App 方案（通用）**
   - 安装 **DroidCam**、**IP Webcam** 或 **Iriun** 等应用。
   - 通过 USB（推荐，低延迟）或 WiFi 连接。
   - 这些工具会创建虚拟视频设备（例如通过 `v4l2loopback`）或暴露标准 UVC 接口。

一旦手机连接成功，只需运行 `AnyCam2Ros`，它就会像普通摄像头一样被检测到。

## 📦 环境要求

| 依赖 | 说明 |
|------|------|
| **Linux** | 需要 V4L2 设备支持 |
| **Python 3.8+** | CLI 运行环境 |
| **ROS2** | 需要 `image_tools` 包 (`sudo apt install ros-<distro>-image-tools`) |
| **v4l-utils** | 用于硬件探测 (`sudo apt install v4l-utils`) |

## ⚡ 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/AnyCam2Ros.git
cd AnyCam2Ros

# 2. 安装依赖 (用于精美的 UI)
pip install -e .

# 3. 运行魔法 CLI
python3 scripts/camera_cli.py
```

跟随交互式向导：
1. 查看检测到的摄像头（手机、Webcam 等）
2. 选择要使用的设备
3. 命名它们（例如：`front_cam`, `robot_eye`）
4. **启动！**

## 🛠️ 使用方法

### 交互模式（推荐）

```bash
python3 scripts/camera_cli.py
```

这将启动 TUI（文本用户界面）。它将引导您选择分辨率、帧率并为您的 ROS 话题命名。

### 从配置重新生成

与队友分享了项目？他们可以通过配置文件生成完全相同的启动脚本：

```bash
python3 scripts/camera_cli.py --from-config
```

## 📂 生成文件结构

输出清晰整洁，可随时部署：

```text
generated_cameras/
├── start_cam_front.sh      # 单独启动脚本 (已 chmod +x)
├── start_cam_wrist.sh      # 单独启动脚本
└── start_all_cams.sh       # 总开关，一次启动所有摄像头
```

## 📄 许可证

MIT © [Your Name]
