from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app import schemas, database, models
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

# --- Visitors ---
@router.post("/visitors", response_model=schemas.VisitorResponse)
def create_visitor(visitor: schemas.VisitorCreate, db: Session = Depends(database.get_db)):
    v = models.Visitor(
        name=visitor.name,
        phone=visitor.phone,
        house_number=visitor.house_number,
        purpose=visitor.purpose,
        entry_time=datetime.utcnow(),
        status="Entered",
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return {
        "_id": str(v.id),
        "name": v.name,
        "phone": v.phone,
        "house_number": v.house_number,
        "purpose": v.purpose,
        "entry_time": v.entry_time,
        "exit_time": v.exit_time,
        "status": v.status,
    }

@router.get("/visitors", response_model=List[schemas.VisitorResponse])
def list_visitors(db: Session = Depends(database.get_db)):
    visitors = db.query(models.Visitor).all()
    return [
        {
            "_id": str(v.id),
            "name": v.name,
            "phone": v.phone,
            "house_number": v.house_number,
            "purpose": v.purpose,
            "entry_time": v.entry_time,
            "exit_time": v.exit_time,
            "status": v.status,
        }
        for v in visitors
    ]

@router.delete("/visitors/{id}")
def delete_visitor(id: str, db: Session = Depends(database.get_db)):
    try:
        vid = int(id)
    except ValueError:
        return {"message": "Deleted"}
    v = db.query(models.Visitor).filter(models.Visitor.id == vid).first()
    if v:
        db.delete(v)
        db.commit()
    return {"message": "Deleted"}

# --- MOM ---
@router.post("/mom", response_model=schemas.MOMResponse)
def create_mom(mom: schemas.MOMCreate, db: Session = Depends(database.get_db)):
    m = models.MOM(
        title=mom.title,
        content=mom.content,
        meeting_date=mom.meeting_date,
        created_at=datetime.utcnow(),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {
        "_id": str(m.id),
        "title": m.title,
        "content": m.content,
        "meeting_date": m.meeting_date,
        "created_at": m.created_at,
    }

@router.get("/mom", response_model=List[schemas.MOMResponse])
def list_mom(db: Session = Depends(database.get_db)):
    moms = db.query(models.MOM).order_by(models.MOM.meeting_date.desc()).all()
    return [
        {
            "_id": str(m.id),
            "title": m.title,
            "content": m.content,
            "meeting_date": m.meeting_date,
            "created_at": m.created_at,
        }
        for m in moms
    ]

@router.delete("/mom/{id}")
def delete_mom(id: str, db: Session = Depends(database.get_db)):
    try:
        mid = int(id)
    except ValueError:
        return {"message": "Deleted"}
    m = db.query(models.MOM).filter(models.MOM.id == mid).first()
    if m:
        db.delete(m)
        db.commit()
    return {"message": "Deleted"}

# --- Amenities ---
@router.post("/amenities", response_model=schemas.AmenityResponse)
def create_amenity(amenity: schemas.AmenityCreate, db: Session = Depends(database.get_db)):
    a = models.Amenity(
        name=amenity.name,
        description=amenity.description,
        location=amenity.location,
        is_available=True,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {
        "_id": str(a.id),
        "name": a.name,
        "description": a.description,
        "location": a.location,
        "is_available": a.is_available,
    }

@router.get("/amenities", response_model=List[schemas.AmenityResponse])
def list_amenities(db: Session = Depends(database.get_db)):
    amenities = db.query(models.Amenity).all()
    return [
        {
            "_id": str(a.id),
            "name": a.name,
            "description": a.description,
            "location": a.location,
            "is_available": a.is_available,
        }
        for a in amenities
    ]

@router.put("/amenities/{id}/toggle")
def toggle_amenity(id: str, db: Session = Depends(database.get_db)):
    try:
        aid = int(id)
    except ValueError:
        raise HTTPException(404, "Amenity not found")
    item = db.query(models.Amenity).filter(models.Amenity.id == aid).first()
    if not item:
        raise HTTPException(404, "Amenity not found")
    item.is_available = not item.is_available
    db.commit()
    return {"message": "Status updated"}

# --- Staff ---
@router.post("/staff", response_model=schemas.StaffResponse)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(database.get_db)):
    s = models.Staff(
        name=staff.name,
        role=staff.role,
        phone=staff.phone,
        shift=staff.shift,
        status="Active",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {
        "_id": str(s.id),
        "name": s.name,
        "role": s.role,
        "phone": s.phone,
        "shift": s.shift,
        "status": s.status,
    }

@router.get("/staff", response_model=List[schemas.StaffResponse])
def list_staff(db: Session = Depends(database.get_db)):
    staff_members = db.query(models.Staff).all()
    return [
        {
            "_id": str(s.id),
            "name": s.name,
            "role": s.role,
            "phone": s.phone,
            "shift": s.shift,
            "status": s.status,
        }
        for s in staff_members
    ]

@router.delete("/staff/{id}")
def delete_staff(id: str, db: Session = Depends(database.get_db)):
    try:
        sid = int(id)
    except ValueError:
        return {"message": "Deleted"}
    s = db.query(models.Staff).filter(models.Staff.id == sid).first()
    if s:
        db.delete(s)
        db.commit()
    return {"message": "Deleted"}
