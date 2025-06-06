#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration settings for NeuroScan API
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    APP_NAME: str = "NeuroScan API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
      # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./neuroscan.db")
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
      # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://verify.neuroscan.com",
        "https://neuroscan-system.vercel.app",
        "https://neuroscan-api.onrender.com"
    ]
    
    # API Keys (for external access)
    API_KEY_EXPIRES_DAYS: int = 365
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
