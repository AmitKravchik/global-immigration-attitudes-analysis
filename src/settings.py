from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    start_date: datetime = datetime(2017, 1, 1, 0, 0, 0)
    end_date: datetime = datetime(2017, 1, 2, 0, 0, 0)

    # Countries to query.
    countries: List[str] = ["US", "GM", "UK", "AU", "CA", "SW", "IT", "SP", "SF", "IN", "BR"]

    # Base query and constraints.
    query: str = "immigration"
    tone: str = "tone>0 tone<0.999"  
    
    # Maximum records per API request.
    max_records: int = 250
    output_format: str = "json"
    sort_order: str = "ToneDesc"

    # Thread pool sizes (adjust as needed based on your system/network).
    num_threads_api: int = 20
    num_threads_scrape: int = 20

    gdelt_doc_base_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"
