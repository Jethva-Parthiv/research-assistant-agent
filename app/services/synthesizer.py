from app.core.llm import llm
from langchain_core.output_parsers import StrOutputParser

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
    - DO NOT include any conversational preamble, introduction, or roleplay meta-commentary framing (such as "As a senior research analyst, I have synthesized...", "As an AI...", or "Here is the report..."). Start the report directly with the content or title.
    """

    chain = llm | parser
    response = chain.invoke(prompt)
    return response
