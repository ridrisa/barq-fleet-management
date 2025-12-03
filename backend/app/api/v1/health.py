import os
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.dependencies import get_db

router = APIRouter()


@router.get("/live")
def liveness_check():
    """Kubernetes/Cloud Run liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes/Cloud Run readiness probe.
    Returns 200 only if application is ready to serve traffic.
    """
    checks: Dict[str, Any] = {}
    all_ready = True

    try:
        start = datetime.utcnow()
        db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        checks["database"] = {"status": "ready", "latency_ms": round(latency, 2)}
    except Exception as e:
        checks["database"] = {"status": "not_ready", "error": str(e)}
        all_ready = False

    if not all_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": checks,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    return {"status": "ready", "checks": checks, "timestamp": datetime.utcnow().isoformat()}


@router.get("/")
@router.get("/detailed")
def health_check_detailed(db: Session = Depends(get_db)):
    """Detailed health check with comprehensive system information"""
    health_data: Dict[str, Any] = {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": _get_uptime(),
        "checks": {},
        "system": {},
    }

    try:
        start_time = datetime.utcnow()
        db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000
        health_data["checks"]["database"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["checks"]["database"] = {"status": "unhealthy", "error": str(e)}

    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        health_data["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "percent_used": memory.percent,
            },
            "disk": {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "percent_used": disk.percent,
            },
        }
    except Exception as e:
        health_data["system"]["error"] = str(e)

    return health_data


def _get_uptime() -> float:
    """Calculate application uptime in seconds"""
    try:
        proc = psutil.Process(os.getpid())
        return max(0.0, datetime.utcnow().timestamp() - proc.create_time())
    except Exception:
        return 0.0
