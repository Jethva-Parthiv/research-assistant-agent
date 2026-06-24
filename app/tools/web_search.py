# To install: pip install tavily-python
from tavily import TavilyClient
from app.core.logging import logger
import os
import time

_client = None

def get_tavily_client() -> TavilyClient:
    """
    Lazy initialization of TavilyClient.
    Raises ValueError if TAVILY_API_KEY is not configured in settings/environment.
    """
    global _client
    if _client is None:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable is not set. "
                "Please configure it in your .env file."
            )
        _client = TavilyClient(tavily_api_key)
    return _client

def web_search(query: str, search_depth: str = 'basic', retries: int = 3):
    logger.info(f"Searching: {query}")

    try:
        client = get_tavily_client()
    except Exception as error:
        logger.error(f"Failed to initialize Tavily client: {error}")
        return []

    for attempt in range(retries):
        try:
            response = client.search(
                query=query,
                search_depth=search_depth,
                max_results=5
            )
            return response["results"]
        
        except Exception as error:
            logger.error(f"Search failed on attempt {attempt + 1}: {error}")
            if attempt < retries - 1:
                time.sleep(2)
    
    return []


def extract_webpages(urls: list):
    logger.info("Extracting webpage content")

    try:
        client = get_tavily_client()
        response = client.extract(urls=urls)
        return response["results"]
    except Exception as error:
        logger.error(f"Webpage extraction failed: {error}")
        return []