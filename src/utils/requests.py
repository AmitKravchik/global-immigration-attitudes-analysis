import requests

def create_session(connection_pool_size: int = 20) -> requests.Session: 
    """
    Create a new requests session with a custom connection pool size.
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