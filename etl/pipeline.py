import sys
from pathlib import Path
import traceback

# Import our ETL modules
sys.path.append(str(Path(__file__).resolve().parent / "etl"))
from scraper import scrape_reviews
from hrms_generator import generate_hrms_dummy_data
from merger import merge_hrms_reviews

def main():
    try:
        print("=== HR Attrition Intelligence Pipeline Started ===")
        
        # Step 1: Scrape reviews
        print("\n[1/3] Scraping reviews...")
        df_reviews = scrape_reviews(company_slug="nineleaps-technology-solutions", num_pages=3)
        print(f"Scraped {len(df_reviews)} reviews.")
        
        # Step 2: Generate HRMS data
        print("\n[2/3] Generating HRMS dummy data...")
        df_hrms = generate_hrms_dummy_data(num_employees=300)
        print(f"Generated {len(df_hrms)} HRMS records.")
        
        # Step 3: Merge reviews with employees
        print("\n[3/3] Enriching reviews with employee data...")
        df_merged = merge_hrms_reviews()
        print(f"Merged dataset has {len(df_merged)} records.")
        
        print("\n=== Pipeline Completed Successfully! ===")
    
    except Exception as e:
        print("\n[ERROR] Pipeline failed!")
        traceback.print_exc()

if __name__ == "__main__":
    main()
