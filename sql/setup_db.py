import sqlite3
from pathlib import Path

project_root = Path(__file__).resolve().parent
db_path = project_root / "data" / "hr_analytics.db"
schema_path = project_root / "sql" / "schema.sql"

# Connect and create
conn = sqlite3.connect(db_path)
with open(schema_path, "r") as f:
    conn.executescript(f.read())
conn.commit()
conn.close()

print(f"Database initialized at {db_path} with reviews_enriched schema.")
