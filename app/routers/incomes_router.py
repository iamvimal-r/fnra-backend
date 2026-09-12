from datetime import datetime
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, auth, database, models

router = APIRouter(
    prefix="/incomes",
    tags=["incomes"]
)


def _income_to_response(inc: models.Income) -> dict:
    return {
        "_id": str(inc.id),
        "title": inc.title,
        "amount": inc.amount,
        "category": inc.category,
        "income_date": inc.income_date,
        "description": inc.description,
        "created_by": str(inc.created_by),
        "created_at": inc.created_at,
    }


@router.post("/", response_model=schemas.IncomeResponse, status_code=status.HTTP_201_CREATED)
def create_income(
    income: schemas.IncomeCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Register a new income. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create incomes")
        
    new_income = models.Income(
        title=income.title,
        amount=income.amount,
        category=income.category,
        income_date=income.income_date,
        description=income.description,
        created_by=str(current_user.id),
        created_at=datetime.utcnow(),
    )
    db.add(new_income)
    db.commit()
    db.refresh(new_income)
    
    return _income_to_response(new_income)


@router.get("/", response_model=List[schemas.IncomeResponse])
def get_all_incomes(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    category: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Retrieve all other incomes. Accessible by all authenticated users."""
    query = db.query(models.Income)
    if category:
        query = query.filter(models.Income.category == category)
        
    incomes_list = query.order_by(models.Income.income_date.desc()).all()
    return [_income_to_response(inc) for inc in incomes_list]


@router.get("/summary")
def get_incomes_summary(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Fetch income totals and categories summary breakdown."""
    incomes = db.query(models.Income).all()
    
    total = 0.0
    by_category = {}
    
    for inc in incomes:
        amt = float(inc.amount or 0.0)
        total += amt
        cat = inc.category or "Other"
        by_category[cat] = by_category.get(cat, 0.0) + amt
        
    category_summary = [{"category": k, "amount": v} for k, v in by_category.items()]
    
    return {
        "total_amount": total,
        "by_category": category_summary
    }


@router.get("/{income_id}", response_model=schemas.IncomeResponse)
def get_income(
    income_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Retrieve details of a single income."""
    try:
        iid = int(income_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid income ID format")
        
    inc = db.query(models.Income).filter(models.Income.id == iid).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Income not found")
        
    return _income_to_response(inc)


@router.put("/{income_id}", response_model=schemas.IncomeResponse)
def update_income(
    income_id: str,
    income: schemas.IncomeCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Edit an income record. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit incomes")
        
    try:
        iid = int(income_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid income ID format")
        
    existing = db.query(models.Income).filter(models.Income.id == iid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Income not found")
        
    existing.title = income.title
    existing.amount = income.amount
    existing.category = income.category
    existing.income_date = income.income_date
    existing.description = income.description
    
    db.commit()
    db.refresh(existing)
    return _income_to_response(existing)


@router.delete("/{income_id}", status_code=status.HTTP_200_OK)
def delete_income(
    income_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Remove an income record. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete incomes")
        
    try:
        iid = int(income_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid income ID format")
        
    inc = db.query(models.Income).filter(models.Income.id == iid).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Income not found")

    db.delete(inc)
    db.commit()
    return {"message": "Income deleted successfully"}
