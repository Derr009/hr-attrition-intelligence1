import schedule
import time
import subprocess

# Path to your ETL script
SCRIPT_PATH = "main.py"

def run_etl():
    print("Starting ETL process...")
    subprocess.run(["python3", SCRIPT_PATH])
    print("ETL process completed.")

# Schedule: run every day at 10:00 AM
schedule.every().day.at("12:30").do(run_etl)

print("Scheduler started. Waiting for next run...")

while True:
    schedule.run_pending()
    time.sleep(1)
