import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
def parse_review_block(review_meta, soup):
    """
    Parses a single review block to extract information.
    This function links the hidden schema.org metadata (in a <span>) with the
    corresponding visible review content (in a <div>) using their shared 'id'.
    Args:
        review_meta (bs4.element.Tag): The BeautifulSoup tag for the <span itemscope...> tag.
        soup (bs4.BeautifulSoup): The BeautifulSoup object for the entire page.
    Returns:
        dict: A dictionary of the parsed review data, or None if the review ID is missing.
    """
    # Get the unique ID from the metadata span to link it with the visible div
    review_id = review_meta.get('id')
    if not review_id:
        return None
    # --- Extract most data from the hidden metadata (more reliable) JIFFIN ---
    company = review_meta.select_one('meta[itemprop="name"]')['content'] if review_meta.select_one('meta[itemprop="name"]') else ""
    author_span = review_meta.find('span', itemprop="author")
    job_title = author_span.select_one('meta[itemprop="jobTitle"]')['content'] if author_span and author_span.select_one('meta[itemprop="jobTitle"]') else ""
    location = author_span.select_one('meta[itemprop="workLocation"]')['content'] if author_span and author_span.select_one('meta[itemprop="workLocation"]') else ""
    review_date = review_meta.select_one('meta[itemprop="datePublished"]')['content'] if review_meta.select_one('meta[itemprop="datePublished"]') else ""
    rating = review_meta.select_one('meta[itemprop="ratingValue"]')['content'] if review_meta.select_one('meta[itemprop="ratingValue"]') else ""
    # Extract Likes (Pros) and Dislikes (Cons) from the full review body text
    pros, cons = "", ""
    review_body_span = review_meta.find('span', itemprop='reviewBody')
    if review_body_span:
        full_text = review_body_span.text.replace('\xa0', ' ').strip()
        # Split the text by "Dislikes:" to separate pros and cons
        if "Dislikes:" in full_text:
            parts = full_text.split("Dislikes:")
            pros = parts[0].replace("Likes:", "").strip()
            cons = parts[1].strip()
        else:
            pros = full_text.replace("Likes:", "").strip()
    # --- Extract Department from the visible review div using the ID ---
    department = ""
    visible_review_div = soup.find('div', id=review_id)
    if visible_review_div:
        # The department is in a <p> tag inside a specific div
        info_container = visible_review_div.find('div', class_="flex mt-1")
        if info_container:
            p_tags = info_container.find_all('p')
            if p_tags:
                # The department is usually the last <p> tag and contains "Department"
                department_text = p_tags[-1].text.strip()
                if "Department" in department_text:
                    department = department_text
    return {
        "ReviewID": review_id,
        "Company": company,
        "JobTitle": job_title,
        "Department": department,
        "Location": location,
        "ReviewDate": review_date,
        "OverallRating": rating,
        "Pros": pros,
        "Cons": cons
    }
def scrape_ambitionbox_reviews(company_slug, num_pages=2, delay=1):
    base_url = f"https://www.ambitionbox.com/reviews/nineleaps-technology-solutions-reviews"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    reviews_data = []
    print(f"Starting scrape for company slug: '{company_slug}'")
    for page in range(1, num_pages + 1):
        page_url = f"{base_url}?page={page}"
        print(f"Scraping page {page}: {page_url}")
        try:
            res = requests.get(page_url, headers=headers)
            res.raise_for_status()  # Checks for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_url}: {e}")
            continue
        soup = BeautifulSoup(res.content, "html.parser")
        # This selector targets the hidden <span> tags containing schema.org metadata
        review_meta_tags = soup.find_all("span", attrs={"itemscope": True, "itemtype": "https://schema.org/Review"})
        if not review_meta_tags:
            print(f"No reviews found on page {page}. This could be the last page or the site structure has changed.")
            break
        for review_meta in review_meta_tags:
            # Pass the entire 'soup' object so the parser can find the corresponding visible review content
            parsed_data = parse_review_block(review_meta, soup)
            if parsed_data:
                reviews_data.append(parsed_data)
        print(f"Found and parsed {len(review_meta_tags)} reviews on page {page}.")
        time.sleep(delay)
    return reviews_data
# The correct company slug from the URL is 'nineleaps-technology-solutions'
company = "nineleaps-technology-solutions"
data = scrape_ambitionbox_reviews(company, num_pages=3)
if data:
    df = pd.DataFrame(data)
    output_file = f"{company}_reviews.csv"
    df.to_csv(output_file, index=False)
    print(f"\nDONE! Saved {len(df)} reviews to {output_file}")
else:
    print("\nNo data was scraped. Check the company slug and website structure.")