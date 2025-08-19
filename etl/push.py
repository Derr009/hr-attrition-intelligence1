from urllib.parse import quote_plus

from merger import merge_with_faker
from sqlalchemy import create_engine
import httplib2
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# --- MySQL Setup ---
MYSQL_USER = "root"
MYSQL_PASSWORD = "NewP@ssw0rd123!"
MYSQL_HOST = "localhost"
MYSQL_DB = "hr_analytics"

# Encode the password safely
encoded_password = quote_plus(MYSQL_PASSWORD)

engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:3306/{MYSQL_DB}"
)

# --- Google Sheets Setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(
    "/home/nineleaps/Desktop/etl/capstone-467705-65af793df23b.json",
    scopes=SCOPES
)
unverified_http = httplib2.Http(disable_ssl_certificate_validation=True)
authorized_http = AuthorizedHttp(CREDS, http=unverified_http)
service = build("sheets", "v4", http=authorized_http)

SPREADSHEET_ID = "1vrGu57Y1w7OMQjRNkxyYZK9mZ1gsv4KlnY4XiylxJg4"
SHEET_NAME = "Master Data"

def append_to_sheets(df):
    body = {"values": df.astype(str).values.tolist()}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:Z",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    print(f"✅ Pushed {len(df)} rows to Google Sheets.")

if __name__ == "__main__":
    df_final = merge_with_faker(fake_count=250)

    # Push to MySQL
    df_final.to_sql("merged_data", engine, if_exists="append", index=False)
    print(f"✅ Inserted {len(df_final)} rows into MySQL.")

    # Push to Google Sheets
    append_to_sheets(df_final)
