from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from app.core.settings import CHAT_MODEL_NAME


llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)

parser = StrOutputParser()

def synthesize_answer(
        query: str,
        evidence: list
):

    context = "\n\n".join(
        [
            f"""
            TASK:
            {item['task']}

            SOURCE:
            {item['source']}

            CONTENT:
            {item['content']}
            """
            for item in evidence
        ]
    )

    prompt = f"""
    You are a senior research analyst.

    Answer the user's question using evidence.

    QUESTION:
    {query}

    EVIDENCE:
    {context}

    Requirements:
    - Analyze findings
    - Compare viewpoints
    - Highlight tradeoffs
    - Use citations
    - Produce structured markdown
    """

    chain = llm | parser

    response = chain.invoke(prompt)

    return response