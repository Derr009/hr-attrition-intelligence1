import pandas as pd
import random
import datetime
from pathlib import Path
import os
from datetime import datetime as dt

def generate_hrms_dummy_data(num_employees=300, save_csv=True):
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    backup_dir = project_root / "Backup" / "hrms"

    # Finalized Departments & Locations
    departments = [
        'IT Support Department',
        'Software Development Department',
        'HR Operations Department',
        'DBA / Data warehousing Department',
        'Data Science & Machine Learning Department',
        'Business Intelligence & Analytics Department',
        'UI / UX Department',
        'Quality Assurance and Testing Department',
        'Production & Manufacturing Department',
        'Data Science & Analytics - Other Department',
        'Engineering Department',
        'Marketing Department',
        'Data Department',
        'Product Management - Technology Department',
        'Technology / IT Department',
        'Recruitment & Talent Acquisition Department',
        'Operations Support Department'
    ]
    locations = ['Bangalore / Bengaluru', 'Hyderabad / Secunderabad', 'Nandigama']

    # Finalized Designations (Job Titles)
    designations = [
        'Data Engineer', 'Lead Software Engineer',
        'Software Development Engineer II', 'Front end Engineer',
        'Associate', 'HR Executive', 'Software Development Engineer 1',
        'Software Engineer', 'Data Analyst 1', 'Data Analyst',
        'UI UX Developer', 'Software Development Engineer',
        'Quality Engineer', 'Software Developer', 'Principal Engineer',
        'Junior Engineer', 'Marketing Executive',
        'Senior Quality Engineer', 'Sdet', 'SDE',
        'Principal Software Engineer', 'Associate Project Manager',
        'QA Engineer', 'Senior Talent Partner', 'Senior Software Engineer',
        'Member Technical Staff 2', 'SDE-2', 'Technical Staff Member 3',
        'Senior QA Engineer'
    ]

    attrition_reasons = ['Better Opportunity', 'Work-Life Balance', 'Relocation', 'Compensation', 'Personal Reasons']
    salary_bands = ['A', 'B', 'C']  # A = low, B = mid, C = high
    indian_names = ['Aarav', 'Vivaan', 'Aditya', 'Diya', 'Ishaan', 'Ananya', 'Riya', 'Karthik', 'Sneha', 'Arjun',
                    'Priya', 'Rahul', 'Meera', 'Siddharth', 'Aisha', 'Vikram', 'Lakshmi', 'Rohan', 'Pooja', 'Krishna']

    data = []
    start_date = datetime.date(2018, 1, 1)
    end_date = datetime.date(2025, 1, 1)

    for emp_id in range(1, num_employees + 1):
        joining = start_date + datetime.timedelta(days=random.randint(0, 2000))
        is_exited = random.choice([True, False])
        exit_date = joining + datetime.timedelta(days=random.randint(200, 2000)) if is_exited else None
        if exit_date and exit_date > end_date:
            exit_date = None
            is_exited = False

        data.append({
            "employee_id": f"EMP{emp_id:04d}",
            "name": random.choice(indian_names) + " " + random.choice(['Sharma', 'Reddy', 'Patel', 'Iyer', 'Nair', 'Singh']),
            "department": random.choice(departments),
            "location": random.choice(locations),
            "designation": random.choice(designations),
            "joining_date": joining,
            "exit_date": exit_date,
            "status": "Exited" if is_exited else "Active",
            "attrition_reason": random.choice(attrition_reasons) if is_exited else "",
            "engagement_score": round(random.uniform(4, 9), 1),
            "performance_rating": random.randint(1, 5),
            "salary_band": random.choice(salary_bands),
            "gender": random.choice(['Male', 'Female']),
            "age": random.randint(22, 50)
        })

    df = pd.DataFrame(data)

    # Save to CSVs using backup utility
    if save_csv:
        from etl.utils import save_with_backup
        latest_path = data_dir / "hrms_latest.csv"
        save_with_backup(df, latest_path, backup_dir, prefix="hrms_data")

    return df

if __name__ == "__main__":
    df_hrms = generate_hrms_dummy_data(300)
    print(df_hrms.head())
