"""
BARQ Fleet Management API

Production-grade FastAPI application with:
- Structured logging
- Exception handling
- Performance monitoring
- Health checks
- CORS configuration
- Sentry error tracking
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Coroutine

import sentry_sdk
from fastapi import FastAPI, Request
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter

from app.api.api import api_router
from app.config.settings import settings
from app.core.database import get_db
from app.core.exceptions import AppException, get_exception_handlers
from app.core.logging import (
    RequestLogger,
    get_logger,
    setup_logging,
)
from app.graphql import schema
from app.middleware.performance import setup_performance_middleware
from app.version import __version__, get_version_info

# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=f"barq-fleet-backend@{__version__}",
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=None,  # Capture all log levels as breadcrumbs
                event_level=None,  # Don't send log messages as events
            ),
        ],
        # Set to True in production for better performance insights
        enable_tracing=True,
        # Attach current user info to events
        send_default_pii=False,
    )

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info(
        "Starting BARQ Fleet Management API",
        extra={
            "version": __version__,
            "environment": settings.ENVIRONMENT,
        },
    )

    # Validate production settings
    if settings.ENVIRONMENT.lower() == "production":
        if settings.SECRET_KEY in ["change-me-in-production", "dev-secret-key", ""]:
            logger.warning("SECRET_KEY should be changed in production!")

    yield

    # Shutdown
    logger.info("Shutting down BARQ Fleet Management API")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        description="BARQ Fleet Management System - Production API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # CORS middleware - must be added FIRST (runs last in the stack, wrapping everything)
    # Use environment-specific origins from settings, fallback to all for dev
    cors_origins = settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"]

    # In staging/production, always include the Cloud Run URLs
    if settings.ENVIRONMENT.lower() in ["staging", "production"]:
        staging_origins = [
            "https://barq-web-staging-frydalfroq-ww.a.run.app",
            "https://barq-web-staging-869422381378.me-central1.run.app",
            "http://localhost:3000",
            "http://localhost:5173",
        ]
        cors_origins = list(set(cors_origins + staging_origins))

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Setup performance middleware (compression, caching, monitoring)
    setup_performance_middleware(app)

    # Sentry user context middleware - set user info for error tracking
    @app.middleware("http")
    async def sentry_user_context(
        request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
    ) -> Response:
        """Set Sentry user context from JWT token for error attribution."""
        # Try to extract user info from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                from jose import jwt
                from app.config.settings import settings as app_settings

                # Decode without full verification to get user info
                # (verification happens in the actual endpoint)
                payload = jwt.decode(
                    token,
                    app_settings.SECRET_KEY,
                    algorithms=[app_settings.ALGORITHM],
                    options={"verify_exp": False, "verify_aud": False, "verify_iss": False},
                )
                user_id = payload.get("sub")
                org_id = payload.get("org_id")

                if user_id:
                    sentry_sdk.set_user({
                        "id": user_id,
                        "org_id": str(org_id) if org_id else None,
                    })
            except Exception:
                # Don't fail requests due to Sentry issues
                pass

        response = await call_next(request)

        # Clear user context after request
        sentry_sdk.set_user(None)

        return response

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Coroutine[Any, Any, Response]]
    ) -> Response:
        """Log all requests with correlation IDs."""
        return await RequestLogger.log_request(request, call_next)

    # Exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application exceptions with consistent format."""
        logger.error(
            f"Application error: {exc.detail}",
            extra={
                "code": exc.code,
                "status_code": exc.status_code,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Capture exception in Sentry
        sentry_sdk.capture_exception(exc)

        logger.exception(
            f"Unexpected error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "ERR_1000",
                    "message": "An unexpected error occurred. Please try again later.",
                    "status": 500,
                }
            },
        )

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # GraphQL endpoint with context for database session
    async def get_context() -> dict[str, Any]:
        db = next(get_db())
        try:
            return {"db": db}
        finally:
            pass  # Session cleanup handled by dependency

    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
    )
    app.include_router(graphql_app, prefix="/graphql")

    # Root endpoint
    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        """Root endpoint with API information."""
        return {
            "message": "BARQ Fleet Management API",
            "version": __version__,
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
        }

    # Basic health check (for load balancer)
    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": __version__,
            "environment": settings.ENVIRONMENT,
        }

    # Version endpoint
    @app.get("/version", tags=["info"])
    def version_info() -> dict[str, Any]:
        """Get detailed version information."""
        return get_version_info()

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
