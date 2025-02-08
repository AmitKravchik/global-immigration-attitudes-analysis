from datetime import datetime

import requests
from src.gdelt.responses import ArticleListResponse
from src.gdelt.query_params import GDELTQuery, GDELTRequestParams

class GDELTClient:
    __base_url: str
    __session: requests.Session

    def __init__(self, base_url: str, session: requests.Session):
        self.__base_url = base_url
        self.__session = session

    def fetch_artlist_json_results(self, request_params: GDELTRequestParams) -> ArticleListResponse:
        url = request_params.build_url(self.__base_url)
        print(url)
        response = self.__session.get(url)
        response.raise_for_status()
        return ArticleListResponse.model_validate(response.json())
    

