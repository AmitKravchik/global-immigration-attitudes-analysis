from concurrent.futures import ThreadPoolExecutor
from src.gdelt.client import GDELTClient
from src.utils.requests import create_session
from src.settings import Settings
from src.gdelt.query_params import GDELTQuery, GDELTRequestParams, GDELTMode, OutputFormat, SortOrder

def main():
    # load configuration
    settings = Settings()

    # create session
    session = create_session(settings.num_threads_api)

    # create thredpool
    executor = ThreadPoolExecutor(max_workers=settings.num_threads_api)

    # create GDELTClient
    gdelt_client = GDELTClient(settings.gdelt_doc_base_url, session)
    
    # fetch articles
    query = GDELTQuery(query=settings.query, source_country="sourcecountry:US", tone=settings.tone)
    request_params = GDELTRequestParams(
        query=query, 
        max_records=settings.max_records, 
        mode=GDELTMode.ART_LIST, 
        output_format=OutputFormat.JSON,
        start_datetime=settings.start_date,
        end_datetime=settings.end_date
    )
    response = gdelt_client.fetch_artlist_json_results(request_params)
    print(response)

    # create parser

if __name__ == "__main__":
    main()