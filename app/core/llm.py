from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.settings import CHAT_MODEL_NAME

# Shared low-temperature LLM instance for deterministic agent behavior
llm = ChatGoogleGenerativeAI(
    model=CHAT_MODEL_NAME,
    temperature=0
)

def get_llm():
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL_NAME,
        temperature=0
    )
