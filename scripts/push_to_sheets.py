"""
Push cleaned data and KPI tables to Google Sheets
Sheet: https://docs.google.com/spreadsheets/d/1b-dBObPNXYCCjQPKyWmR9eqvKrvcL8o_h1rJSOabmjg/
"""
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey-patch requests to ignore SSL verification
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

class SSLBypassAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = ssl._create_unverified_context()
        return super().init_poolmanager(*args, **kwargs)

requests.Session().mount('https://', SSLBypassAdapter())

import pandas as pd
import sqlite3
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import numpy as np

# === CONFIG ===
SHEET_ID = "1f8TCoAxGtT4tsdKas4lv7G4rlD0OfMivGztRHstRzPo"
CREDENTIALS_PATH = "capstone-468106-a5f2815bbb80.json"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hr_analytics.db"
CLEANED_CSV = Path(__file__).resolve().parent.parent / "data" / "reviews_enriched_latest.csv"

# === Authenticate Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID)

def push_df_to_sheet(df, worksheet_name):
    try:
        worksheet = sheet.worksheet(worksheet_name)
        worksheet.clear()
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=worksheet_name, rows=str(len(df)+5), cols=str(len(df.columns)+5))
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# === 1. Push Cleaned Data ===
df_cleaned = pd.read_csv(CLEANED_CSV)
push_df_to_sheet(df_cleaned, "Cleaned Data")

# === 2. Connect to DB for SQL-based KPIs ===
conn = sqlite3.connect(DB_PATH)

# --- KPI 1: Overall Attrition Rate (monthly, quarterly, yearly) ---
df_attrition_month = pd.read_sql_query('''
    SELECT strftime('%Y-%m', exit_date) AS month, COUNT(*) AS attritions
    FROM reviews_enriched
    WHERE status='Exited' AND exit_date IS NOT NULL
    GROUP BY month
    ORDER BY month
''', conn)
push_df_to_sheet(df_attrition_month, "Attrition Rate Monthly")

df_attrition_year = pd.read_sql_query('''
    SELECT strftime('%Y', exit_date) AS year, COUNT(*) AS attritions
    FROM reviews_enriched
    WHERE status='Exited' AND exit_date IS NOT NULL
    GROUP BY year
    ORDER BY year
''', conn)
push_df_to_sheet(df_attrition_year, "Attrition Rate Yearly")

# --- KPI 2: Voluntary vs. Involuntary Attrition ---
df_vol_invol = pd.read_sql_query('''
    SELECT attrition_reason, COUNT(*) AS count
    FROM reviews_enriched
    WHERE status='Exited'
    GROUP BY attrition_reason
    ORDER BY count DESC
''', conn)
push_df_to_sheet(df_vol_invol, "Voluntary vs Involuntary")

# --- KPI 3: Department-wise Attrition ---
df_dept_attrition = pd.read_sql_query('''
    SELECT department, COUNT(*) AS attritions
    FROM reviews_enriched
    WHERE status='Exited'
    GROUP BY department
    ORDER BY attritions DESC
''', conn)
push_df_to_sheet(df_dept_attrition, "Dept Attrition")

# --- KPI 4: Location-wise Attrition ---
df_loc_attrition = pd.read_sql_query('''
    SELECT location, COUNT(*) AS attritions
    FROM reviews_enriched
    WHERE status='Exited'
    GROUP BY location
    ORDER BY attritions DESC
''', conn)
push_df_to_sheet(df_loc_attrition, "Location Attrition")

# --- KPI 5: Early Attrition (within 1 year) ---
df_early_attrition = pd.read_sql_query('''
    SELECT COUNT(*) AS early_attritions
    FROM reviews_enriched
    WHERE status='Exited' AND CAST((julianday(exit_date) - julianday(joining_date))/365.25 AS FLOAT) < 1
''', conn)
push_df_to_sheet(df_early_attrition, "Early Attrition")

