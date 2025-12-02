from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.workflow import workflow_comment
from app.schemas.workflow import (
    WorkflowCommentCreate,
    WorkflowCommentUpdate,
    WorkflowCommentResponse,
    WorkflowCommentWithUser,
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowCommentResponse])
def list_comments(
    workflow_instance_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List workflow comments with optional filtering by workflow instance"""
    if workflow_instance_id:
        comments = db.query(workflow_comment.model).filter(
            workflow_comment.model.workflow_instance_id == workflow_instance_id
        ).offset(skip).limit(limit).all()
    else:
        comments = workflow_comment.get_multi(db, skip=skip, limit=limit)
    return comments


@router.post("/", response_model=WorkflowCommentResponse, status_code=201)
def create_comment(
    comment_in: WorkflowCommentCreate,
    db: Session = Depends(get_db),
):
    """Create a new workflow comment"""
    comment = workflow_comment.create(db, obj_in=comment_in)
    return comment


@router.get("/{comment_id}", response_model=WorkflowCommentResponse)
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    """Get a workflow comment by ID"""
    comment = workflow_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.put("/{comment_id}", response_model=WorkflowCommentResponse)
def update_comment(
    comment_id: int,
    comment_in: WorkflowCommentUpdate,
    db: Session = Depends(get_db),
):
    """Update a workflow comment"""
    comment = workflow_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Mark as edited
    update_data = comment_in.model_dump(exclude_unset=True)
    if "comment" in update_data:
        update_data["is_edited"] = True
        from datetime import datetime
        update_data["edited_at"] = datetime.utcnow()

    comment = workflow_comment.update(db, db_obj=comment, obj_in=update_data)
    return comment


@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
):
    """Delete a workflow comment"""
    comment = workflow_comment.get(db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    workflow_comment.remove(db, id=comment_id)
    return None


@router.get("/instance/{instance_id}/thread", response_model=List[WorkflowCommentResponse])
def get_comment_thread(
    instance_id: int,
    db: Session = Depends(get_db),
):
    """Get all comments for a workflow instance in threaded format"""
    comments = db.query(workflow_comment.model).filter(
        workflow_comment.model.workflow_instance_id == instance_id,
        workflow_comment.model.parent_comment_id == None
    ).order_by(workflow_comment.model.created_at.desc()).all()

    return comments
