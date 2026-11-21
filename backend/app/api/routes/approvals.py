
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Approval
from backend.app.api.schemas.approval import ApprovalResponse


router = APIRouter(
    prefix="/api/v1/approvals",
    tags=["Approvals"]
)


# 1. Get all approval requests
@router.get("/", response_model=list[ApprovalResponse])
def get_approvals(db: Session = Depends(get_db)):

    approvals = db.query(Approval).order_by(
        Approval.created_at.desc()
    ).all()

    return approvals


# 2. Approve a notification
@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve_notification(
    approval_id: int,
    db: Session = Depends(get_db)
):

    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found."
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"This request has already been {approval.status}."
        )

    approval.status = "approved"
    approval.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    return approval


# 3. Reject a notification
@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject_notification(
    approval_id: int,
    db: Session = Depends(get_db)
):

    approval = db.query(Approval).filter(
        Approval.id == approval_id
    ).first()

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found."
        )

    if approval.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"This request has already been {approval.status}."
        )

    approval.status = "rejected"
    approval.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(approval)

    return approval
