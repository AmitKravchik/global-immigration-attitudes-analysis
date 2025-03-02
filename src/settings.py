from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    start_date: datetime = datetime(2018, 1, 1, 0, 0, 0)
    end_date: datetime = datetime(2018, 1, 8, 0, 0, 0)

    # Countries to query.
    countries: List[str] = ["sourcecountry:US"]#, "sourcecountry:GM"]#, "sourcecountry:UK", "sourcecountry:AU", "sourcecountry:CA", "sourcecountry:SW", "sourcecountry:IT", "sourcecountry:SP", "sourcecountry:SF", "sourcecountry:IN", "sourcecountry:BR"]

    # Base query and constraints.
    query: str = '(immigration OR immigrant OR migration OR migrant)'
    theme: str = "theme:%IMMIGRATION%"
    # tone: str = ["tone<-9.999", "tone>-10 tone<-4.999", "tone>-5 tone<-0.5", "tone>-0.5 tone<0.5", "tone>0.5 tone<5.001", "tone>5 tone" , "tone>9.999"]  
    
    # Maximum records per API request.
    max_records: int = 250
    output_format: str = "json"
    sort_order: str = "ToneDesc"

    # Thread pool sizes (adjust as needed based on your system/network).
    num_processes: int = 48
    num_threads_api: int = 30
    num_threads_scrape: int = 90

    gdelt_doc_base_url: str = "https://api.gdeltproject.org/api/v2/doc/doc"

    epsilon: float = 0.001  # a very small number


    tone: dict = {
        "slightly_negative": f"tone>{-5 - epsilon} tone<-0.5"     # "tone>-5.001 tone<-0.5"
    }

