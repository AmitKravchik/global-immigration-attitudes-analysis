import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import multiprocessing

# ---------------------------
# GLOBAL SESSION
# ---------------------------
# Create a persistent session for all HTTP requests.
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; YourScraper/1.0)'})

# ---------------------------
# CONFIGURATION PARAMETERS
# ---------------------------
# Define the query period.
START_DATE = datetime(2017, 1, 1, 0, 0, 0)
END_DATE   = datetime(2025, 1, 1, 0, 0, 0)

# Countries to query.
COUNTRIES = ["US", "GM", "UK", "AU", "CA", "SW", "IT", "SP", "SF", "IN", "BR"]

# Base query and constraints.
QUERY = "immigration"
TONE_CONSTRAINT = "tone<-5"  # For example, only articles with a negative tone.
# Maximum records per API request.
MAX_RECORDS = 250
OUTPUT_FORMAT = "json"
SORT_ORDER = "ToneDesc"

# Thread pool sizes (adjust as needed based on your system/network).
NUM_THREADS_API = 20
NUM_THREADS_SCRAPE = 20

# ---------------------------
# STEP 1: GENERATE HOURLY INTERVALS
# ---------------------------
def generate_hourly_intervals(start_dt, end_dt):
    """
    Generate a list of (start, end) time intervals, each spanning one hour.
    Returns a list of tuples with timestamps formatted as YYYYMMDDHHMMSS.
    """
    intervals = []
    current = start_dt
    while current < end_dt:
        start_str = current.strftime("%Y%m%d%H%M%S")
        next_hour = current + timedelta(hours=1)
        # Do not exceed the end date.
        end_str = (next_hour if next_hour < end_dt else end_dt).strftime("%Y%m%d%H%M%S")
        intervals.append((start_str, end_str))
        current = next_hour
    return intervals

# ---------------------------
# STEP 2: QUERY GDELT API TO FETCH ARTICLE URLs
# ---------------------------
def fetch_articles_for_task(country, start_datetime, end_datetime, query=QUERY, tone_constraint=TONE_CONSTRAINT):
    """
    Fetches articles from GDELT for a given country and one-hour interval.
    Combines the base query, tone constraint, and country filter.
    
    Returns:
        A list of article URLs from the JSON response.
    """
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
    # Build the query string.
    country_query = f"sourcecountry:{country}"
    full_query = f"{query} {tone_constraint} {country_query}".strip()
    
    params = {
        "query": full_query,
        "mode": "artlist",
        "STARTDATETIME": start_datetime,
        "ENDDATETIME": end_datetime,
        "maxrecords": MAX_RECORDS,
        "format": OUTPUT_FORMAT,
        "sort": SORT_ORDER,
    }
    
    try:
        response = session.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        urls = [article.get('url') for article in articles if article.get('url')]
        return urls
    except requests.RequestException as e:
        print(f"Error fetching articles for {country} {start_datetime}-{end_datetime}: {e}")
        return []

def process_api_task(task):
    """
    Processes a single API task.
    Task is a tuple: (country, start_datetime, end_datetime).
    Returns a tuple (country, start_datetime, end_datetime, list_of_urls).
    """
    country, start_dt, end_dt = task
    urls = fetch_articles_for_task(country, start_dt, end_dt)
    return (country, start_dt, end_dt, urls)

def run_api_tasks(tasks):
    """
    Runs API tasks concurrently using ThreadPoolExecutor.
    
    Returns:
        A list of results for each task.
    """
    results = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS_API) as executor:
        future_to_task = {executor.submit(process_api_task, task): task for task in tasks}
        for future in as_completed(future_to_task):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print("Error processing API task:", e)
    return results

# ---------------------------
# STEP 3: SCRAPE ARTICLES TO EXTRACT TITLE AND BODY
# ---------------------------
def get_text_and_title(url):
    """
    Fetches HTML content from a URL and extracts the title and main body text.
    
    Returns:
        A tuple (url, title, body).
    """
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return url, None, None

    soup = BeautifulSoup(response.text, "lxml")
    
    # Extract title: prefer <h1> if available.
    title = soup.title.get_text(strip=True) if soup.title else None
    h1 = soup.find('h1')
    if h1 and (not title or len(h1.get_text(strip=True)) > len(title)):
        title = h1.get_text(strip=True)
    
    # Extract body: try <article> tag first, then fallback to common containers.
    body = ""
    article_tag = soup.find('article')
    if article_tag:
        body = article_tag.get_text(separator=" ", strip=True)
    else:
        for class_name in ['article-body', 'post-content', 'entry-content', 'story-body']:
            container = soup.find('div', class_=class_name)
            if container:
                body = container.get_text(separator=" ", strip=True)
                break
        if not body:
            body_tag = soup.find('body')
            if body_tag:
                body = body_tag.get_text(separator=" ", strip=True)
    
    return url, title, body

def process_scraping(urls):
    """
    Processes a list of URLs concurrently using ThreadPoolExecutor for scraping.
    
    Returns:
        A list of tuples (url, title, body) for each scraped article.
    """
    results = []
    with ThreadPoolExecutor(max_workers=NUM_THREADS_SCRAPE) as executor:
        future_to_url = {executor.submit(get_text_and_title, url): url for url in urls if url}
        for future in as_completed(future_to_url):
            try:
                results.append(future.result())
            except Exception as e:
                print("Error processing URL:", e)
    return results

# ---------------------------
# MAIN PIPELINE
# ---------------------------
def main():
    # Generate hourly intervals.
    intervals = generate_hourly_intervals(START_DATE, END_DATE)
    print(f"Total hourly intervals generated: {len(intervals)}")
    
    # Build a list of API tasks: one per country per interval.
    tasks = []
    for country in COUNTRIES:
        for (start_dt, end_dt) in intervals:
            tasks.append((country, start_dt, end_dt))
    
    print(f"Total API tasks to process: {len(tasks)}")
    
    # For demonstration, we process only a sample batch (e.g., first 100 tasks).
    sample_tasks = tasks[:100]
    api_results = run_api_tasks(sample_tasks)
    
    # Flatten the URLs from all API task results.
    all_urls = []
    for country, start_dt, end_dt, urls in api_results:
        print(f"Country: {country} | Interval: {start_dt}-{end_dt} | Articles found: {len(urls)}")
        all_urls.extend(urls)
    
    print(f"Total URLs to scrape: {len(all_urls)}")
    
    # Process the scraping of each URL to extract title and body.
    scraped_articles = process_scraping(all_urls)
    
    # Output the results (or store them as needed)
    for url, title, body in scraped_articles:
        print("URL:", url)
        print("Title:", title)
        snippet = body[:200] if body else "No body found"
        print("Body snippet:", snippet, "\n---\n")

if __name__ == "__main__":
    main()
