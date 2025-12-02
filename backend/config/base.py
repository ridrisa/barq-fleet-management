"""
BARQ Fleet Management - Base Configuration

Base configuration class with default values and validation.
All environment-specific configurations inherit from this.
"""
import os
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """
    Base configuration with sensible defaults.

    Configuration is loaded from:
    1. Environment variables (highest priority)
    2. .env file (if present)
    3. Default values (lowest priority)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    PROJECT_NAME: str = Field(default="BARQ Fleet Management")
    VERSION: str = Field(default="1.1.0")
    API_V1_STR: str = Field(default="/api/v1")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    # -------------------------------------------------------------------------
    # Security Settings
    # -------------------------------------------------------------------------
    SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_SECRET_KEY: Optional[str] = Field(default=None)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)

    # -------------------------------------------------------------------------
    # Database Settings
    # -------------------------------------------------------------------------
    DATABASE_URL: Optional[str] = Field(default=None)
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="barq_fleet")
    POSTGRES_PORT: int = Field(default=5432)

    # Pool settings
    DB_POOL_SIZE: int = Field(default=5)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=1800)
    DB_ECHO: bool = Field(default=False)

    # -------------------------------------------------------------------------
    # Redis Settings
    # -------------------------------------------------------------------------
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = Field(default=10)

    # -------------------------------------------------------------------------
    # CORS Settings
    # -------------------------------------------------------------------------
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:5173"
    )

    # -------------------------------------------------------------------------
    # Logging Settings
    # -------------------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")  # json or text

    # -------------------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------------------
    FEATURE_GOOGLE_AUTH: bool = Field(default=True)
    FEATURE_WORKFLOW_ENGINE: bool = Field(default=True)
    FEATURE_SUPPORT_MODULE: bool = Field(default=True)

    # -------------------------------------------------------------------------
    # Google OAuth (Optional)
    # -------------------------------------------------------------------------
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:5173"]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build SQLAlchemy database URI."""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{user}:{password}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"

    def validate_production_settings(self) -> List[str]:
        """
        Validate that all required production settings are configured.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if self.is_production:
            # Check secret key
            if self.SECRET_KEY in ["change-me-in-production", "dev-secret-key", ""]:
                errors.append("SECRET_KEY must be set to a secure value in production")

            # Check database
            if "localhost" in self.SQLALCHEMY_DATABASE_URI:
                errors.append(
                    "Database should not use localhost in production"
                )

            # Check debug mode
            if self.DEBUG:
                errors.append("DEBUG should be False in production")

        return errors

    def startup_check(self) -> None:
        """
        Perform startup validation checks.

        Raises:
            ValueError: If critical configuration is invalid in production
        """
        errors = self.validate_production_settings()
        if errors and self.is_production:
            error_msg = "Production configuration errors:\n" + "\n".join(
                f"  - {e}" for e in errors
            )
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)
