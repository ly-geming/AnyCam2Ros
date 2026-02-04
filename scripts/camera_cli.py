#!/usr/bin/env python3
"""
AnyCam2Ros - Interactive camera setup CLI for ROS2.

Discovers Any cameras (Linux/USB/Android) and generates reusable cam2image startup scripts.
"""
import argparse
import datetime
import glob
import json
import os
import stat
import re
import subprocess
import sys
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.layout import Layout
from rich.text import Text

# Resolve paths relative to this script's location
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)

DEFAULT_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "configs", "cameras.json")
DEFAULT_OUTPUT_DIR = os.path.join(_SCRIPT_DIR, "generated_cameras")

INFO_PATTERNS = [
    re.compile(r"Caps"),
    re.compile(r"Width/Height"),
    re.compile(r"Payload"),
    re.compile(r"Pixel Format"),
]

console = Console()

def print_banner():
    title = Text("AnyCam2Ros", style="bold magenta", justify="center")
    subtitle = Text("Discover & Configure Any Camera for ROS2", style="cyan", justify="center") 
    
    panel = Panel(
        Text.assemble(title, "\n", subtitle),
        border_style="magenta",
        expand=False,
        padding=(1, 4)
    )
    console.print(panel, justify="center")
    console.print()

def run_v4l2_all(device_path, timeout_s=2.0):
    try:
        result = subprocess.run(
            ["v4l2-ctl", f"--device={device_path}", "--all"],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError:
        return False, "v4l2-ctl not found"
    except subprocess.TimeoutExpired:
        return False, "v4l2-ctl timeout"

    if result.returncode != 0:
        return False, result.stderr.strip() or "v4l2-ctl failed"
    return True, result.stdout


def extract_summary(output):
    lines = []
    width = None
    height = None

    for line in output.splitlines():
        if any(p.search(line) for p in INFO_PATTERNS):
            lines.append(line.strip())

        if "Width/Height" in line:
            match = re.search(r"Width/Height\s*:\s*(\d+)\s*/\s*(\d+)", line)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))

    return lines, width, height


def build_symlink_maps():
    by_id = {}
    by_path = {}

    for base, mapping in (
        ("/dev/v4l/by-id", by_id),
        ("/dev/v4l/by-path", by_path),
    ):
        if not os.path.isdir(base):
            continue
        for link in glob.glob(os.path.join(base, "*")):
            if not os.path.islink(link):
                continue
            target = os.path.realpath(link)
            mapping[target] = link

    return by_id, by_path


def list_video_devices():
    devices = [d for d in glob.glob("/dev/video*") if os.path.exists(d)]
    return sorted(devices)


def gather_device_info():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task(description="Scanning for cameras...", total=None)
        
        by_id, by_path = build_symlink_maps()
        devices = list_video_devices()
        results = []

        for dev in devices:
            progress.update(task, description=f"Probing {dev}...")
            ok, output = run_v4l2_all(dev)
            if ok:
                summary, width, height = extract_summary(output)
            else:
                summary = [output]
                width = None
                height = None

            results.append(
                {
                    "path": dev,
                    "by_id": by_id.get(os.path.realpath(dev)),
                    "by_path": by_path.get(os.path.realpath(dev)),
                    "summary_lines": summary,
                    "width": width,
                    "height": height,
                }
            )
            time.sleep(0.1) # UI feel

        return results


