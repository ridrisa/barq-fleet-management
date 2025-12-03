from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
import io

router = APIRouter()


@router.get("/export")
def export_gosi(
    month: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export GOSI report - stub implementation"""
    # TODO: Implement actual GOSI export
    output = io.StringIO()
    output.write("GOSI Export Placeholder")
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=gosi_{month}.csv"
        }
    )
