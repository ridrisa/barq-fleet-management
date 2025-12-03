"""
Enhanced Security Module

This module provides production-grade security features including:
- Argon2 password hashing (OWASP recommended)
- Secure JWT token generation with refresh tokens
- Token blacklisting and revocation
- Brute force protection
- Session management
- Password policy enforcement

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from jose import jwt, JWTError

from app.config.settings import settings
from app.core.security_config import security_config

# Initialize Argon2 password hasher with secure defaults
ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,   # Memory usage in KiB (64 MB)
    parallelism=4,       # Number of parallel threads
    hash_len=32,         # Length of the hash in bytes
    salt_len=16,         # Length of random salt in bytes
)


class PasswordValidator:
    """
    Password policy validator

    Enforces organizational password policies including:
    - Length requirements
    - Character complexity
    - Common password prevention
    - Repeated character limits
    """

    # Common passwords list (top 100 most common - in production, use larger list)
    COMMON_PASSWORDS = {
        "password", "123456", "123456789", "12345678", "12345", "1234567",
        "password1", "123123", "1234567890", "000000", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey", "dragon",
        "master", "sunshine", "princess", "football", "shadow", "michael",
        "superman", "696969", "batman", "trustno1", "jordan", "jennifer"
    }

    @staticmethod
    def validate(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against policy

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        policy = security_config.password_policy

        # Length check
        if len(password) < policy.min_length:
            return False, f"Password must be at least {policy.min_length} characters"

        if len(password) > policy.max_length:
            return False, f"Password must not exceed {policy.max_length} characters"

        # Uppercase check
        if policy.require_uppercase and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"

        # Lowercase check
        if policy.require_lowercase and not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"

        # Digit check
        if policy.require_digits and not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        # Special character check
        if policy.require_special:
            special_regex = f"[{re.escape(policy.special_chars)}]"
            if not re.search(special_regex, password):
                return False, f"Password must contain at least one special character ({policy.special_chars})"

        # Repeated characters check
        if policy.max_repeated_chars > 0:
            pattern = r"(.)\1{" + str(policy.max_repeated_chars) + ",}"
            if re.search(pattern, password):
                return False, f"Password must not contain more than {policy.max_repeated_chars} repeated characters"

        # Common password check
        if policy.prevent_common_passwords:
            if password.lower() in PasswordValidator.COMMON_PASSWORDS:
                return False, "Password is too common, please choose a stronger password"

        return True, None


class PasswordHasher:
    """
    Password hashing utilities with multiple algorithm support

    Supports:
    - Argon2 (default, OWASP recommended)
    - BCrypt (legacy support)
    """

    @staticmethod
    def hash_password(password: str, algorithm: Optional[str] = None) -> str:
        """
        Hash password using configured algorithm

        Args:
            password: Plain text password
            algorithm: Optional algorithm override (default: from config)

        Returns:
            Hashed password string with algorithm prefix
        """
        algo = algorithm or security_config.hash_algorithm.value

        if algo == "argon2":
            hashed = ph.hash(password)
            return f"argon2${hashed}"
        elif algo == "bcrypt":
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return f"bcrypt${hashed.decode('utf-8')}"
        else:
            raise ValueError(f"Unsupported hashing algorithm: {algo}")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to check against

        Returns:
            True if password matches, False otherwise
        """
        if not hashed_password:
            return False

        try:
            # Extract algorithm prefix
            if "$" in hashed_password:
                algo, hash_value = hashed_password.split("$", 1)
            else:
                # Legacy hashes without prefix (assume bcrypt)
                algo = "bcrypt"
                hash_value = hashed_password

            if algo == "argon2":
                ph.verify(hash_value, plain_password)
                return True
            elif algo == "bcrypt":
                return bcrypt.checkpw(
                    plain_password.encode("utf-8"),
                    hash_value.encode("utf-8")
                )
            else:
                return False

        except (VerifyMismatchError, InvalidHash, ValueError):
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """
        Check if password hash needs updating (algorithm changed or parameters outdated)

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if rehashing is recommended
        """
        if not hashed_password or "$" not in hashed_password:
            return True

        algo, hash_value = hashed_password.split("$", 1)

        # Check if algorithm has changed
        if algo != security_config.hash_algorithm.value:
            return True

        # For Argon2, check if parameters need updating
        if algo == "argon2":
            try:
                return ph.check_needs_rehash(hash_value)
            except:
                return True

        return False


