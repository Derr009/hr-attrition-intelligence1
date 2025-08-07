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
    reviews_path = data_dir / "nineleaps-technology-solutions_reviews.csv"
    enriched_path = data_dir / "reviews_enriched_latest.csv"

    df_hrms = pd.read_csv(hrms_path, parse_dates=["joining_date", "exit_date"])
    df_reviews = pd.read_csv(reviews_path, parse_dates=["ReviewDate"])

    # Load existing enriched reviews if present
    if enriched_path.exists():
        existing_enriched_df = pd.read_csv(enriched_path, parse_dates=["review_date"])
        already_merged_ids = set(existing_enriched_df['review_id'])
    else:
        existing_enriched_df = pd.DataFrame()
        already_merged_ids = set()

    # Filter only fresh (unmerged) reviews
    df_reviews = df_reviews[~df_reviews['ReviewID'].isin(already_merged_ids)]

    if df_reviews.empty:
        print("No new reviews to process.")
        return existing_enriched_df

    # Clean department fields
    df_hrms['department'] = df_hrms['department'].str.strip()
    df_reviews['Department'] = df_reviews['Department'].str.replace('Department', '', regex=False).str.strip()

    # Enrich fresh reviews
    enriched_reviews = []
    for _, review in df_reviews.iterrows():
        # 1. Try department + location match
        dept_loc_employees = df_hrms[
            (df_hrms['department'].str.lower() == review['Department'].lower()) &
            (df_hrms['location'].str.lower() == str(review['Location']).lower())
        ]
        if not dept_loc_employees.empty:
            mapped_emp = dept_loc_employees.sample(1).iloc[0]
        else:
            # 2. Try department only
            dept_employees = df_hrms[df_hrms['department'].str.lower() == review['Department'].lower()]
            if not dept_employees.empty:
                mapped_emp = dept_employees.sample(1).iloc[0]
            else:
                # 3. Fallback: any employee
                mapped_emp = df_hrms.sample(1).iloc[0]

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

    new_enriched_df = pd.DataFrame(enriched_reviews)

    # Concatenate with previous data (incremental update)
    full_enriched_df = pd.concat([existing_enriched_df, new_enriched_df], ignore_index=True)

    # Save with backup
    from etl.utils import save_with_backup
    save_with_backup(full_enriched_df, enriched_path, backup_dir, prefix="reviews_enriched")

    # --- Insert only new data to SQLite ---
    db_path = project_root / "data" / "hr_analytics.db"
    conn = sqlite3.connect(db_path)

    # If table exists, append only new records
    new_enriched_df.to_sql("merged_data", conn, if_exists="append", index=False)
    conn.close()
    print(f"Inserted {len(new_enriched_df)} new records into SQLite.")

    return new_enriched_df

if __name__ == "__main__":
    df_merged = merge_hrms_reviews()
    print(df_merged.head())
