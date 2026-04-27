import os
from dotenv import load_dotenv
from typing import Dict
from pydantic_settings import BaseSettings
from typing import Optional

def validate_env_vars():
    required_vars = ['DATABASE_URL']
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    # Firebase es opcional — solo avisar en desarrollo local, no en Vercel
    if not os.getenv("VERCEL"):
        optional_vars = ['FIREBASE_API_KEY', 'FIREBASE_APP_ID', 'FIREBASE_PROJECT_ID']
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            print(f"Warning: Optional environment variables not set: {', '.join(missing_optional)}")

load_dotenv(override=True)
validate_env_vars()

def database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        # Strip surrounding quotes if the value was stored with them
        url = url.strip('"\'')
        # SQLAlchemy 2.x requires postgresql:// not postgres://
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        if os.getenv('VERCEL'):
            print("Ejecutándose en Vercel")
        elif os.getenv('REPLIT_DEPLOYMENT'):
            print("Ejecutándose en deploy")
        else:
            print("Ejecutándose en development")
        return url
    dev_url = os.getenv("DATABASE_URL_DEV", "postgresql://postgres:postgres@localhost/telecom")
    print("Ejecutándose en development (DATABASE_URL_DEV)")
    return dev_url

class Settings(BaseSettings):
    DATABASE_URL: str = database_url()
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Aumentado a 24 horas (60 min * 24)

    # Google OAuth settings
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")

    # Firebase settings
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_APP_ID: str = os.getenv("FIREBASE_APP_ID", "")

    # General settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra environment variables

settings = Settings()