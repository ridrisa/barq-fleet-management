"""
CSRF (Cross-Site Request Forgery) Protection Middleware

This module provides CSRF protection including:
- Double-submit cookie pattern
- Token generation and validation
- SameSite cookie attributes
- Origin header validation
- Exempt endpoints configuration

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import secrets
from typing import Callable, List, Optional, Set

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.security_config import security_config


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware using double-submit cookie pattern

    How it works:
    1. Generate CSRF token on first request
    2. Store token in cookie (HttpOnly=False so JS can read it)
    3. Require token in header for state-changing requests (POST, PUT, DELETE, PATCH)
    4. Validate token matches cookie value

    Features:
    - Automatic token generation
    - Double-submit cookie pattern
    - Origin/Referer header validation
    - Configurable exempt endpoints
    - SameSite cookie attribute
    """

    # HTTP methods that require CSRF protection
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

    # Endpoints that don't require CSRF protection
    EXEMPT_PATHS: Set[str] = {
        "/health",
        "/",
        "/api/v1/docs",
        "/api/v1/openapi.json",
        "/api/v1/redoc",
        "/api/v1/auth/login",  # OAuth flow handles CSRF differently
        "/api/v1/auth/google/callback",
    }

    # Paths that start with these prefixes are exempt
    EXEMPT_PREFIXES: List[str] = [
        "/static/",
        "/media/",
        "/public/",
    ]

    def __init__(
        self,
        app,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_secure: bool = True,
        cookie_samesite: str = "Lax",
        token_length: int = 32,
    ):
        """
        Initialize CSRF protection middleware

        Args:
            app: FastAPI application
            cookie_name: Name of CSRF cookie
            header_name: Name of CSRF header
            cookie_secure: Set Secure flag on cookie (HTTPS only)
            cookie_samesite: SameSite attribute (Strict, Lax, or None)
            token_length: Length of CSRF token in bytes
        """
        super().__init__(app)
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_secure = cookie_secure and security_config.is_production
        self.cookie_samesite = cookie_samesite
        self.token_length = token_length

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with CSRF protection"""

        # Check if endpoint is exempt
        if self._is_exempt(request):
            response = await call_next(request)
            return response

        # Check if method requires CSRF protection
        if request.method in self.PROTECTED_METHODS:
            # Validate CSRF token
            self._validate_csrf_token(request)

            # Validate Origin/Referer headers
            self._validate_origin(request)

        # Process request
        response = await call_next(request)

        # Ensure CSRF token cookie is set
        if self.cookie_name not in request.cookies:
            self._set_csrf_cookie(response)

        return response

    def _is_exempt(self, request: Request) -> bool:
        """
        Check if request is exempt from CSRF protection

        Args:
            request: FastAPI request object

        Returns:
            True if exempt, False otherwise
        """
        path = request.url.path

        # Check exact path match
        if path in self.EXEMPT_PATHS:
            return True

        # Check prefix match
        for prefix in self.EXEMPT_PREFIXES:
            if path.startswith(prefix):
                return True

        # API keys are exempt (assume they're used programmatically)
        if "X-API-Key" in request.headers:
            return True

        return False

    def _validate_csrf_token(self, request: Request):
        """
        Validate CSRF token

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If CSRF validation fails
        """
        # Get token from cookie
        cookie_token = request.cookies.get(self.cookie_name)

        if not cookie_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token missing from cookie"
            )

        # Get token from header
        header_token = request.headers.get(self.header_name)

        if not header_token:
            # Also check in form data for traditional forms
            if hasattr(request, "form"):
                form_data = request.form()
                header_token = form_data.get(self.cookie_name)

        if not header_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"CSRF token missing from header ({self.header_name})",
            )

        # Validate tokens match (constant-time comparison)
        if not secrets.compare_digest(cookie_token, header_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token validation failed"
            )

    def _validate_origin(self, request: Request):
        """
        Validate Origin or Referer header

        Args:
            request: FastAPI request object

        Raises:
            HTTPException: If origin validation fails
        """
        # Get Origin header (preferred)
        origin = request.headers.get("Origin")

        # Fall back to Referer header
        if not origin:
            referer = request.headers.get("Referer")
            if referer:
                # Extract origin from referer
                origin = self._extract_origin_from_url(referer)

        if not origin:
            # In production, require Origin/Referer for state-changing requests
            if security_config.is_production:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Origin or Referer header required",
                )
            return

        # Validate origin matches allowed origins
        if not self._is_allowed_origin(origin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Origin not allowed: {origin}"
            )

    def _is_allowed_origin(self, origin: str) -> bool:
        """
        Check if origin is in allowed list

        Args:
            origin: Origin URL

        Returns:
            True if allowed, False otherwise
        """
        allowed_origins = security_config.cors.allow_origins

        # Exact match
        if origin in allowed_origins:
            return True

        # Wildcard match (if configured)
        if "*" in allowed_origins:
            return True

        # Parse and check domain
        from urllib.parse import urlparse

        parsed = urlparse(origin)
        origin_host = f"{parsed.scheme}://{parsed.netloc}"

        return origin_host in allowed_origins

    def _extract_origin_from_url(self, url: str) -> str:
        """Extract origin from full URL"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _set_csrf_cookie(self, response: Response):
        """
        Set CSRF token cookie

        Args:
            response: Response object to set cookie on
        """
        # Generate new token
        token = self._generate_token()

        # Set cookie
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            max_age=None,  # Session cookie (expires when browser closes)
            path="/",
            secure=self.cookie_secure,
            httponly=False,  # JS needs to read this
            samesite=self.cookie_samesite,
        )

    def _generate_token(self) -> str:
        """
        Generate cryptographically secure CSRF token

        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(self.token_length)


class CSRFTokenGenerator:
    """
    Utility class for generating and validating CSRF tokens

    Can be used independently of middleware for custom implementations
    """

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate CSRF token

        Args:
            length: Token length in bytes

        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def validate_token(cookie_token: str, header_token: str) -> bool:
        """
        Validate CSRF tokens match

        Args:
            cookie_token: Token from cookie
            header_token: Token from header

        Returns:
            True if tokens match, False otherwise
        """
        if not cookie_token or not header_token:
            return False

        return secrets.compare_digest(cookie_token, header_token)


def get_csrf_token(request: Request) -> Optional[str]:
    """
    Get CSRF token from request

    Args:
        request: FastAPI request object

    Returns:
        CSRF token or None
    """
    return request.cookies.get("csrf_token")


def generate_csrf_token() -> str:
    """
    Generate new CSRF token

    Returns:
        CSRF token string
    """
    return CSRFTokenGenerator.generate_token()


def validate_csrf_token(request: Request, token: str) -> bool:
    """
    Validate CSRF token against request cookie

    Args:
        request: FastAPI request object
        token: Token to validate

    Returns:
        True if valid, False otherwise
    """
    cookie_token = get_csrf_token(request)
    if not cookie_token:
        return False

    return CSRFTokenGenerator.validate_token(cookie_token, token)


# Decorator for endpoint-specific CSRF protection
def csrf_protect(func: Callable) -> Callable:
    """
    Decorator to enforce CSRF protection on specific endpoints

    Usage:
        @router.post("/protected-endpoint")
        @csrf_protect
        async def protected_endpoint(request: Request):
            ...
    """

    async def wrapper(*args, request: Request = None, **kwargs):
        if request is None:
            request = kwargs.get("request")

        if request is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object required for CSRF protection",
            )

        # Get tokens
        cookie_token = request.cookies.get("csrf_token")
        header_token = request.headers.get("X-CSRF-Token")

        # Validate
        if not CSRFTokenGenerator.validate_token(cookie_token or "", header_token or ""):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed"
            )

        return await func(*args, request=request, **kwargs)

    return wrapper


# Decorator to exempt endpoint from CSRF protection
def csrf_exempt(func: Callable) -> Callable:
    """
    Decorator to mark endpoint as exempt from CSRF protection

    Usage:
        @router.post("/public-webhook")
        @csrf_exempt
        async def webhook(request: Request):
            ...
    """
    # Mark function as CSRF exempt
    func._csrf_exempt = True  # type: ignore
    return func
