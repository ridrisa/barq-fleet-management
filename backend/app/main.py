"""
BARQ Fleet Management API

Production-grade FastAPI application with:
- Structured logging
- Exception handling
- Performance monitoring
- Health checks
- CORS configuration
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.config.settings import settings
from app.core.exceptions import AppException, get_exception_handlers
from strawberry.fastapi import GraphQLRouter
from app.graphql import schema
from app.core.database import get_db
from app.core.logging import (
    RequestLogger,
    get_logger,
    setup_logging,
)
from app.middleware.performance import setup_performance_middleware
from app.version import __version__, get_version_info

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Setup performance middleware (compression, caching, monitoring)
    setup_performance_middleware(app)

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
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
    async def get_context():
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
    def root():
        """Root endpoint with API information."""
        return {
            "message": "BARQ Fleet Management API",
            "version": __version__,
            "docs": f"{settings.API_V1_STR}/docs",
            "health": "/health",
        }

    # Basic health check (for load balancer)
    @app.get("/health", tags=["health"])
    def health_check():
        """Basic health check endpoint."""
        return {
            "status": "healthy",
            "version": __version__,
            "environment": settings.ENVIRONMENT,
        }

    # Version endpoint
    @app.get("/version", tags=["info"])
    def version_info():
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
