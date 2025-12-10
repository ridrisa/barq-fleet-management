"""
External integrations API endpoints

Provides integration with:
- BigQuery (SANED performance data)
"""
from fastapi import APIRouter

from app.api.v1.integrations import bigquery

router = APIRouter()

# Include BigQuery integration routes
router.include_router(bigquery.router, prefix="/bigquery", tags=["bigquery"])
