"""
Security Headers Middleware

This module provides comprehensive security headers including:
- Content-Security-Policy (CSP)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security (HSTS)
- Referrer-Policy
- Permissions-Policy

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.security_config import security_config


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses

    Implements OWASP recommended security headers for web application security
    """

    def __init__(self, app):
        super().__init__(app)
        self.config = security_config

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""

        # Process request
        response = await call_next(request)

        # Add security headers
        headers = self._get_security_headers(request)

        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response

    def _get_security_headers(self, request: Request) -> dict:
        """
        Get security headers based on configuration and request context

        Args:
            request: FastAPI request object

        Returns:
            Dictionary of security headers
        """
        headers = {}

        # X-Content-Type-Options
        # Prevents MIME type sniffing
        headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options
        # Prevents clickjacking attacks
        headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection
        # Enables browser XSS filtering (legacy, CSP is preferred)
        headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy
        # Controls how much referrer information is included with requests
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy (formerly Feature-Policy)
        # Restricts which browser features can be used
        headers["Permissions-Policy"] = self._build_permissions_policy()

        # Strict-Transport-Security (HSTS)
        # Forces HTTPS connections (production only)
        if self.config.is_production:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Content-Security-Policy
        # Prevents XSS, injection attacks, and unauthorized resource loading
        headers["Content-Security-Policy"] = self._build_csp_header()

        # X-Permitted-Cross-Domain-Policies
        # Restricts Adobe Flash and PDF cross-domain access
        headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # X-DNS-Prefetch-Control
        # Controls DNS prefetching to prevent information leakage
        headers["X-DNS-Prefetch-Control"] = "off"

        # X-Download-Options
        # Prevents IE from executing downloads in site's context
        headers["X-Download-Options"] = "noopen"

        # Cross-Origin-Opener-Policy (COOP)
        # Isolates browsing context
        headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin-Embedder-Policy (COEP)
        # Prevents loading cross-origin resources without explicit permission
        if self.config.is_production:
            headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin-Resource-Policy (CORP)
        # Protects against Spectre attacks
        headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Cache-Control for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"

        # Server header (hide server information)
        headers["Server"] = "BARQ API"

        return headers

    def _build_csp_header(self) -> str:
        """
        Build Content-Security-Policy header

        Returns:
            CSP header value string
        """
        directives = []

        for directive, sources in self.config.csp_directives.items():
            directive_value = f"{directive} {' '.join(sources)}"
            directives.append(directive_value)

        # Add upgrade-insecure-requests in production
        if self.config.is_production:
            directives.append("upgrade-insecure-requests")

        # Add block-all-mixed-content in production
        if self.config.is_production:
            directives.append("block-all-mixed-content")

        return "; ".join(directives)

    def _build_permissions_policy(self) -> str:
        """
        Build Permissions-Policy header

        Returns:
            Permissions-Policy header value
        """
        # Restrictive policy by default
        policies = {
            "accelerometer": "()",
            "ambient-light-sensor": "()",
            "autoplay": "()",
            "battery": "()",
            "camera": "()",
            "display-capture": "()",
            "document-domain": "()",
            "encrypted-media": "()",
            "execution-while-not-rendered": "()",
            "execution-while-out-of-viewport": "()",
            "fullscreen": "()",
            "geolocation": "()",
            "gyroscope": "()",
            "magnetometer": "()",
            "microphone": "()",
            "midi": "()",
            "navigation-override": "()",
            "payment": "()",
            "picture-in-picture": "()",
            "publickey-credentials-get": "()",
            "screen-wake-lock": "()",
            "sync-xhr": "()",
            "usb": "()",
            "web-share": "()",
            "xr-spatial-tracking": "()",
        }

        # Allow geolocation for delivery tracking (if needed)
        # policies["geolocation"] = "(self)"

        return ", ".join([f"{key}={value}" for key, value in policies.items()])

    def _is_sensitive_endpoint(self, path: str) -> bool:
        """
        Check if endpoint contains sensitive data

        Args:
            path: Request path

        Returns:
            True if endpoint is sensitive
        """
        sensitive_patterns = [
            "/auth/",
            "/users/me",
            "/api/v1/finances",
            "/api/v1/analytics",
            "/api/v1/reports",
        ]

        return any(pattern in path for pattern in sensitive_patterns)


class HSTSMiddleware(BaseHTTPMiddleware):
    """
    HTTP Strict Transport Security (HSTS) Middleware

    Forces HTTPS connections and prevents protocol downgrade attacks
    """

    def __init__(
        self,
        app,
        max_age: int = 31536000,  # 1 year
        include_subdomains: bool = True,
        preload: bool = True
    ):
        super().__init__(app)
        self.max_age = max_age
        self.include_subdomains = include_subdomains
        self.preload = preload

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add HSTS header if using HTTPS"""

        response = await call_next(request)

        # Only add HSTS if using HTTPS
        if request.url.scheme == "https" or security_config.is_production:
            hsts_value = f"max-age={self.max_age}"

            if self.include_subdomains:
                hsts_value += "; includeSubDomains"

            if self.preload:
                hsts_value += "; preload"

            response.headers["Strict-Transport-Security"] = hsts_value

        return response


class NoSniffMiddleware(BaseHTTPMiddleware):
    """
    X-Content-Type-Options Middleware

    Prevents MIME type sniffing
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response


class FrameOptionsMiddleware(BaseHTTPMiddleware):
    """
    X-Frame-Options Middleware

    Prevents clickjacking attacks by controlling frame embedding
    """

    def __init__(self, app, option: str = "DENY"):
        """
        Initialize middleware

        Args:
            app: FastAPI application
            option: Frame option (DENY, SAMEORIGIN, or ALLOW-FROM uri)
        """
        super().__init__(app)
        self.option = option

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = self.option
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """
    X-XSS-Protection Middleware

    Enables browser XSS filtering (legacy support)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


class ReferrerPolicyMiddleware(BaseHTTPMiddleware):
    """
    Referrer-Policy Middleware

    Controls referrer information sent with requests
    """

    def __init__(self, app, policy: str = "strict-origin-when-cross-origin"):
        """
        Initialize middleware

        Args:
            app: FastAPI application
            policy: Referrer policy
        """
        super().__init__(app)
        self.policy = policy

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["Referrer-Policy"] = self.policy
        return response


def get_security_headers() -> dict:
    """
    Get all security headers as a dictionary

    Utility function for testing or custom implementations

    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-Permitted-Cross-Domain-Policies": "none",
        "X-DNS-Prefetch-Control": "off",
        "X-Download-Options": "noopen",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
        "Server": "BARQ API",
    }
