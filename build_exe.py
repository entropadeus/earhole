#!/usr/bin/env python3
"""
Build standalone Earhole executable using PyInstaller.
"""

import subprocess
import sys
import os
from pathlib import Path


def build():
    project_dir = Path(__file__).parent
    main_script = project_dir / "main.py"
    icon_path = project_dir / "assets" / "earhole.ico"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Earhole",
        "--onefile",
        "--windowed",  # No console window
        "--icon", str(icon_path),

        # Collect all needed packages
        "--collect-all", "faster_whisper",
        "--collect-all", "ctranslate2",
        "--collect-all", "tokenizers",
        "--collect-all", "huggingface_hub",

        # Hidden imports
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "pynput.mouse._win32",
        "--hidden-import", "sounddevice",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "PIL.ImageDraw",
        "--hidden-import", "PIL.ImageTk",

        # Add src as data
        "--add-data", f"{project_dir / 'src'};src",
        "--add-data", f"{project_dir / 'assets'};assets",

        str(main_script)
    ]

    print("Building Earhole executable...")
    print("This may take several minutes...\n")
    print(f"Command: {' '.join(cmd[:10])}...")

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        exe_path = project_dir / "dist" / "Earhole.exe"
        print(f"\n{'='*50}")
        print(f"BUILD SUCCESSFUL!")
        print(f"{'='*50}")
        print(f"Executable: {exe_path}")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size_mb:.1f} MB")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()
