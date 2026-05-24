# To install: pip install tavily-python
from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(tavily_api_key)

def web_search(query : str,search_depth : str = 'basic'):
    response = client.search(
        query=query,
        search_depth=search_depth
    )

    return response["results"]