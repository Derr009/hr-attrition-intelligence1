import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import os
import random

def merge_hrms_reviews():
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    backup_dir = project_root / "Backup" / "merged"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    # Load datasets
    hrms_path = data_dir / "hrms_latest.csv"
    reviews_path = data_dir / "nineleaps-technology-solutions_reviews_latest.csv"
    df_hrms = pd.read_csv(hrms_path, parse_dates=["joining_date", "exit_date"])
    df_reviews = pd.read_csv(reviews_path, parse_dates=["ReviewDate"])

    # --- Clean ---
    df_hrms['department'] = df_hrms['department'].str.strip()
    df_reviews['Department'] = df_reviews['Department'].str.replace('Department', '', regex=False).str.strip()

    # --- Map each review to a random employee in the same department (if possible) ---
    enriched_reviews = []
    for _, review in df_reviews.iterrows():
        dept_employees = df_hrms[df_hrms['department'].str.lower() == review['Department'].lower()]
        if dept_employees.empty:
            mapped_emp = df_hrms.sample(1).iloc[0]  # fallback to random employee
        else:
            mapped_emp = dept_employees.sample(1).iloc[0]

        enriched_reviews.append({
            "review_id": review['ReviewID'],
            "company": review['Company'],
            "job_title": review['JobTitle'],
            "department": review['Department'],
            "location": review['Location'],
            "review_date": review['ReviewDate'],
            "overall_rating": review['OverallRating'],
            "pros": review['Pros'],
            "cons": review['Cons'],
            "employee_id": mapped_emp['employee_id'],
            "name": mapped_emp['name'],
            "status": mapped_emp['status'],
            "joining_date": mapped_emp['joining_date'],
            "exit_date": mapped_emp['exit_date'],
            "engagement_score": mapped_emp['engagement_score'],
            "performance_rating": mapped_emp['performance_rating'],
            "salary_band": mapped_emp['salary_band'],
            "gender": mapped_emp['gender'],
            "age": mapped_emp['age']
        })

    merged_df = pd.DataFrame(enriched_reviews)

    # --- Save to CSV ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    latest_path = data_dir / "reviews_enriched_latest.csv"
    backup_path = backup_dir / f"reviews_enriched_{timestamp}.csv"
    merged_df.to_csv(latest_path, index=False)
    merged_df.to_csv(backup_path, index=False)
    print(f"Saved enriched dataset to {latest_path} and archived version to {backup_path}")

    # --- Insert into SQLite ---
    db_path = project_root / "data" / "hr_analytics.db"
    conn = sqlite3.connect(db_path)
    merged_df.to_sql("reviews_enriched", conn, if_exists="append", index=False)
    conn.close()
    print("Inserted enriched data into SQLite.")

    return merged_df

if __name__ == "__main__":
    df_merged = merge_hrms_reviews()
    print(df_merged.head())
