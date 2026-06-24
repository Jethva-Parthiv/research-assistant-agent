from app.core.llm import llm
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()

def rewrite_query(query: str) -> str:

    prompt = f"""
    You are a search query optimization AI.

    Rewrite the user's query into a better web search query.

    RULES:
    - Keep meaning same
    - Make query specific
    - Optimize for search engines
    - Keep concise

    USER QUERY:
    {query}
    """

    chain = llm | parser
    response = chain.invoke(prompt)

    return response