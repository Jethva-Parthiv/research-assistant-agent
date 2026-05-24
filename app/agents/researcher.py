from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.settings import CHAT_MODEL_NAME
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)


def generate_answer(query: str, search_results: list):

    context = "\n\n".join(
        [
            f"Title: {r['title']}\n"
            f"Content: {r['content']}\n"
            f"Source: {r['url']}"
            for r in search_results
        ]
    )

    prompt = f"""
    You are a research assistant AI.

    Answer the user's question using ONLY the provided search results.

    Question:
    {query}

    Search Results:
    {context}

    Instructions:
    - Give a clear answer
    - Use factual information
    - Add citations using source URLs
    - Do not hallucinate
    """

    response = llm.invoke(prompt)

    return response.content