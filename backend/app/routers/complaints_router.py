from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import schemas, auth, database, models

router = APIRouter(
    prefix="/complaints",
    tags=["complaints"]
)

class ComplaintStatusUpdate(BaseModel):
    status: str


def _complaint_to_response(c: models.Complaint) -> dict:
    return {
        "_id": str(c.id),
        "title": c.title,
        "description": c.description,
        "status": c.status,
        "user_id": str(c.user_id) if c.user_id else "",
        "date_submitted": c.date_submitted,
    }


@router.get("/", response_model=List[schemas.ComplaintResponse])
def get_complaints(current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Fetch complaints. Admins see all, residents see their own."""
    if getattr(current_user, "role", None) == "admin":
        complaints = db.query(models.Complaint).order_by(models.Complaint.date_submitted.desc()).all()
    else:
        complaints = db.query(models.Complaint).filter(models.Complaint.user_id == str(current_user.id)).order_by(models.Complaint.date_submitted.desc()).all()
        
    return [_complaint_to_response(c) for c in complaints]


@router.post("/", response_model=schemas.ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint: schemas.ComplaintCreate, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Submit a new complaint."""
    new_complaint = models.Complaint(
        title=complaint.title,
        description=complaint.description,
        status="Open",
        user_id=str(current_user.id),
        date_submitted=datetime.utcnow(),
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return _complaint_to_response(new_complaint)


@router.put("/{complaint_id}/status")
def update_complaint_status(complaint_id: str, status_update: ComplaintStatusUpdate, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Update complaint status (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if status_update.status not in ["Open", "In Progress", "Resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        cid = int(complaint_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint = db.query(models.Complaint).filter(models.Complaint.id == cid).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    complaint.status = status_update.status
    db.commit()
    return {"message": "Status updated successfully"}


@router.delete("/{complaint_id}")
def delete_complaint(complaint_id: str, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Delete a complaint."""
    try:
        cid = int(complaint_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint = db.query(models.Complaint).filter(models.Complaint.id == cid).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    if getattr(current_user, "role", None) != "admin" and str(complaint.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this complaint")
        
    db.delete(complaint)
    db.commit()
    return {"message": "Complaint deleted successfully"}
