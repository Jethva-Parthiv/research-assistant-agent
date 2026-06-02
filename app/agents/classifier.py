from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.settings import CHAT_MODEL_NAME
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()


llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)


def classify_query(query: str):

    prompt = f"""
    You are a routing classifier.

    Classify the query as:

    SIMPLE:
    - factual lookup
    - definition
    - short answer
    - single topic

    DEEP:
    - comparison
    - analysis
    - research
    - multiple sources required
    - report generation
    - latest trends

    Return ONLY:
    SIMPLE
    or
    DEEP

    Query:
    {query}
    """

    chain = llm | parser

    response = chain.invoke(prompt)

    return response