class TokenManager:
    """
    JWT token management with refresh tokens and blacklisting

    Features:
    - Short-lived access tokens
    - Long-lived refresh tokens
    - Token revocation via blacklist
    - Secure token generation
    - Multi-tenant organization context
    """

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        organization_id: Optional[int] = None,
        organization_role: Optional[str] = None
    ) -> str:
        """
        Create JWT access token with standard claims and optional organization context.

        Args:
            data: Payload data to encode (must include 'sub' for user ID)
            expires_delta: Optional expiration override
            organization_id: Optional organization ID for multi-tenant context
            organization_role: Optional organization role (OWNER, ADMIN, MANAGER, VIEWER)

        Returns:
            Encoded JWT token string

        Example:
            token = TokenManager.create_access_token(
                data={"sub": str(user.id)},
                organization_id=org.id,
                organization_role="ADMIN"
            )
        """
        to_encode = data.copy()

        # Set expiration
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=security_config.token.access_token_expire_minutes
            )

        # Add standard JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow(),
            "iss": security_config.token.issuer,
            "aud": security_config.token.audience,
            "jti": secrets.token_urlsafe(32),  # Unique token ID
        })

        # Add multi-tenant organization context if provided
        if organization_id is not None:
            to_encode["org_id"] = organization_id
        if organization_role is not None:
            to_encode["org_role"] = organization_role

        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=security_config.token.algorithm
        )

        return encoded_jwt

    @staticmethod
    def create_tenant_token(
        user_id: int,
        organization_id: int,
        organization_role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token with full multi-tenant context.

        This is a convenience method for creating tokens with organization context.

        Args:
            user_id: User ID to encode
            organization_id: Organization ID for tenant isolation
            organization_role: User's role in the organization
            expires_delta: Optional expiration override

        Returns:
            Encoded JWT token string with tenant context
        """
        return TokenManager.create_access_token(
            data={"sub": str(user_id)},
            expires_delta=expires_delta,
            organization_id=organization_id,
            organization_role=organization_role
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> Tuple[str, str]:
        """
        Create refresh token

        Args:
            user_id: User ID to encode in token

        Returns:
            Tuple of (token, token_id)
        """
        token_id = secrets.token_urlsafe(32)
        expire = datetime.utcnow() + timedelta(
            days=security_config.token.refresh_token_expire_days
        )

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": token_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": security_config.token.issuer,
        }

        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=security_config.token.algorithm
        )

        return token, token_id

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string
            token_type: Type of token (access or refresh)

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[security_config.token.algorithm],
                issuer=security_config.token.issuer,
                audience=security_config.token.audience if token_type == "access" else None,
                leeway=security_config.token.leeway_seconds
            )

            # Verify token type for refresh tokens
            if token_type == "refresh" and payload.get("type") != "refresh":
                raise JWTError("Invalid token type")

            return payload

        except JWTError as e:
            raise JWTError(f"Token verification failed: {str(e)}")

    @staticmethod
    def get_token_jti(token: str) -> Optional[str]:
        """
        Extract JTI (JWT ID) from token without full verification

        Args:
            token: JWT token string

        Returns:
            Token JTI or None
        """
        try:
            payload = jwt.get_unverified_claims(token)
            return payload.get("jti")
        except:
            return None


class BruteForceProtector:
    """
    Brute force attack protection

    Tracks failed authentication attempts and implements account lockout

    Note: In production, use Redis for distributed tracking across multiple servers
    """

    # In-memory storage (replace with Redis in production)
    _failed_attempts: Dict[str, list] = {}
    _lockouts: Dict[str, datetime] = {}

    @classmethod
    def record_failed_attempt(cls, identifier: str) -> bool:
        """
        Record failed authentication attempt

        Args:
            identifier: User identifier (email, IP, etc.)

        Returns:
            True if account should be locked, False otherwise
        """
        if not security_config.brute_force.enabled:
            return False

        now = datetime.utcnow()

        # Initialize tracking for this identifier
        if identifier not in cls._failed_attempts:
            cls._failed_attempts[identifier] = []

        # Add this attempt
        cls._failed_attempts[identifier].append(now)

        # Clean old attempts (outside lockout window)
        window_start = now - timedelta(
            minutes=security_config.brute_force.lockout_duration_minutes
        )
        cls._failed_attempts[identifier] = [
            attempt for attempt in cls._failed_attempts[identifier]
            if attempt > window_start
        ]

        # Check if lockout threshold exceeded
        if len(cls._failed_attempts[identifier]) >= security_config.brute_force.max_attempts:
            cls._lockouts[identifier] = now + timedelta(
                minutes=security_config.brute_force.lockout_duration_minutes
            )
            return True

        return False

    @classmethod
    def is_locked_out(cls, identifier: str) -> bool:
        """
        Check if identifier is currently locked out

        Args:
            identifier: User identifier to check

        Returns:
            True if locked out, False otherwise
        """
        if not security_config.brute_force.enabled:
            return False

        if identifier not in cls._lockouts:
            return False

        # Check if lockout has expired
        if datetime.utcnow() > cls._lockouts[identifier]:
            del cls._lockouts[identifier]
            if identifier in cls._failed_attempts:
                del cls._failed_attempts[identifier]
            return False

        return True

    @classmethod
    def clear_attempts(cls, identifier: str):
        """
        Clear failed attempts for identifier (call on successful login)

        Args:
            identifier: User identifier to clear
        """
        if identifier in cls._failed_attempts:
            del cls._failed_attempts[identifier]
        if identifier in cls._lockouts:
            del cls._lockouts[identifier]

    @classmethod
    def get_remaining_attempts(cls, identifier: str) -> int:
        """
        Get remaining login attempts before lockout

        Args:
            identifier: User identifier

        Returns:
            Number of remaining attempts
        """
        if not security_config.brute_force.enabled:
            return 999

        if cls.is_locked_out(identifier):
            return 0

        attempts = len(cls._failed_attempts.get(identifier, []))
        return max(0, security_config.brute_force.max_attempts - attempts)


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token

    Args:
        length: Token length in bytes

    Returns:
        URL-safe token string
    """
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """
    Generate API key with checksum

    Returns:
        API key string in format: barq_live_xxxxxxxxxxxx
    """
    prefix = "barq_live" if security_config.is_production else "barq_test"
    random_part = secrets.token_urlsafe(32)
    checksum = hashlib.sha256(random_part.encode()).hexdigest()[:8]
    return f"{prefix}_{random_part}_{checksum}"


def verify_api_key(api_key: str) -> bool:
    """
    Verify API key checksum

    Args:
        api_key: API key to verify

    Returns:
        True if valid, False otherwise
    """
    try:
        parts = api_key.split("_")
        if len(parts) != 3:
            return False

        prefix, random_part, checksum = parts
        expected_checksum = hashlib.sha256(random_part.encode()).hexdigest()[:8]
        return checksum == expected_checksum
    except:
        return False


# Legacy compatibility functions (maintain backward compatibility)
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Legacy function - use TokenManager.create_access_token instead"""
    return TokenManager.create_access_token(data, expires_delta)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Legacy function - use PasswordHasher.verify_password instead"""
    return PasswordHasher.verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Legacy function - use PasswordHasher.hash_password instead"""
    return PasswordHasher.hash_password(password)
