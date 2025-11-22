"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    # Environment
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Project Info
    PROJECT_NAME: str = "PMS API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    
    # Database
    DATABASE_URL: str = "postgresql://pms_user:pms_password@localhost:5432/pms_db"
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175"
    ]
    
    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@pms.com"
    EMAILS_FROM_NAME: str = "PMS System"
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Business Rules
    HELMET_FEE: int = 1000  # COP
    DATA_RETENTION_DAYS: int = 365
    GLOBAL_BONUS_PERCENTAGE: float = 15.0  # Default bonus %
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_cors(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
