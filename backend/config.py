"""
Configuration management for Bloomberg Terminal Alternative
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str = ""
    alpha_vantage_api_key: Optional[str] = ""
    finnhub_api_key: Optional[str] = ""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./terminal.db"
    
    # CORS
    cors_origins: list = ["http://localhost:4300", "http://127.0.0.1:4300"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
