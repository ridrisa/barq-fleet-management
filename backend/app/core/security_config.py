"""
Security Configuration Module

This module centralizes all security-related configurations for the BARQ Fleet Management system.
It provides type-safe security settings with validation and environment-based configuration.

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


class SecurityLevel(Enum):
    """Security level enumeration for different environments"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HashAlgorithm(Enum):
    """Supported password hashing algorithms"""

    ARGON2 = "argon2"
    BCRYPT = "bcrypt"
    SCRYPT = "scrypt"


@dataclass
class PasswordPolicy:
    """Password policy configuration"""

    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    max_repeated_chars: int = 3
    prevent_common_passwords: bool = True
    password_history_count: int = 5  # Prevent reuse of last N passwords


@dataclass
class TokenConfig:
    """JWT token configuration"""

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    issuer: str = "barq-api"
    audience: str = "barq-client"
    leeway_seconds: int = 10  # Clock skew tolerance


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""

    enabled: bool = True
    default_limit: str = "100/minute"
    auth_limit: str = "5/minute"
    api_limit: str = "1000/hour"
    storage_uri: Optional[str] = None  # Redis URI for distributed rate limiting


@dataclass
class SessionConfig:
    """Session management configuration"""

    session_lifetime_hours: int = 24
    max_concurrent_sessions: int = 3
    session_renewal_threshold_minutes: int = 30
    enforce_ip_binding: bool = False  # Bind session to IP (may cause issues with mobile)
    enforce_user_agent_binding: bool = True


@dataclass
class BruteForceProtection:
    """Brute force protection configuration"""

    enabled: bool = True
    max_attempts: int = 5
    lockout_duration_minutes: int = 30
    track_by_ip: bool = True
    track_by_user: bool = True
    notification_threshold: int = 3  # Send alert after N failed attempts


@dataclass
class EncryptionConfig:
    """Encryption configuration"""

    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    enable_field_encryption: bool = True
    encrypted_fields: List[str] = None

    def __post_init__(self):
        if self.encrypted_fields is None:
            self.encrypted_fields = [
                "national_id",
                "bank_account",
                "iban",
                "tax_number",
                "driving_license",
                "passport_number",
            ]


@dataclass
class AuditConfig:
    """Audit logging configuration"""

    enabled: bool = True
    log_authentication: bool = True
    log_authorization: bool = True
    log_data_access: bool = True
    log_configuration_changes: bool = True
    log_pii_access: bool = True
    tamper_evident: bool = True  # Use hash chaining for tamper detection
    retention_days: int = 365


@dataclass
class CORSConfig:
    """CORS configuration"""

    allow_origins: List[str] = None
    allow_credentials: bool = True
    allow_methods: List[str] = None
    allow_headers: List[str] = None
    expose_headers: List[str] = None
    max_age: int = 600

    def __post_init__(self):
        if self.allow_origins is None:
            self.allow_origins = ["http://localhost:3000"]
        if self.allow_methods is None:
            self.allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        if self.allow_headers is None:
            self.allow_headers = ["*"]
        if self.expose_headers is None:
            self.expose_headers = ["X-Request-ID", "X-RateLimit-Remaining"]


