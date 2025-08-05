import pandas as pd

# Load datasets
reviews = pd.read_csv("nineleaps-technology-solutions_reviews.csv")
hrms = pd.read_csv("hrms_dummy_data.csv")

# --- Clean & Transform Reviews ---
reviews['ReviewDate'] = pd.to_datetime(reviews['ReviewDate'], errors='coerce')
reviews['review_month'] = reviews['ReviewDate'].dt.to_period('M').astype(str)
reviews['Department'] = reviews['Department'].fillna("Unknown")
reviews['Location'] = reviews['Location'].fillna("Unknown")

reviews_agg = reviews.groupby(['Department', 'Location', 'review_month']).agg(
    avg_review_rating=('OverallRating', 'mean'),
    review_count=('OverallRating', 'count')
).reset_index()

# --- Clean & Transform HRMS ---
hrms['exit_date'] = pd.to_datetime(hrms['exit_date'], errors='coerce')
hrms['exit_month'] = hrms['exit_date'].dt.to_period('M').astype(str)
hrms['department'] = hrms['department'].fillna("Unknown")
hrms['location'] = hrms['location'].fillna("Unknown")

hrms_agg = hrms.groupby(['department', 'location', 'exit_month']).agg(
    attrition_count=('employee_id', 'count'),
    avg_engagement_score=('engagement_score', 'mean'),
    avg_performance_rating=('performance_rating', 'mean')
).reset_index()

# Rename columns for merging
hrms_agg.rename(columns={
    'department': 'Department',
    'location': 'Location',
    'exit_month': 'review_month'
}, inplace=True)

# --- Merge Datasets ---
merged = pd.merge(
    hrms_agg, reviews_agg,
    on=['Department', 'Location', 'review_month'],
    how='outer'
)

# Fill missing values
merged[['attrition_count', 'avg_engagement_score', 'avg_performance_rating', 'avg_review_rating', 'review_count']] = \
    merged[['attrition_count', 'avg_engagement_score', 'avg_performance_rating', 'avg_review_rating', 'review_count']].fillna(0)

# Save merged dataset
merged.to_csv("merged_dataset.csv", index=False)
print("Merged dataset saved to merged_dataset.csv")
