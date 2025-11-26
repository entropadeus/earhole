#!/usr/bin/env python3
"""
Adds Earhole to Windows startup.
Creates a shortcut in the Startup folder.
"""

import os
import sys
from pathlib import Path


def get_startup_folder() -> Path:
    """Get the Windows Startup folder path."""
    return Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def create_shortcut(target: Path, shortcut_path: Path, working_dir: Path, icon_path: Path = None):
    """Create a Windows shortcut (.lnk file)."""
    try:
        import subprocess

        icon_line = ""
        if icon_path and icon_path.exists():
            icon_line = f'$Shortcut.IconLocation = "{icon_path}"'

        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.WorkingDirectory = "{working_dir}"
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Earhole - Speech to Text"
{icon_line}
$Shortcut.Save()
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"PowerShell error: {result.stderr}")
            return False
        return True

    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


def install():
    """Install to startup."""
    project_dir = Path(__file__).parent.resolve()
    pythonw = project_dir / "venv" / "Scripts" / "pythonw.exe"
    main_script = project_dir / "main.py"
    icon_path = project_dir / "assets" / "earhole.ico"

    if not pythonw.exists():
        print(f"Error: Virtual environment not found at {pythonw}")
        print("Run setup.bat first to create the virtual environment.")
        return False

    startup_folder = get_startup_folder()
    shortcut_path = startup_folder / "Earhole.lnk"

    # Create launcher batch file
    launcher = project_dir / "launch_earhole.bat"
    launcher.write_text(f'''@echo off
cd /d "{project_dir}"
start "" "{pythonw}" "{main_script}"
''')

    if create_shortcut(launcher, shortcut_path, project_dir, icon_path):
        print(f"Success! Earhole will now start with Windows.")
        print(f"Shortcut created at: {shortcut_path}")
        return True
    else:
        print("Failed to create startup shortcut.")
        return False


def uninstall():
    """Remove from startup."""
    startup_folder = get_startup_folder()
    shortcut_path = startup_folder / "Earhole.lnk"

    if shortcut_path.exists():
        shortcut_path.unlink()
        print(f"Removed startup shortcut: {shortcut_path}")
        return True
    else:
        print("Startup shortcut not found.")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manage Earhole startup")
    parser.add_argument("--uninstall", action="store_true", help="Remove from startup")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        install()


if __name__ == "__main__":
    main()
