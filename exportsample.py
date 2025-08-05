import sqlite3
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

# --- Google Sheets Setup ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("capstone-467705-c7302abce011.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1b-dBObPNXYCCjQPKyWmR9eqvKrvcL8o_h1rJSOabmjg")  # Google Sheet ID

# --- Connect to DB ---
project_root = Path(__file__).resolve().parent
db_path = project_root / "data" / "hr_analytics.db"
conn = sqlite3.connect(db_path)


# --- Sample Queries ---
queries = {
    "Employee_Count_By_Department": """
        SELECT department, COUNT(*) AS total_employees 
        FROM reviews_enriched GROUP BY department
    """,
    "Attrition_By_Department": """
        SELECT department, SUM(CASE WHEN status='Exited' THEN 1 ELSE 0 END) AS attritions
        FROM reviews_enriched GROUP BY department
    """,
    "Average_Performance_By_Department": """
        SELECT department, AVG(performance_rating) AS avg_performance
        FROM reviews_enriched GROUP BY department
    """,
    "Salary_Band_Distribution": """
        SELECT salary_band, COUNT(*) AS count FROM reviews_enriched GROUP BY salary_band
    """,
    "Engagement_By_Location": """
        SELECT location, AVG(engagement_score) AS avg_engagement
        FROM reviews_enriched GROUP BY location
    """
}

# --- Write each query result to a separate sheet ---
for tab_name, query in queries.items():
    df = pd.read_sql_query(query, conn)

    try:
        worksheet = sheet.worksheet(tab_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=tab_name, rows=str(len(df)+5), cols=str(len(df.columns)+5))

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Data exported to Google Sheets successfully.")
