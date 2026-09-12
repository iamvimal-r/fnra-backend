from datetime import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, auth, database, models

router = APIRouter(
    prefix="/notices",
    tags=["notices"]
)

def _notice_to_response(notice: models.Notice) -> dict:
    return {
        "_id": str(notice.id),
        "title": notice.title,
        "content": notice.content,
        "date_posted": notice.date_posted,
        "author_id": str(notice.author_id) if notice.author_id else "",
    }


@router.get("/", response_model=List[schemas.NoticeResponse])
def get_notices(current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Fetch all notices."""
    notices = db.query(models.Notice).order_by(models.Notice.date_posted.desc()).all()
    return [_notice_to_response(n) for n in notices]


@router.post("/", response_model=schemas.NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(notice: schemas.NoticeCreate, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Create a new notice (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to post notices")
    
    new_notice = models.Notice(
        title=notice.title,
        content=notice.content,
        date_posted=datetime.utcnow(),
        author_id=str(current_user.id),
    )
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    return _notice_to_response(new_notice)


@router.delete("/{notice_id}")
def delete_notice(notice_id: str, current_user: Annotated[models.User, Depends(auth.get_current_user)], db: Session = Depends(database.get_db)):
    """Delete a notice (Admin only)."""
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        nid = int(notice_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Notice not found")

    notice = db.query(models.Notice).filter(models.Notice.id == nid).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
        
    db.delete(notice)
    db.commit()
    return {"message": "Notice deleted successfully"}