def print_device_table(devices):
    table = Table(title="Detected Video Devices", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", width=4)
    table.add_column("Device", style="green")
    table.add_column("Stable Info", style="yellow")
    table.add_column("Resolution", justify="right")
    table.add_column("Summary", overflow="fold")

    for idx, dev in enumerate(devices):
        stable = dev.get("by_id") or dev.get("by_path") or "-"
        stable = os.path.basename(stable) if stable != "-" else "-" # shorten for table
        
        size = "-"
        if dev.get("width") and dev.get("height"):
            size = f"{dev.get('width')}x{dev.get('height')}"
            
        summary = dev.get("summary_lines")[0] if dev.get("summary_lines") else "-"
        # Clean summary for display
        
        table.add_row(
            str(idx),
            dev.get('path', ''),
            stable,
            size,
            summary
        )

    console.print(table)
    console.print("[dim]Hint: Prefer stable paths in /dev/v4l/by-id or /dev/v4l/by-path.[/dim]")


def parse_selection(raw, max_idx):
    raw = raw.strip().lower()
    if raw in {"a", "all"}:
        return list(range(max_idx))
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    selected = []
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Invalid selection: {part}")
        idx = int(part)
        if idx < 0 or idx >= max_idx:
            raise ValueError(f"Out of range: {idx}")
        selected.append(idx)
    if not selected:
        raise ValueError("No selection")
    return selected


def parse_selection_with_count(raw, max_idx, expected_count):
    selected = parse_selection(raw, max_idx)
    if len(selected) != expected_count:
        raise ValueError(f"Expected {expected_count} devices, got {len(selected)}")
    return selected


def sanitize_name(name):
    name = name.strip().lower().replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]+", "", name)
    if not name:
        raise ValueError("Name cannot be empty")
    return name


def is_valid_namespace(value):
    return re.fullmatch(r"/([A-Za-z0-9_]+/)*[A-Za-z0-9_]+", value or "") is not None


def is_valid_rel_name(value):
    return re.fullmatch(r"[A-Za-z0-9_]+(/[A-Za-z0-9_]+)*", value or "") is not None


def prompt_namespace(default_value):
    while True:
        value = Prompt.ask("ROS namespace [dim](must start with /)[/dim]", default=default_value)
        if is_valid_namespace(value):
            return value
        console.print("[red]Invalid namespace. Example: /hdas/camera_left[/red]")


def prompt_rel_topic(default_value, label):
    while True:
        value = Prompt.ask(label, default=default_value).strip()
        value = value.lstrip("/")
        if is_valid_rel_name(value):
            return value
        console.print("[red]Invalid value. Use letters/numbers/_ and '/'.[/red]")


def join_topic(namespace, image_topic):
    return f"{namespace.rstrip('/')}/{image_topic.lstrip('/')}"


def resolve_default_size(dev):
    width = dev.get("width") or 1920
    height = dev.get("height") or 1080
    return width, height


def choose_device_path(dev):
    return dev.get("by_id") or dev.get("by_path") or dev.get("path")


def generate_cam_script(camera):
    return "\n".join(
        [
            "#!/bin/bash",
            "set -euo pipefail",
            "",
            f'DEVICE_PATH="{camera["device_path"]}"',
            f"WIDTH=${{WIDTH:-{camera['width']}}}",
            f"HEIGHT=${{HEIGHT:-{camera['height']}}}",
            f"FREQ=${{FREQ:-{camera['fps']}}}",
            f'FRAME_ID=${{FRAME_ID:-"{camera["frame_id"]}"}}',
            f'NAMESPACE=${{NAMESPACE:-"{camera["namespace"]}"}}',
            f'IMAGE_TOPIC=${{IMAGE_TOPIC:-"{camera["image_topic"]}"}}',
            "",
            "resolve_device_id() {",
            '  local input="$1"',
            "",
            '  if [ -z "$input" ]; then',
            "    return 1",
            "  fi",
            "",
            '  if [[ "$input" =~ ^/dev/video([0-9]+)$ ]]; then',
            '    echo "${BASH_REMATCH[1]}"',
            "    return 0",
            "  fi",
            "",
            '  if [[ "$input" =~ ^[0-9]+$ ]]; then',
            '    echo "$input"',
            "    return 0",
            "  fi",
            "",
            '  if [ -e "$input" ]; then',
            "    local target",
            '    target=$(readlink -f "$input")',
            '    if [[ "$target" =~ /dev/video([0-9]+)$ ]]; then',
            '      echo "${BASH_REMATCH[1]}"',
            "      return 0",
            "    fi",
            "  fi",
            "",
            "  return 1",
            "}",
            "",
            'DEVICE_ID=$(resolve_device_id "$DEVICE_PATH" || true)',
            'if [ -z "$DEVICE_ID" ]; then',
            '  echo "Failed to resolve device id from $DEVICE_PATH" >&2',
            "  exit 1",
            "fi",
            "",
            "ros2 run image_tools cam2image --ros-args \\",
            "  -p device_id:=$DEVICE_ID \\",
            "  -p width:=$WIDTH \\",
            "  -p height:=$HEIGHT \\",
            "  -p frequency:=$FREQ \\",
            "  -p frame_id:=$FRAME_ID \\",
            "  --remap __ns:=$NAMESPACE \\",
            "  --remap image:=$IMAGE_TOPIC",
        ]
    )


