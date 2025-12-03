from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
import io

router = APIRouter()


@router.get("/export/{courier_id}")
def export_eos(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export End of Service report for a courier - stub implementation"""
    # TODO: Implement actual EOS calculation and export
    output = io.StringIO()
    output.write(f"EOS Export for Courier {courier_id} Placeholder")
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=eos_courier_{courier_id}.pdf"
        }
    )
