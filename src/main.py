import json
from multiprocessing import cpu_count
import os
import threading
from queue import Queue
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from threading import Lock
from typing import List, Dict, Tuple
import requests
from loguru import logger

# --- Imports from your project (adjust these as needed) ---
from src.gdelt.responses import GDELTToneChartBin, ToneChartResponse
# from src.gdelt.tonechart import ToneChart
from src.settings import Settings
from src.gdelt.client import GDELTClient
from src.gdelt.article import Article, ArticleList, ToneChartBin, ToneChart
from src.gdelt.query_params import GDELTQuery
from src.parsers.body_parser import BodyParser
from src.parsers.title_parser import TitleParser
from src.utils.requests import create_session, fetch_html
import argparse

# --- Utility: generate date intervals ---
def generate_date_intervals(start: datetime, end: datetime, delta: timedelta) -> List[tuple]:
    intervals = []
    current = start
    while current < end:
        next_interval = min(current + delta, end)
        intervals.append((current, next_interval))
        current = next_interval
    return intervals

# --- Stage 1 helper: fetch article lists ---
def fetch_tonechart_for_query(query: GDELTQuery, start_dt: datetime, end_dt: datetime) -> ToneChartResponse:
    logger.debug(f"Thread {threading.current_thread().name} is in stage 1")
    response = client.fetch_tonechart_json_results(
        query=query, start_datetime=start_dt, end_datetime=end_dt
    )

    futures = []
    bins = {}

    logger.debug(f"Thread {threading.current_thread().name} is processing tonechart")
    # {"1": {"count": 12, "top_articles": []}}6

    with ThreadPoolExecutor(max_workers=settings.num_threads_api) as thread_executor, \
         ProcessPoolExecutor(max_workers=5) as process_executor:
        for bin in response.tonechart:
            bins[bin.bin] = {"count": bin.count, "top_articles": []}
            for ta in bin.top_articles:
                article = Article(**ta.model_dump(), startdatetime=start_dt, enddatetime=end_dt, sourcecountry=query.source_country, tone=bin.bin)
                futures.append(thread_executor.submit(fetch_html_for_article, article))
        
        for future in as_completed(futures):
            try:
                article = future.result()
            except Exception as e:
                logger.error(f"Error fetching HTML for {article.url}: {e}")

        futures2 = []
        for future in as_completed(futures):
            try:
                article = future.result()
                futures2.append(process_executor.submit(parse_html_for_article, article))
            except Exception as e:
                logger.error(f"Error fetching HTML for {article.url}: {e}")
        
        for future in as_completed(futures2):
            try:
                article = future.result()
                bins[article.gdelt_tone]["top_articles"].append(article)
            except Exception as e:
                logger.error(f"Error parsing HTML for {article.url}: {e}")
    
    try:
        logger.debug(f"Thread {threading.current_thread().name} is updating bins")
        updated_bins = []
        for bin in bins:
            updated_bins.append(ToneChartBin(bin=bin, count=bins[bin]["count"], toparts=bins[bin]["top_articles"]))
        logger.debug(f"Thread {threading.current_thread().name} is creating tonechart")
        tonechart = ToneChart(tonechart=updated_bins, source_country=query.source_country, startdatetime=start_dt, enddatetime=end_dt)
        return tonechart
    except Exception as e:
        logger.error(f"Error updating bins: {e}")
        raise e

# --- Stage 2 helper: fetch HTML for one article ---

def fetch_html_for_article(article: Article, timeout: int = 5) -> Article:
    try:
        logger.debug(f"Thread {threading.current_thread().name} Article {article.url}")
        article.html = fetch_html(article.url, session, timeout) 
        return article
    except Exception as e:
        logger.error(e)
        raise e



# --- Stage 3 helper: parse HTML for one article (CPU-bound) ---
def parse_html_for_article(article: Article) -> Article:
    logger.debug(f"Thread {threading.current_thread().name} with PID {os.getpid()} is in stage 3")
    try:
        body_parser = BodyParser()
        title_parser = TitleParser()
        article.html_body = body_parser.parse(article.html)
        article.html_title = title_parser.parse(article.html)
        article.html = None  # Clear HTML content after parsing
        return article
    except Exception as e:
        logger.error(e)
        raise e

# --- Stage 4: Writer thread that saves articles to disk ---

# --- Global lock dictionary ---
file_locks = {}
file_locks_access = Lock()

def get_file_lock(filename):
    """Retrieve or create a lock for the given filename."""
    with file_locks_access:
        if filename not in file_locks:
            file_locks[filename] = Lock()
        return file_locks[filename]

def write_article_to_file(tonechart: ToneChart, base_dir="output2"):
    logger.debug(f"Thread {threading.current_thread().name} is writing")
    path = f"{base_dir}/{tonechart.source_country}/{tonechart.start_datetime.year}"
    if not os.path.exists(path):
        os.makedirs(path)
    filename = f"{path}/{tonechart.start_datetime.month}.json"
    file_lock = get_file_lock(filename)
    with file_lock:
        logger.debug(f"Thread {threading.current_thread().name} is writing to {filename}")
        with open(filename, "a") as file:
            data = tonechart.model_dump(exclude_none=True)
            file.write(json.dumps(data) + "\n")


settings = Settings()
session = create_session(settings.num_threads_api)
client = GDELTClient(settings.gdelt_doc_base_url, session)


@logger.catch
def main():
    logger.info("Starting the pipeline")
    delta = timedelta(weeks=1)
    date_intervals = generate_date_intervals(settings.start_date, settings.end_date, delta)

    tasks = []
    for country in settings.countries:
        for start_dt, end_dt in date_intervals:
            tasks.append({
                "country": country,
                "start_date": start_dt,
                "end_date": end_dt,
                "base_query": settings.query,
                "theme": settings.theme
            })


    logger.info(f"Starting {len(tasks)} tasks")

    with ProcessPoolExecutor(max_workers=5) as process_executor:
        for task in tasks:
            query = GDELTQuery(
                query=task["base_query"],
                source_country=task["country"],
                theme=task["theme"]
            )
            future = process_executor.submit(
                fetch_tonechart_for_query,
                query, task["start_date"], task["end_date"]
            )
            future.add_done_callback(lambda f: write_article_to_file(f.result()))

    logger.info("Finished processing all tasks")



if __name__ == "__main__":
    def parse_arguments():
        parser = argparse.ArgumentParser(description="Process GDELT data for a specific country.")
        parser.add_argument("source_country", type=str, help="The source country to process data for")
        return parser.parse_args()
    
    args = parse_arguments()
    print(args.source_country)
    settings.countries = [args.source_country]
    main()