class SecurityConfig:
    """
    Main security configuration class

    This class loads and validates all security settings from environment variables
    and provides type-safe access to security configurations.
    """

    def __init__(self):
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = self.environment.lower() == "development"

        # Security Level
        security_level = os.getenv("SECURITY_LEVEL", "high" if self.is_production else "medium")
        self.security_level = SecurityLevel(security_level)

        # Password Hashing
        hash_algo = os.getenv("PASSWORD_HASH_ALGORITHM", "argon2")
        self.hash_algorithm = HashAlgorithm(hash_algo)
        self.password_policy = PasswordPolicy(
            min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "12")),
            require_uppercase=os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
            require_lowercase=os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
            require_digits=os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true",
            require_special=os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true",
        )

        # Token Configuration
        self.token = TokenConfig(
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            issuer=os.getenv("JWT_ISSUER", "barq-api"),
            audience=os.getenv("JWT_AUDIENCE", "barq-client"),
        )

        # Rate Limiting
        self.rate_limit = RateLimitConfig(
            enabled=os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            storage_uri=os.getenv("REDIS_URL"),
        )

        # Session Management
        self.session = SessionConfig(
            session_lifetime_hours=int(os.getenv("SESSION_LIFETIME_HOURS", "24")),
            max_concurrent_sessions=int(os.getenv("MAX_CONCURRENT_SESSIONS", "3")),
        )

        # Brute Force Protection
        self.brute_force = BruteForceProtection(
            enabled=os.getenv("BRUTE_FORCE_PROTECTION", "true").lower() == "true",
            max_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            lockout_duration_minutes=int(os.getenv("LOCKOUT_DURATION_MINUTES", "30")),
        )

        # Encryption
        self.encryption = EncryptionConfig(
            enable_field_encryption=os.getenv("ENABLE_FIELD_ENCRYPTION", "true").lower() == "true",
            key_rotation_days=int(os.getenv("KEY_ROTATION_DAYS", "90")),
        )

        # Audit Logging
        self.audit = AuditConfig(
            enabled=os.getenv("AUDIT_ENABLED", "true").lower() == "true",
            retention_days=int(os.getenv("AUDIT_RETENTION_DAYS", "365")),
        )

        # CORS
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000")
        self.cors = CORSConfig(
            allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
        )

        # Security Headers
        self.csp_directives = self._build_csp_directives()

        # Validate configuration
        self._validate()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"

    def _build_csp_directives(self) -> dict:
        """Build Content Security Policy directives"""
        base_directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            "font-src": ["'self'", "https://fonts.gstatic.com"],
            "img-src": ["'self'", "data:", "https:", "storage.googleapis.com"],
            "connect-src": ["'self'"],
            "frame-src": ["'none'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
        }

        # Add Google OAuth domains if OAuth is enabled
        if os.getenv("GOOGLE_CLIENT_ID"):
            base_directives["script-src"].append("https://accounts.google.com")
            base_directives["frame-src"] = ["https://accounts.google.com"]

        # Relaxed CSP for development
        if self.is_development:
            base_directives["script-src"].append("'unsafe-eval'")
            base_directives["connect-src"].append("http://localhost:*")

        return base_directives

    def _validate(self):
        """Validate security configuration"""
        errors = []

        # Production checks
        if self.is_production:
            if os.getenv("SECRET_KEY", "").startswith("dev-"):
                errors.append("SECRET_KEY must be changed in production")

            # Accept either traditional Redis URL or Upstash REST API
            if not os.getenv("REDIS_URL") and not os.getenv("UPSTASH_REDIS_REST_URL"):
                errors.append("REDIS_URL or UPSTASH_REDIS_REST_URL must be set in production for session/rate limiting")

            if self.token.access_token_expire_minutes > 60:
                errors.append("ACCESS_TOKEN_EXPIRE_MINUTES should be <= 60 in production")

            if not self.brute_force.enabled:
                errors.append("Brute force protection should be enabled in production")

            if not self.audit.enabled:
                errors.append("Audit logging should be enabled in production")

        # Password policy checks
        if self.password_policy.min_length < 8:
            errors.append("PASSWORD_MIN_LENGTH must be at least 8")

        if self.password_policy.max_length > 256:
            errors.append("PASSWORD_MAX_LENGTH should not exceed 256")

        # Token checks
        if self.token.access_token_expire_minutes < 1:
            errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be at least 1")

        if self.token.refresh_token_expire_days < 1:
            errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be at least 1")

        if errors:
            error_msg = "Security configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            if self.is_production:
                raise ValueError(error_msg)
            else:
                print(f"WARNING: {error_msg}")

    def get_security_headers(self) -> dict:
        """Get security headers for HTTP responses"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        if self.is_production:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return headers

    def get_csp_header(self) -> str:
        """Get Content Security Policy header value"""
        directives = []
        for key, values in self.csp_directives.items():
            directives.append(f"{key} {' '.join(values)}")
        return "; ".join(directives)


# Global security configuration instance
security_config = SecurityConfig()
