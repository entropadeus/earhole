#!/usr/bin/env python3
"""
Build script for creating the Earworm executable.
"""

import subprocess
import sys
import os
from pathlib import Path


def find_faster_whisper_data():
    """Find faster-whisper package location for bundling."""
    try:
        import faster_whisper
        return Path(faster_whisper.__file__).parent
    except ImportError:
        return None


def build():
    """Build the executable using PyInstaller."""
    project_dir = Path(__file__).parent
    main_script = project_dir / "src" / "app.py"

    # Base PyInstaller command
    icon_path = project_dir / "assets" / "earhole.ico"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Earworm",
        "--onefile",  # Single executable
        "--windowed",  # No console window (use --console for debugging)
        "--add-data", f"{project_dir / 'src'};src",
    ]

    # Add icon if it exists
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])

    # Add faster-whisper data if found
    fw_path = find_faster_whisper_data()
    if fw_path:
        cmd.extend(["--collect-all", "faster_whisper"])
        cmd.extend(["--collect-all", "ctranslate2"])

    # Hidden imports that PyInstaller might miss
    hidden_imports = [
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "sounddevice",
        "numpy",
        "PIL",
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # The main script
    cmd.append(str(main_script))

    print("Building Earworm executable...")
    print(f"Command: {' '.join(cmd)}")

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        print("\nBuild successful!")
        print(f"Executable: {project_dir / 'dist' / 'Earworm.exe'}")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()
