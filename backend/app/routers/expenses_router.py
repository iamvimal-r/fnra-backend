from datetime import datetime
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, auth, database, models

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)


def _expense_to_response(exp: models.Expense) -> dict:
    return {
        "_id": str(exp.id),
        "title": exp.title,
        "amount": exp.amount,
        "category": exp.category,
        "expense_date": exp.expense_date,
        "description": exp.description,
        "created_by": str(exp.created_by),
        "created_at": exp.created_at,
    }


@router.post("/", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: schemas.ExpenseCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Register a new expenditure. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create expenses")
        
    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        expense_date=expense.expense_date,
        description=expense.description,
        created_by=str(current_user.id),
        created_at=datetime.utcnow(),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return _expense_to_response(new_expense)


@router.get("/", response_model=List[schemas.ExpenseResponse])
def get_all_expenses(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    category: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Retrieve all expenditures. Accessible by all authenticated users."""
    query = db.query(models.Expense)
    if category:
        query = query.filter(models.Expense.category == category)
        
    expenses_list = query.order_by(models.Expense.expense_date.desc()).all()
    return [_expense_to_response(e) for e in expenses_list]


@router.get("/summary")
def get_expenses_summary(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Fetch expense totals and categories summary breakdown."""
    expenses = db.query(models.Expense).all()
    
    total = 0.0
    by_category = {}
    
    for exp in expenses:
        amt = float(exp.amount or 0.0)
        total += amt
        cat = exp.category or "Other"
        by_category[cat] = by_category.get(cat, 0.0) + amt
        
    category_summary = [{"category": k, "amount": v} for k, v in by_category.items()]
    
    return {
        "total_amount": total,
        "by_category": category_summary
    }


@router.get("/{expense_id}", response_model=schemas.ExpenseResponse)
def get_expense(
    expense_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Retrieve details of a single expense."""
    try:
        eid = int(expense_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expense ID format")
        
    exp = db.query(models.Expense).filter(models.Expense.id == eid).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    return _expense_to_response(exp)


@router.put("/{expense_id}", response_model=schemas.ExpenseResponse)
def update_expense(
    expense_id: str,
    expense: schemas.ExpenseCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Edit an expenditure record. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to edit expenses")
        
    try:
        eid = int(expense_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expense ID format")
        
    existing = db.query(models.Expense).filter(models.Expense.id == eid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    existing.title = expense.title
    existing.amount = expense.amount
    existing.category = expense.category
    existing.expense_date = expense.expense_date
    existing.description = expense.description
    
    db.commit()
    db.refresh(existing)
    return _expense_to_response(existing)


@router.delete("/{expense_id}", status_code=status.HTTP_200_OK)
def delete_expense(
    expense_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db)
):
    """Remove an expenditure record. Only Administrators are allowed."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete expenses")
        
    try:
        eid = int(expense_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expense ID format")
        
    exp = db.query(models.Expense).filter(models.Expense.id == eid).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(exp)
    db.commit()
    return {"message": "Expense deleted successfully"}
