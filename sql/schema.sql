DROP TABLE IF EXISTS reviews_enriched;

CREATE TABLE reviews_enriched (
    review_id TEXT PRIMARY KEY,
    company TEXT,
    job_title TEXT,
    department TEXT,
    location TEXT,
    review_date DATE,
    overall_rating REAL,
    pros TEXT,
    cons TEXT,
    employee_id TEXT,
    name TEXT,
    status TEXT,
    joining_date DATE,
    exit_date DATE,
    engagement_score REAL,
    performance_rating INTEGER,
    salary_band TEXT,
    gender TEXT,
    age INTEGER
);
