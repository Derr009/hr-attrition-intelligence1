import os
from urllib.parse import quote_plus
from merger import merge_with_faker
from sqlalchemy import create_engine
import httplib2
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# --- PostgreSQL/Supabase Setup ---
POSTGRES_USER = os.getenv("SUPABASE_USER")
POSTGRES_PASSWORD = os.getenv("SUPABASE_PASSWORD")
POSTGRES_HOST = os.getenv("SUPABASE_HOST", "aws-1-ap-south-1.pooler.supabase.com")
POSTGRES_PORT = os.getenv("SUPABASE_PORT", "5432")
POSTGRES_DB = os.getenv("SUPABASE_DB", "postgres")

encoded_password = quote_plus(POSTGRES_PASSWORD)

engine = create_engine(
    f"postgresql+psycopg2://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode=require"
)

# --- Google Sheets Setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH")
CREDS = Credentials.from_service_account_file(GOOGLE_CREDS_PATH, scopes=SCOPES)
unverified_http = httplib2.Http(disable_ssl_certificate_validation=True)
authorized_http = AuthorizedHttp(CREDS, http=unverified_http)
service = build("sheets", "v4", http=authorized_http)

SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Master Data")

def append_to_sheets(df):
    body = {"values": df.astype(str).values.tolist()}
    # Optional: clear sheet for full sync
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:Z"
    ).execute()
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:Z",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    print(f"✅ Pushed {len(df)} rows to Google Sheets.")

if __name__ == "__main__":
    df_final = merge_with_faker(fake_count=250)

    # Push to PostgreSQL
    try:
        df_final.to_sql("merged_data", engine, if_exists="append", index=False)
        print(f"✅ Inserted {len(df_final)} rows into PostgreSQL.")
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")

    # Push to Google Sheets
    try:
        append_to_sheets(df_final)
    except Exception as e:
        print(f"❌ Google Sheets Error: {e}")
