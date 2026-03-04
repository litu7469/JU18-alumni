from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost/ju18_alumni"
    
    # JWT
    SECRET_KEY: str = "changeme-use-strong-random-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Email (Gmail SMTP)
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    FROM_NAME: str = "JU 18th Batch Alumni"
    
    # App
    APP_NAME: str = "JU 18th Batch Alumni Association"
    BASE_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:8000"
    ENVIRONMENT: str = "development"
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
