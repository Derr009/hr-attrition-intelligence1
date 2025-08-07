import sqlite3

conn = sqlite3.connect("data/hr_analytics.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM merged_data")
count = cursor.fetchone()[0]
rows = cursor.fetchall()
for row in rows:
    print(row)
