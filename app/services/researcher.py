from app.core.llm import llm
from app.prompts.research_prompt import RESEARCH_PROMPT
from langchain_core.output_parsers import StrOutputParser
from app.tools.tavily_search import tavily_search

parser = StrOutputParser()

def generate_answer(query: str, context: str):
    prompt = RESEARCH_PROMPT.format(
        query=query,
        context=context
    )
    chain = llm | parser
    response = chain.invoke(prompt)
    return response

def research_task(task: str):
    results = tavily_search(task)
    evidence = []
    for result in results:
        evidence.append(
            {
                "task": task,
                "source": result["url"],
                "content": result["content"]
            }
        )
    return evidence
