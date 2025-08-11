import schedule
import time
import subprocess
import os
import sys
from pathlib import Path

# Resolve project root and prefer venv Python if available
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
PYTHON_EXEC = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)

# Path to your ETL script (entry point)
SCRIPT_PATH = PROJECT_ROOT / "main.py"

def run_etl():
    print("Starting ETL process...")
    cmd = [str(PYTHON_EXEC), str(SCRIPT_PATH)]
    subprocess.run(cmd, check=False)
    print("ETL process completed.")

# Schedule: run every day at the configured time (HH:MM, 24h). Default: 12:30
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "12:30")
schedule.every().day.at(SCHEDULE_TIME).do(run_etl)

print(f"Scheduler started. Next runs daily at {SCHEDULE_TIME}. Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(1)
