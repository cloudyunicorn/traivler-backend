import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 🔑 API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # 🧠 LLM Settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.3))
    
    # 🌍 App Settings
    APP_NAME: str = "Traivler"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # ⏱ Timeouts / Limits
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", 5))


settings = Settings()