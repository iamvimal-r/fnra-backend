from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, auth, database, models

router = APIRouter(
    prefix="/billing",
    tags=["billing"]
)

def _bill_to_response(b: models.Bill) -> dict:
    return {
        "_id": str(b.id),
        "user_id": str(b.user_id),
        "amount": b.amount,
        "description": b.description,
        "due_date": b.due_date,
        "status": b.status,
    }


@router.get("/me", response_model=List[schemas.BillResponse])
def get_my_bills(current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Fetch bills for the logged-in user."""
    bills = db.query(models.Bill).filter(models.Bill.user_id == str(current_user.id)).order_by(models.Bill.due_date.desc()).all()
    return [_bill_to_response(b) for b in bills]


@router.get("/", response_model=List[schemas.BillResponse])
def get_all_bills(current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Fetch all bills (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    bills = db.query(models.Bill).order_by(models.Bill.due_date.desc()).all()
    return [_bill_to_response(b) for b in bills]


@router.post("/", response_model=schemas.BillResponse, status_code=status.HTTP_201_CREATED)
def create_bill(bill: schemas.BillCreate, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Create a new bill (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    new_bill = models.Bill(
        user_id=bill.user_id,
        amount=bill.amount,
        description=bill.description,
        due_date=bill.due_date,
        status="Pending",
    )
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return _bill_to_response(new_bill)


@router.put("/{bill_id}/pay")
def pay_bill(bill_id: str, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Mock payment processor to mark a bill as paid."""
    try:
        bid = int(bill_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill = db.query(models.Bill).filter(models.Bill.id == bid).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    if str(bill.user_id) != str(current_user.id) and getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to pay this bill")
        
    bill.status = "Paid"
    db.commit()
    return {"message": "Payment successful"}


@router.delete("/{bill_id}")
def delete_bill(bill_id: str, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Delete a bill (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        bid = int(bill_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    bill = db.query(models.Bill).filter(models.Bill.id == bid).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    db.delete(bill)
    db.commit()
    return {"message": "Bill deleted successfully"}
