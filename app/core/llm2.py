from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm2():
    return ChatOpenAI(
        model=settings.MODEL_NAME2,
        temperature=settings.TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )