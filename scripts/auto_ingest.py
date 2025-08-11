"""
Scheduled Auto-Ingestion Script
Runs the full ETL pipeline (scraping, HRMS generation, merging) and logs output.
Intended to be triggered by cron or a scheduler.
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_ROOT / "venv" / "bin" / "python"
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file per run (timestamped)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOGS_DIR / f"auto_ingest_{timestamp}.log"

# The ETL pipeline entry point
pipeline_script = PROJECT_ROOT / "main.py"

# Prefer the project's venv Python if it exists; otherwise, use the current interpreter
python_exec = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
cmd = [str(python_exec), str(pipeline_script)]

with open(log_file, "w") as f:
    f.write(f"=== Auto-Ingestion Run: {timestamp} ===\n")
    f.write(f"Command: {' '.join(cmd)}\n\n")
    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
    proc.wait()
    f.write(f"\n=== Run Complete. Exit code: {proc.returncode} ===\n")

print(f"Auto-ingestion complete. Log saved to {log_file}")
