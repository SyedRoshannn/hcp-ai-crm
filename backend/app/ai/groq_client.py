from app.core.config import settings

def verify_groq_credentials() -> None:
    """Verifies that the Groq API Key is present in the configuration."""
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        raise ValueError(
            "GROQ_API_KEY is missing or set to the default placeholder in environment variables."
        )
