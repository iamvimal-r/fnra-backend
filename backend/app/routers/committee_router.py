from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app import auth, database, models
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/committee", tags=["Committee"])

# ── Schema ────────────────────────────────────────────────────────────────────

VALID_ROLES = [
    "President",
    "Vice President",
    "Secretary",
    "Joint Secretary",
    "Treasurer",
    "Executive Member",
]

class CommitteeMemberSchema(BaseModel):
    name: str
    role: str                       # from VALID_ROLES
    photo_url: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    bio: Optional[str] = ""
    order: int = 99
    published: bool = True

class CommitteeMemberResponse(CommitteeMemberSchema):
    id: str
    created_at: str

def _fmt(m: models.CommitteeMember) -> dict:
    return {
        "id": str(m.id),
        "name": m.name,
        "role": m.designation,
        "photo_url": m.photo_url or "",
        "phone": m.phone or "",
        "email": m.email or "",
        "bio": m.bio or "",
        "order": m.order if m.order is not None else 99,
        "published": m.published if m.published is not None else True,
        "created_at": m.created_at.isoformat() if m.created_at else datetime.utcnow().isoformat(),
    }

# ── Public GET ────────────────────────────────────────────────────────────────

@router.get("", response_model=list[CommitteeMemberResponse])
def list_members(db: Session = Depends(database.get_db)):
    """Public — no auth needed."""
    members = db.query(models.CommitteeMember).filter(models.CommitteeMember.published == True).order_by(models.CommitteeMember.order.asc()).all()
    return [_fmt(m) for m in members]

@router.get("/all", response_model=list[CommitteeMemberResponse])
def list_all_members(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Admin — returns all including unpublished."""
    members = db.query(models.CommitteeMember).order_by(models.CommitteeMember.order.asc()).all()
    return [_fmt(m) for m in members]

# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("", response_model=CommitteeMemberResponse, status_code=201)
def create_member(
    data: CommitteeMemberSchema,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    member = models.CommitteeMember(
        name=data.name,
        designation=data.role,
        photo_url=data.photo_url,
        phone=data.phone,
        email=data.email,
        bio=data.bio,
        order=data.order,
        published=data.published,
        created_at=datetime.utcnow(),
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return _fmt(member)

@router.put("/{mid}", response_model=CommitteeMemberResponse)
def update_member(
    mid: str,
    data: CommitteeMemberSchema,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        oid = int(mid)
    except ValueError:
        raise HTTPException(404, "Member not found")
    member = db.query(models.CommitteeMember).filter(models.CommitteeMember.id == oid).first()
    if not member:
        raise HTTPException(404, "Member not found")
    
    member.name = data.name
    member.designation = data.role
    member.photo_url = data.photo_url
    member.phone = data.phone
    member.email = data.email
    member.bio = data.bio
    member.order = data.order
    member.published = data.published
    db.commit()
    db.refresh(member)
    return _fmt(member)

@router.delete("/{mid}", status_code=200)
def delete_member(
    mid: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    try:
        oid = int(mid)
    except ValueError:
        raise HTTPException(404, "Member not found")
    member = db.query(models.CommitteeMember).filter(models.CommitteeMember.id == oid).first()
    if not member:
        raise HTTPException(404, "Member not found")
    db.delete(member)
    db.commit()
    return {"message": "Deleted"}
