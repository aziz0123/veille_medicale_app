# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration
    SECRET_KEY: str = "votre-cle-secrete-tres-longue-et-securisee-a-changer-en-production-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_URL: str = "postgresql://admin:admin@localhost:5432/veille"
    MONGO_URL: str = "mongodb://admin:admin@localhost:27018/"
    
    class Config:
        env_file = ".env"

settings = Settings()