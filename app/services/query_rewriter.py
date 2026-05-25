from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from app.core.settings import CHAT_MODEL_NAME


llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)

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