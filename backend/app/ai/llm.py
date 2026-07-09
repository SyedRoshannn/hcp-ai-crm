from langchain_groq import ChatGroq
from app.core.config import settings
from app.ai.groq_client import verify_groq_credentials

def get_llm() -> ChatGroq:
    """Lazy-loads and returns a ChatGroq instance after validating credentials."""
    verify_groq_credentials()
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.MODEL_NAME,
        temperature=0.2
    )
