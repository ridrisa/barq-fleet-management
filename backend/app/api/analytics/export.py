"""Data Export API

Export analytics data in various formats (CSV, Excel, JSON) with streaming support.
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from pydantic import BaseModel
import io
import json

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.utils.export import (
    export_to_csv,
    export_to_json,
    export_to_excel_dict,
    validate_export_data,
    filter_columns,
    sort_data,
    generate_export_filename,
    chunk_data_for_export
)


router = APIRouter()


class ExportRequest(BaseModel):
    """Export request schema"""
    data_type: str  # deliveries, fleet, financial, etc.
    format: str = "csv"  # csv, excel, json
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None
    sort_by: Optional[str] = None
    sort_desc: bool = False
    limit: Optional[int] = None


@router.post("/generate")
def generate_export(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate data export in requested format"""
    # Set default date range if not provided
    if not request.end_date:
        request.end_date = date.today()
    if not request.start_date:
        request.start_date = request.end_date - timedelta(days=30)

    # Fetch data based on data_type
    # This is a template - implement actual data fetching
    sample_data = [
        {
            "id": 1,
            "date": request.start_date.isoformat(),
            "metric1": 100,
            "metric2": 200.50,
            "metric3": "Sample"
        },
        {
            "id": 2,
            "date": (request.start_date + timedelta(days=1)).isoformat(),
            "metric1": 110,
            "metric2": 220.75,
            "metric3": "Sample"
        }
    ]

    # Validate data
    is_valid, error_message = validate_export_data(sample_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Filter columns if specified
    if request.columns:
        sample_data = filter_columns(sample_data, include_columns=request.columns)

    # Sort data if specified
    if request.sort_by:
        sample_data = sort_data(sample_data, request.sort_by, request.sort_desc)

    # Apply limit if specified
    if request.limit:
        sample_data = sample_data[:request.limit]

    # Generate filename
    filename = generate_export_filename(
        f"{request.data_type}_export",
        request.format
    )

    # Export based on format
    if request.format == "csv":
        csv_content = export_to_csv(sample_data, columns=request.columns)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    elif request.format == "json":
        json_data = export_to_json(sample_data)
        return Response(
            content=json.dumps(json_data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    elif request.format == "excel":
        # For Excel, you would need openpyxl or xlsxwriter
        # This returns the structure - implement actual Excel generation
        excel_data = export_to_excel_dict(sample_data, columns=request.columns)
        return {
            "message": "Excel export prepared",
            "filename": filename,
            "data": excel_data
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")


@router.get("/deliveries/csv")
def export_deliveries_csv(
    db: Session = Depends(get_db),
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Export deliveries data as CSV"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Fetch delivery data - implement actual query
    data = []

    csv_content = export_to_csv(data)
    filename = generate_export_filename("deliveries", "csv")

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/fleet/csv")
def export_fleet_csv(
    db: Session = Depends(get_db),
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Export fleet data as CSV"""
    # Fetch fleet data - implement actual query
    data = []

    csv_content = export_to_csv(data)
    filename = generate_export_filename("fleet", "csv")

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/financial/csv")
def export_financial_csv(
    db: Session = Depends(get_db),
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    current_user: User = Depends(get_current_user),
):
    """Export financial data as CSV"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Fetch financial data - implement actual query
    data = []

    csv_content = export_to_csv(data)
    filename = generate_export_filename("financial", "csv")

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stream/{data_type}")
def stream_export(
    data_type: str,
    db: Session = Depends(get_db),
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user: User = Depends(get_current_user),
):
    """Stream large dataset export"""
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)

    def generate_csv_stream():
        """Generator for streaming CSV data"""
        # Yield header
        yield "id,date,metric1,metric2,metric3\n"

        # Fetch and yield data in chunks
        chunk_size = 1000
        offset = 0

        while True:
            # Fetch chunk - implement actual query with offset/limit
            chunk = []  # Replace with actual data fetch

            if not chunk:
                break

            for row in chunk:
                yield f"{row.get('id')},{row.get('date')},{row.get('metric1')},{row.get('metric2')},{row.get('metric3')}\n"

            offset += chunk_size

    def generate_json_stream():
        """Generator for streaming JSON data"""
        yield '{"data": ['

        chunk_size = 1000
        offset = 0
        first = True

        while True:
            # Fetch chunk - implement actual query
            chunk = []  # Replace with actual data fetch

            if not chunk:
                break

            for row in chunk:
                if not first:
                    yield ","
                yield json.dumps(row)
                first = False

            offset += chunk_size

        yield ']}'

    # Select generator based on format
    if format == "csv":
        generator = generate_csv_stream()
        media_type = "text/csv"
    else:
        generator = generate_json_stream()
        media_type = "application/json"

    filename = generate_export_filename(f"{data_type}_stream", format)

    return StreamingResponse(
        generator,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/templates")
def get_export_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get predefined export templates"""
    templates = [
        {
            "id": 1,
            "name": "Daily Operations Export",
            "description": "Export daily operational data",
            "data_type": "deliveries",
            "default_format": "csv",
            "columns": ["id", "date", "courier", "status", "zone", "revenue"],
            "filters": {"period": "last_7_days"}
        },
        {
            "id": 2,
            "name": "Fleet Status Export",
            "description": "Export current fleet status",
            "data_type": "fleet",
            "default_format": "excel",
            "columns": ["vehicle_id", "registration", "type", "status", "utilization"],
            "filters": {}
        },
        {
            "id": 3,
            "name": "Monthly Financial Export",
            "description": "Export monthly financial summary",
            "data_type": "financial",
            "default_format": "excel",
            "columns": ["date", "revenue", "costs", "profit", "margin"],
            "filters": {"period": "current_month"}
        }
    ]

    return templates


@router.post("/schedule")
def schedule_export(
    data_type: str,
    frequency: str = Query(..., regex="^(daily|weekly|monthly)$"),
    format: str = Query("csv", regex="^(csv|excel|pdf)$"),
    recipients: List[str] = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Schedule recurring data export"""
    # Implement actual scheduling logic
    return {
        "message": "Export scheduled successfully",
        "schedule_id": 1,
        "data_type": data_type,
        "frequency": frequency,
        "format": format,
        "recipients": recipients,
        "next_run": (datetime.now() + timedelta(days=1)).isoformat()
    }


@router.get("/scheduled")
def get_scheduled_exports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of scheduled exports"""
    schedules = [
        {
            "id": 1,
            "data_type": "deliveries",
            "frequency": "daily",
            "format": "csv",
            "recipients": ["manager@example.com"],
            "is_active": True,
            "next_run": (datetime.now() + timedelta(days=1)).isoformat(),
            "last_run": datetime.now().isoformat()
        }
    ]

    return schedules


@router.delete("/scheduled/{schedule_id}")
def delete_scheduled_export(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete scheduled export"""
    # Implement actual deletion
    return {"message": "Scheduled export deleted successfully"}


@router.get("/history")
def get_export_history(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    """Get export history"""
    history = [
        {
            "id": 1,
            "data_type": "deliveries",
            "format": "csv",
            "exported_at": datetime.now().isoformat(),
            "exported_by": current_user.email,
            "row_count": 1000,
            "file_size_kb": 250,
            "download_url": "/api/analytics/export/download/1"
        }
    ]

    return history


@router.get("/download/{export_id}")
def download_export_file(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download previously generated export file"""
    # Implement actual file retrieval
    raise HTTPException(status_code=404, detail="Export file not found or expired")


@router.get("/formats")
def get_supported_formats(
    current_user: User = Depends(get_current_user),
):
    """Get list of supported export formats"""
    return {
        "formats": [
            {
                "format": "csv",
                "description": "Comma-Separated Values",
                "mime_type": "text/csv",
                "supports_streaming": True,
                "max_rows": 1000000
            },
            {
                "format": "json",
                "description": "JavaScript Object Notation",
                "mime_type": "application/json",
                "supports_streaming": True,
                "max_rows": 100000
            },
            {
                "format": "excel",
                "description": "Microsoft Excel",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "supports_streaming": False,
                "max_rows": 100000
            },
            {
                "format": "pdf",
                "description": "Portable Document Format",
                "mime_type": "application/pdf",
                "supports_streaming": False,
                "max_rows": 10000
            }
        ]
    }
