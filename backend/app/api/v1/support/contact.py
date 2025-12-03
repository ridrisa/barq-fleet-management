"""Contact Support API Routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.support import (
    ContactFormSubmit, ContactFormResponse, DepartmentInfo
)
from app.services.support import contact_support_service


router = APIRouter()


@router.post("/submit", response_model=ContactFormResponse)
def submit_contact_form(
    form_data: ContactFormSubmit,
    db: Session = Depends(get_db),
):
    """
    Submit a contact form

    This endpoint is public - no authentication required.
    Automatically creates a support ticket for the submission.
    """
    result = contact_support_service.submit_contact_form(
        db,
        name=form_data.name,
        email=form_data.email,
        subject=form_data.subject,
        message=form_data.message,
        phone=form_data.phone,
        department=form_data.department,
        urgency=form_data.urgency
    )
    return ContactFormResponse(**result)


@router.get("/departments", response_model=List[DepartmentInfo])
def get_departments():
    """
    Get list of departments for contact routing

    This endpoint is public - no authentication required.
    """
    departments = contact_support_service.get_departments()
    return [DepartmentInfo(**dept) for dept in departments]


@router.get("/info")
def get_contact_info():
    """
    Get general contact information

    This endpoint is public - no authentication required.
    """
    return {
        "company_name": "BARQ Fleet Management",
        "general_email": "info@barq.sa",
        "support_email": "support@barq.sa",
        "phone": "+966-XXX-XXX-XXXX",
        "address": "Riyadh, Saudi Arabia",
        "working_hours": {
            "weekdays": "Sunday - Thursday, 8:00 AM - 6:00 PM",
            "weekend": "Closed",
            "timezone": "Arabia Standard Time (AST)"
        },
        "emergency_support": {
            "available": True,
            "hours": "24/7 for critical issues",
            "phone": "+966-XXX-XXX-XXXX"
        },
        "social_media": {
            "twitter": "@BARQFleet",
            "linkedin": "BARQ Fleet Management",
            "facebook": "BARQFleetManagement"
        }
    }


@router.get("/urgency-levels")
def get_urgency_levels():
    """
    Get available urgency levels for contact form

    This endpoint is public - no authentication required.
    """
    return [
        {
            "value": "normal",
            "label": "Normal",
            "description": "Standard inquiry, response within 24-48 hours",
            "response_time": "24-48 hours"
        },
        {
            "value": "high",
            "label": "High",
            "description": "Important issue requiring faster response",
            "response_time": "12-24 hours"
        },
        {
            "value": "critical",
            "label": "Critical",
            "description": "Urgent issue affecting operations",
            "response_time": "2-4 hours"
        }
    ]
