from datetime import datetime
import re
from loguru import logger
import requests
from src.gdelt.responses import ArticleListResponse, ToneChartResponse
from src.gdelt.query_params import GDELTMode, GDELTQuery, GDELTRequestParams, OutputFormat

class GDELTClient:
    __base_url: str
    __session: requests.Session

    def __init__(self, base_url: str, session: requests.Session):
        self.__base_url = base_url
        self.__session = session

    def fetch_artlist_json_results(self, query: GDELTQuery, max_records: int, start_datetime: datetime, end_datetime: datetime) -> ArticleListResponse:
        request_params = GDELTRequestParams(
            query=query,
            max_records=max_records,
            mode=GDELTMode.ART_LIST,
            output_format=OutputFormat.JSON,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        url = request_params.build_url(self.__base_url)
        print(url)
        response = self.__session.get(url)
        response.raise_for_status()
        return ArticleListResponse.model_validate_json(response.content)
    
    def fetch_tonechart_json_results(self, query: GDELTQuery, start_datetime: datetime, end_datetime: datetime) -> ArticleListResponse:
        request_params = GDELTRequestParams(
            query=query,
            mode=GDELTMode.TONE_CHART,
            output_format=OutputFormat.JSON,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        url = request_params.build_url(self.__base_url)
        response = self.__session.get(url)
        response.raise_for_status()
        try:
            # clean_response = clean_json_string(response.content.decode('utf-8'))
            res = ToneChartResponse.model_validate_json(clean_json_string(response.text))
            return res
        except Exception as e:
            logger.error(f"Invalid json response: {response.text}")
            raise e
    

def clean_json_string(json_content):
    # Fix unescaped backslashes
    json_content = re.sub(r'\\(?![/u"\\bfnrt])', r'\\\\', json_content)

    # Replace invalid escape sequences
    json_content = json_content.replace('\\\'', '\'')  # Single quotes don't need to be escaped
    json_content = json_content.replace('\\"', '"')    # Properly escape double quotes

    # Replace control characters within strings
    json_content = re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda x: f'\\u{ord(x.group(0)):04x}', json_content)
    
    return json_content
