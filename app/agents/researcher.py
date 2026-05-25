from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.settings import CHAT_MODEL_NAME
from app.prompts.research_prompt import RESEARCH_PROMPT
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

parser = StrOutputParser()

llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)


def generate_answer(query: str, context : str):

    prompt = RESEARCH_PROMPT.format(
        query = query,
        context = context
    )

    chain = llm | parser

    response = chain.invoke(prompt)

    return response