from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from app import auth, database, models
from pydantic import BaseModel

router = APIRouter(prefix="/contacts", tags=["Contacts"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name: str
    phone: str
    category: str          # electrician | plumber | security | maintenance | authority | emergency
    notes: Optional[str] = None
    address: Optional[str] = None
    availability: Optional[str] = None
    whatsapp: Optional[bool] = True

class ContactResponse(ContactCreate):
    id: str

def _fmt(c: models.Contact) -> dict:
    return {
        "id": str(c.id),
        "name": c.name,
        "phone": c.phone,
        "category": c.category,
        "notes": c.description,
        "address": None,
        "availability": None,
        "whatsapp": True,
    }

# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ContactResponse])
def list_contacts(
    category: Optional[str] = Query(None, description="Filter by category (e.g. emergency)"),
    db: Session = Depends(database.get_db),
):
    """Public endpoint — no auth required. Optionally filter by category."""
    query = db.query(models.Contact)
    if category:
        query = query.filter(models.Contact.category == category)
    contacts = query.order_by(models.Contact.category.asc()).all()
    return [_fmt(c) for c in contacts]


@router.post("", response_model=ContactResponse, status_code=201)
def create_contact(
    data: ContactCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    contact = models.Contact(
        name=data.name,
        phone=data.phone,
        category=data.category,
        description=data.notes,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return _fmt(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: str,
    data: ContactCreate,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        cid = int(contact_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Contact not found")

    existing = db.query(models.Contact).filter(models.Contact.id == cid).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Contact not found")

    existing.name = data.name
    existing.phone = data.phone
    existing.category = data.category
    existing.description = data.notes
    
    db.commit()
    db.refresh(existing)
    return _fmt(existing)


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: str,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    try:
        cid = int(contact_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact = db.query(models.Contact).filter(models.Contact.id == cid).first()
    if contact:
        db.delete(contact)
        db.commit()
    return {"message": "Contact deleted"}