def generate_start_all(script_names):
    lines = [
        "#!/bin/bash",
        "set -euo pipefail",
        "",
        'SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)',
        "",
    ]
    for script in script_names:
        lines.append(f"$SCRIPT_DIR/{script} &")
    lines.append("wait")
    return "\n".join(lines)


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
        handle.write("\n")


def make_executable(path):
    st_mode = os.stat(path).st_mode
    os.chmod(path, st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def load_config_cameras(config_path):
    with open(config_path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError("Config root must be an object")

    camera_items = raw.get("cameras", [])
    if not isinstance(camera_items, list) or not camera_items:
        raise ValueError("No cameras in config")

    cameras = []
    for item in camera_items:
        if not isinstance(item, dict):
            raise ValueError("Each camera entry must be an object")
        camera = {
            "name": str(item.get("name", "")),
            "device_path": str(item.get("device_path", "")),
            "width": int(item.get("width", 0)),
            "height": int(item.get("height", 0)),
            "fps": float(item.get("fps", 0.0)),
            "namespace": str(item.get("namespace", "")),
            "frame_id": str(item.get("frame_id", "")),
            "image_topic": str(item.get("image_topic", "")),
        }
        if not camera["name"] or not camera["device_path"]:
            raise ValueError("Camera entry missing name or device_path")
        if not is_valid_namespace(camera["namespace"]):
            raise ValueError(
                f"Invalid namespace in config: {camera['namespace']} (must start with /)"
            )
        if not is_valid_rel_name(camera["image_topic"]):
            raise ValueError(f"Invalid image_topic in config: {camera['image_topic']}")
        cameras.append(camera)

    return cameras


def generate_from_config(config_path, output_dir):
    try:
        cameras = load_config_cameras(config_path)
    except Exception as e:
        console.print(f"[bold red]Error loading config:[/bold red] {e}")
        return

    ensure_dir(output_dir)
    script_names = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(description=f"Generating {len(cameras)} scripts...", total=len(cameras))
        
        for camera in cameras:
            script_name = f"start_cam_{camera['name']}.sh"
            script_names.append(script_name)
            script_path = os.path.join(output_dir, script_name)
            write_file(script_path, generate_cam_script(camera))
            make_executable(script_path)
            progress.advance(task)

    start_all_path = os.path.join(output_dir, "start_all_cams.sh")
    write_file(start_all_path, generate_start_all(script_names))
    make_executable(start_all_path)

    console.print(Panel(
        f"[green]Successfully generated scripts![/green]\n\n"
        f"Output Directory: [bold]{output_dir}[/bold]\n"
        f"Master Script: [bold]{start_all_path}[/bold]",
        title="Generation Complete"
    ))


def interactive_setup(config_path, output_dir):
    print_banner()
    console.print(Rule("Step 1/4: Scan Environment"))
    
    devices = gather_device_info()
    if not devices:
        console.print("[bold red]No /dev/video* devices found.[/bold red]")
        console.print("Make sure your camera is connected. If using Android, open the USB webcam app.")
        sys.exit(1)

    print_device_table(devices)
    
    console.print("\n")
    console.print(Rule("Step 2/4: Selection"))
    console.print(f"Detected devices: [bold cyan]{len(devices)}[/bold cyan]")
    
    camera_count = IntPrompt.ask("How many cameras do you want to configure?", default=2)
    while camera_count > len(devices):
        console.print("[red]Count exceeds detected devices.[/red]")
        camera_count = IntPrompt.ask("How many cameras do you want to configure?", default=len(devices))
        if camera_count <= 0: return

    console.print("[dim]Select device IDs separated by comma (e.g. 0,2).[/dim]")
    while True:
        raw = Prompt.ask("Select device IDs")
        try:
            selections = parse_selection_with_count(raw, len(devices), camera_count)
            break
        except ValueError as exc:
            console.print(f"[red]Invalid selection:[/red] {exc}")

    cameras = []
    console.print("\n")
    console.print(Rule("Step 3/4: Configuration"))
    
    used_names = set()
    for idx_sel in selections:
        dev = devices[idx_sel]
        
        console.print(Panel(f"Configuring Device [bold cyan]{idx_sel}[/bold cyan] ({dev['path']})", border_style="blue"))
        
        if dev.get("by_id") or dev.get("by_path"):
            console.print(f"[dim]Stable path: {dev.get('by_id') or dev.get('by_path')}[/dim]")
        
        default_name = f"cam{idx_sel}"
        name = sanitize_name(Prompt.ask("Friendly name", default=default_name))
        while name in used_names:
            console.print("[red]Name already used.[/red]")
            name = sanitize_name(Prompt.ask("Friendly name"))
        used_names.add(name)

        default_width, default_height = resolve_default_size(dev)
        width = IntPrompt.ask("Width", default=default_width)
        height = IntPrompt.ask("Height", default=default_height)
        fps = FloatPrompt.ask("FPS", default=30.0)

        namespace = prompt_namespace(f"/hdas/camera_{name}")
        frame_id = prompt_rel_topic(f"{name}_camera", "Frame ID")
        image_topic = prompt_rel_topic("color/image_raw", "Image topic")

        cameras.append(
            {
                "name": name,
                "device_path": choose_device_path(dev),
                "width": width,
                "height": height,
                "fps": fps,
                "namespace": namespace,
                "frame_id": frame_id,
                "image_topic": image_topic,
            }
        )

    ensure_dir(os.path.dirname(config_path))
    ensure_dir(output_dir)

    console.print("\n")
    console.print(Rule("Step 4/4: Review"))
    
    table = Table(title="Configuration Summary")
    table.add_column("Name", style="bold")
    table.add_column("Path", style="dim", overflow="fold")
    table.add_column("Config")
    table.add_column("Topic")

    for camera in cameras:
        config_str = f"{camera['width']}x{camera['height']} @ {camera['fps']}fps"
        topic = join_topic(camera['namespace'], camera['image_topic'])
        table.add_row(camera['name'], camera['device_path'], config_str, topic)
        
    console.print(table)
    console.print()

    if not Confirm.ask("Proceed to generate scripts?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    config = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cameras": cameras,
    }
    write_file(config_path, json.dumps(config, indent=2))

    script_names = []
    for camera in cameras:
        script_name = f"start_cam_{camera['name']}.sh"
        script_names.append(script_name)
        script_path = os.path.join(output_dir, script_name)
        write_file(script_path, generate_cam_script(camera))
        make_executable(script_path)

    start_all_path = os.path.join(output_dir, "start_all_cams.sh")
    write_file(start_all_path, generate_start_all(script_names))
    make_executable(start_all_path)

    console.print(Panel(
        f"[green]Setup Complete![/green]\n\n"
        f"Config saved to: [bold]{config_path}[/bold]\n"
        f"Scripts generated in: [bold]{output_dir}[/bold]\n\n"
        f"Run all cameras with:\n[bold on black]{start_all_path}[/bold on black]",
        title="Success",
        border_style="green"
    ))
    
    console.print("[bold]Quick Verification Command:[/bold]")
    for camera in cameras:
        topic = join_topic(camera["namespace"], camera["image_topic"])
        console.print(f"  ros2 run image_view image_view --ros-args -r image:={topic}")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive camera setup CLI for ROS2 cam2image scripts."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to config file to write/read.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated start scripts.",
    )
    parser.add_argument(
        "--from-config",
        action="store_true",
        help="Generate scripts from an existing config without prompts.",
    )

    args = parser.parse_args()

    if args.from_config:
        generate_from_config(args.config, args.output_dir)
        return

    interactive_setup(args.config, args.output_dir)


if __name__ == "__main__":
    main()
