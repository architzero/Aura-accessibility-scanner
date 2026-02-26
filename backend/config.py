from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    mongo_db_uri: str
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS - Allowed origins for API access
    cors_origins: List[str] = [
        "http://127.0.0.1:8001",
        "http://localhost:8001",
    ]
    
    # Application
    environment: str = "development"  # development, staging, production
    
    # Rate Limiting
    rate_limit_per_minute: int = 10  # Max requests per minute per user
    scan_rate_limit_per_hour: int = 20  # Max scans per hour per user
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
