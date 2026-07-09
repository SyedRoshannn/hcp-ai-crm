from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "HCP AI CRM"
    DATABASE_URL: str = "sqlite:///./dev.db"
    GROQ_API_KEY: str = ""  # Default to empty string so the app starts even if missing
    MODEL_NAME: str = "gemma2-9b-it"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
