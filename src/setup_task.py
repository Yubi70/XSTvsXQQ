"""
setup_task.py — Registers a Windows Task Scheduler task to auto-start
the XST vs XQQ monitor at 9:00 AM every Mon-Fri.
Run once as Administrator: .venv\\Scripts\\python src\\setup_task.py

--- MANUAL COMMAND (run in an Admin terminal if the script fails) ---
schtasks /create /tn "XSTvsXQQ_Monitor" /tr "\"c:\Python\XSTvsXQQ\.venv\Scripts\python.exe\" \"c:\Python\XSTvsXQQ\src\monitor.py\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00 /rl HIGHEST /f

To remove the task manually:
schtasks /delete /tn "XSTvsXQQ_Monitor" /f
---
"""

import subprocess
import sys
import os

TASK_NAME   = "XSTvsXQQ_Monitor"
PYTHON_EXE  = os.path.join(os.path.dirname(sys.executable), "python.exe")  # console window visible
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "monitor.py")
START_TIME  = "09:00"
DAYS        = "MON,TUE,WED,THU,FRI"


def register_task() -> None:
    # Delete existing task if present (ignore errors)
    subprocess.run(
        ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
        capture_output=True
    )

    cmd = [
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", f'"{PYTHON_EXE}" "{SCRIPT_PATH}"',
        "/sc", "weekly",
        "/d", DAYS,
        "/st", START_TIME,
        "/rl", "HIGHEST",   # run with highest privileges
        "/f",               # force overwrite
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' created successfully.")
        print(f"  Runs  : {DAYS} at {START_TIME}")
        print(f"  Script: {SCRIPT_PATH}")
        print(f"  Stops : automatically at 16:30 ET")
    else:
        print(f"Failed to create task:\n{result.stderr}")
        print("\nTry running this script as Administrator.")


def remove_task() -> None:
    result = subprocess.run(
        ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Task '{TASK_NAME}' removed.")
    else:
        print(f"Could not remove task: {result.stderr}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_task()
    else:
        register_task()
