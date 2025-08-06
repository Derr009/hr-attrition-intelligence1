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
pipeline_script = PROJECT_ROOT / "etl" / "pipeline.py"

cmd = [str(VENV_PYTHON), str(pipeline_script)]

with open(log_file, "w") as f:
    f.write(f"=== Auto-Ingestion Run: {timestamp} ===\n")
    f.write(f"Command: {' '.join(cmd)}\n\n")
    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
    proc.wait()
    f.write(f"\n=== Run Complete. Exit code: {proc.returncode} ===\n")

print(f"Auto-ingestion complete. Log saved to {log_file}")