# --- KPI 6: Tenure-based Attrition ---
df_tenure = pd.read_sql_query('''
    SELECT 
        CASE 
            WHEN tenure < 1 THEN '<1 year'
            WHEN tenure < 3 THEN '1-3 years'
            WHEN tenure < 5 THEN '3-5 years'
            ELSE '5+ years'
        END AS tenure_bucket,
        COUNT(*) AS attritions
    FROM (
        SELECT *, CAST((julianday(exit_date) - julianday(joining_date))/365.25 AS FLOAT) AS tenure
        FROM reviews_enriched
        WHERE status='Exited' AND exit_date IS NOT NULL AND joining_date IS NOT NULL
    )
    GROUP BY tenure_bucket
    ORDER BY tenure_bucket
''', conn)
push_df_to_sheet(df_tenure, "Tenure Attrition")

# --- KPI 7: Performance-based Attrition ---
df_perf_attrition = pd.read_sql_query('''
    SELECT performance_rating, COUNT(*) AS attritions
    FROM reviews_enriched
    WHERE status='Exited'
    GROUP BY performance_rating
    ORDER BY performance_rating
''', conn)
push_df_to_sheet(df_perf_attrition, "Perf Attrition")

# --- KPI 8: Average Engagement Score ---
df_engagement = pd.read_sql_query('''
    SELECT AVG(engagement_score) AS avg_engagement
    FROM reviews_enriched
    WHERE engagement_score IS NOT NULL
''', conn)
push_df_to_sheet(df_engagement, "Engagement")

# --- KPI 9: Sentiment Score from reviews (trend) ---
# Simple sentiment: count of positive/negative words in Pros/Cons
# (For demo, you can replace with TextBlob/VADER for better results)
def simple_sentiment(text):
    pos_words = ["good", "great", "excellent", "positive", "happy", "support", "growth", "flexible", "best", "learning"]
    neg_words = ["bad", "poor", "stress", "negative", "problem", "issue", "worst", "overwork", "toxic", "leave"]
    score = 0
    if pd.isna(text):
        return 0
    text = str(text).lower()
    for w in pos_words:
        if w in text:
            score += 1
    for w in neg_words:
        if w in text:
            score -= 1
    return score

df_cleaned['sentiment_score'] = df_cleaned['Pros'].apply(simple_sentiment) - df_cleaned['Cons'].apply(simple_sentiment)
df_sentiment_trend = df_cleaned.groupby(df_cleaned['review_date'].str[:7])["sentiment_score"].mean().reset_index().rename(columns={"review_date": "month", "sentiment_score": "avg_sentiment"})
push_df_to_sheet(df_sentiment_trend, "Sentiment Trend")

# --- KPI 10: Department-wise Sentiment vs. Attrition ---
df_dept_sentiment = df_cleaned.groupby("department")["sentiment_score"].mean().reset_index().rename(columns={"department": "department", "sentiment_score": "avg_sentiment"})
df_dept_sentiment = pd.merge(df_dept_sentiment, df_dept_attrition, on="department", how="left")
push_df_to_sheet(df_dept_sentiment, "Sentiment vs Attrition")

# --- KPI 11: Top recurring complaint themes (Cons column, simple word count) ---
from collections import Counter
import re
all_cons = " ".join(df_cleaned["Cons"].dropna().astype(str).tolist()).lower()
words = re.findall(r"\b\w+\b", all_cons)
stopwords = set(["the", "and", "to", "of", "in", "a", "is", "for", "on", "with", "as", "at", "by", "an", "be", "are", "it", "from", "that", "this", "or", "but", "if", "not", "was", "so", "they", "we", "you", "their", "has", "have", "had", "were", "which", "can", "will", "more", "all", "than", "when", "who", "our", "my", "your", "he", "she", "them"])
filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
top_complaints = Counter(filtered_words).most_common(10)
df_complaints = pd.DataFrame(top_complaints, columns=["complaint_theme", "count"])
push_df_to_sheet(df_complaints, "Complaint Themes")

conn.close()
print("All data and KPIs pushed to Google Sheets!")
