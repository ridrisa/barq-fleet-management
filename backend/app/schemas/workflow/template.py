from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date

class WorkflowTemplateBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    steps: List[Dict[str, Any]] = Field(..., description="JSON array of workflow steps")
    category: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=0, description="Duration in minutes")
    is_active: bool = True

class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass

class WorkflowTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None
    estimated_duration: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class WorkflowTemplateResponse(WorkflowTemplateBase):
    id: int
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
