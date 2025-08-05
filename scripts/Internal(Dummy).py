import pandas as pd
import random
import datetime

def generate_hrms_dummy_data(num_employees=300):
    departments = ['Engineering', 'Product', 'HR', 'Sales', 'Marketing', 'Finance', 'Operations']
    locations = ['Bangalore', 'Hyderabad', 'Pune', 'Remote']
    designations = ['Software Engineer', 'Manager', 'Analyst', 'HRBP', 'Consultant']
    attrition_reasons = ['Better Opportunity', 'Work-Life Balance', 'Relocation', 'Compensation', 'Personal Reasons']
    salary_bands = ['A', 'B', 'C']  # A = low, B = mid, C = high
    
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
            "name": f"Employee {emp_id}",
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
    
    return pd.DataFrame(data)

# Generate dataset
df_hrms = generate_hrms_dummy_data(300)
df_hrms.to_csv("hrms_dummy_data.csv", index=False)
print("HRMS dummy data generated: hrms_dummy_data.csv")
