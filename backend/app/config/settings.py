import os
from typing import List
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""

    # Project
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', 'BARQ Fleet Management')
    VERSION: str = os.getenv('VERSION', '1.0.0')
    API_V1_STR: str = os.getenv('API_V1_STR', '/api/v1')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')

    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production')
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '10080'))

    # Google OAuth (optional)
    GOOGLE_CLIENT_ID: str | None = os.getenv('GOOGLE_CLIENT_ID')

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]

    # Database URL (built from environment variables)
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        user = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        server = os.getenv('POSTGRES_SERVER', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'barq_fleet')
        return f"postgresql://{user}:{password}@{server}:{port}/{db}"


settings = Settings()
