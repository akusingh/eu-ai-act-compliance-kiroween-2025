"""Configuration management for the EU AI Act Compliance Agent."""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set GOOGLE_API_KEY for ADK (it reads from environment)
if os.getenv("GOOGLE_GENAI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_GENAI_API_KEY")


class Config:
    """Application configuration."""

    # API Keys - loaded from environment
    GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
    COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")  # Optional - for reranking

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # Application settings
    MAX_TURNS = 10
    SESSION_TIMEOUT = 3600  # 1 hour
    SEARCH_TIMEOUT = 10

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.GOOGLE_GENAI_API_KEY:
            logging.warning("GOOGLE_GENAI_API_KEY not set. Some features may not work.")
        if not cls.SERPAPI_API_KEY:
            logging.warning("SERPAPI_API_KEY not set. Google Search tool will not work.")
        return bool(cls.GOOGLE_GENAI_API_KEY or cls.SERPAPI_API_KEY)
