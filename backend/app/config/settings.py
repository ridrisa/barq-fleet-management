import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Load .env from project root (single source of truth)
root_env = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(root_env)


class Settings:
    """Application settings loaded from environment variables"""

    def __init__(self) -> None:
        # Project
        self.PROJECT_NAME: str = os.getenv("PROJECT_NAME", "BARQ Fleet Management")
        self.VERSION: str = os.getenv("VERSION", "1.0.0")
        self.API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

        # Sentry Error Tracking
        self.SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
        self.SENTRY_TRACES_SAMPLE_RATE: float = float(
            os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")
        )
        self.SENTRY_PROFILES_SAMPLE_RATE: float = float(
            os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "1.0")
        )

        # Security
        self.SECRET_KEY: str = self._require_secret("SECRET_KEY")
        self.ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

        # Environment-sensitive JWT expiration (15 min prod, 60 min dev)
        default_expire = "15" if self.ENVIRONMENT.lower() == "production" else "60"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default_expire)
        )

        # JWT audience and issuer verification
        self.JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "barq-client")
        self.JWT_ISSUER: str = os.getenv("JWT_ISSUER", "barq-api")

        # Google OAuth (optional)
        self.GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")

        # Redis (optional - for token blacklist, rate limiting, caching)
        self.REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

        # Google BigQuery (for performance analytics)
        self.BIGQUERY_PROJECT_ID: str = os.getenv(
            "BIGQUERY_PROJECT_ID", "looker-barqdata-2030"
        )
        self.BIGQUERY_DATASET: str = os.getenv("BIGQUERY_DATASET", "master_saned")
        self.BIGQUERY_CREDENTIALS_PATH: Optional[str] = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS"
        )

        # CORS
        self.BACKEND_CORS_ORIGINS: List[str] = self._load_cors_origins()

    def _require_secret(self, key: str) -> str:
        value = os.getenv(key, "")
        if not value or value == "your-super-secret-key-change-this-in-production":
            if self.ENVIRONMENT.lower() == "production":
                raise ValueError(f"{key} must be set in production")
            value = value or "dev-secret-key"
        return value

    def _load_cors_origins(self) -> List[str]:
        raw = os.getenv("BACKEND_CORS_ORIGINS", "")
        if raw:
            return [origin.strip() for origin in raw.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]

    # Database URL (built from environment variables)
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        direct_url = os.getenv("DATABASE_URL")
        if direct_url:
            return direct_url

        user = quote_plus(os.getenv("POSTGRES_USER", "postgres"))
        password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
        server = os.getenv("POSTGRES_SERVER", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "barq_fleet")

        # Handle Cloud SQL Unix socket path (starts with /cloudsql/)
        if server.startswith("/cloudsql/"):
            # Cloud SQL format: postgresql://user:password@/dbname?host=/cloudsql/instance
            return f"postgresql://{user}:{password}@/{db}?host={server}"

        return f"postgresql://{user}:{password}@{server}:{port}/{db}"


settings = Settings()
