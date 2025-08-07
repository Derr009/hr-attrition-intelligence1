import sqlite3

conn = sqlite3.connect("data/hr_analytics.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM merged_data;")
conn.commit()
conn.close()
print("Dropped merged_data table.")

