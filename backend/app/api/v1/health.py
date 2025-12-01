from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import psutil
import os

from app.api.deps import get_db
from app.config.settings import settings

router = APIRouter()


@router.get("/live")
def liveness_check():
    """
    Kubernetes/Cloud Run liveness probe
    Returns 200 if application is running (minimal check)
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes/Cloud Run readiness probe
    Returns 200 only if application is ready to serve traffic
    Checks critical dependencies: database
    """
    checks = {}
    all_ready = True

    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "ready", "latency_ms": 0}
    except Exception as e:
        checks["database"] = {"status": "not_ready", "error": str(e)}
        all_ready = False

    # You can add more checks here (Redis, external APIs, etc.)

    if not all_ready:
        return Response(
            content={"status": "not_ready", "checks": checks, "timestamp": datetime.utcnow().isoformat()},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/")
@router.get("/detailed")
def health_check_detailed(db: Session = Depends(get_db)):
    """
    Detailed health check with comprehensive system information
    Used for monitoring dashboards and debugging
    """
    health_data: Dict[str, Any] = {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": _get_uptime(),
        "checks": {},
        "system": {}
    }

    # Database check
    try:
        start_time = datetime.utcnow()
        db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        health_data["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": round(latency, 2)
        }
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # System metrics
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        health_data["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "percent_used": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "percent_used": disk.percent
            }
        }
    except Exception as e:
        health_data["system"]["error"] = str(e)

    return health_data


def _get_uptime() -> float:
    """Calculate application uptime in seconds"""
    try:
        return psutil.Process(os.getpid()).create_time()
    except:
        return 0.0
