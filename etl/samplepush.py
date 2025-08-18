import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# === Step 1: Authenticate with Google ===
scopes = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

# Replace with your service account JSON key file
creds = Credentials.from_service_account_file("capstone-467705-65af793df23b.json", scopes=scopes)
client = gspread.authorize(creds)

# === Step 2: Generate a small dataset ===
data = {
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [25, 30, 35, 40],
    "City": ["NY", "LA", "Chicago", "Houston"]
}
df = pd.DataFrame(data)

# === Step 3: Open your Google Sheet ===
# Replace with your Google Sheet ID (from the URL)
SHEET_ID = "1vrGu57Y1w7OMQjRNkxyYZK9mZ1gsv4KlnY4XiylxJg4"
sheet = client.open_by_key(SHEET_ID)
worksheet = sheet.sheet1  # First sheet (you can also use .worksheet("SheetName"))

# === Step 4: Clear existing content & upload new data ===
worksheet.clear()  # Clears old data

# Add column headers + rows from DataFrame
worksheet.update([df.columns.values.tolist()] + df.values.tolist())

print("✅ Data pushed successfully to Google Sheets!")
