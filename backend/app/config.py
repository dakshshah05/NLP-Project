import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AURA AI - Autonomous NLP Workflow Agent"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aura_ai.db")
    
    # LLM & Vector DB
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    
    # Fallback to Mock NLP/DB if services are unavailable or packages fail to load
    FALLBACK_TO_MOCK_NLP: bool = True
    FALLBACK_TO_MOCK_VECTOR: bool = True
    FALLBACK_TO_MOCK_DB: bool = True

    class Config:
        case_sensitive = True

settings = Settings()
