# To install: pip install tavily-python
from tavily import TavilyClient
from dotenv import load_dotenv
from app.core.logging import logger
import os
import time

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(tavily_api_key)

def web_search(query : str,search_depth : str = 'basic', retries : int = 3):
    logger.info(f"Searching: {query}")

    for attempt in range(retries):
        try:
            response = client.search(
                query=query,
                search_depth=search_depth,
                max_results=5
            )
            return response["results"]
        
        except Exception as error:
            logger.error(f"Search failed: {error}")
            time.sleep(2)
    
    return []


def extract_webpages(urls: list):

    logger.info("Extracting webpage content")

    response = client.extract(urls=urls)

    return response["results"]