import requests

def create_session(connection_pool_size: int = 20) -> requests.Session: 
    """
    Create a new requests session with a custom connection pool size and timeout.
    """
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; GDELT-Scraper/1.0; +http://example.com)"
    }
    session.headers.update(headers)
    adapter = requests.adapters.HTTPAdapter(pool_connections=connection_pool_size, pool_maxsize=connection_pool_size)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def fetch_html(url: str, session: requests.Session, timeout: int) -> str:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()  # raise an HTTPError for bad responses

    # If no encoding is provided, let requests try to guess it
    if not response.encoding:
        response.encoding = response.apparent_encoding

    return response.text