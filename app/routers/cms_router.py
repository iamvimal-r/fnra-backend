from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from app import auth, database, models
from pydantic import BaseModel
from datetime import datetime
import os, uuid, shutil

router = APIRouter(prefix="/cms", tags=["CMS"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"}

# ── Image Upload ──────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Annotated[models.User, Depends(auth.get_current_user)] = None,
):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}. Use JPEG, PNG, WebP, or GIF.")
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(UPLOAD_DIR, filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"url": f"/static/uploads/{filename}", "filename": filename}

# ── Schemas ───────────────────────────────────────────────────────────────────

class SlideSchema(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image_url: str
    link: Optional[str] = None
    order: int = 0
    active: bool = True

class SlideResponse(SlideSchema):
    id: str

class NewsItem(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    category: str = "general"   # general | event | notice | urgent
    published: bool = True
    date: Optional[str] = None  # ISO string

class NewsResponse(NewsItem):
    id: str
    created_at: str

class GalleryItem(BaseModel):
    title: str
    image_url: str
    category: str = "general"   # general | event | facility | maintenance
    order: int = 0

class GalleryResponse(GalleryItem):
    id: str
    created_at: str

# ── Slides ────────────────────────────────────────────────────────────────────

@router.get("/slides", response_model=list[SlideResponse])
def list_slides(db: Session = Depends(database.get_db)):
    slides = db.query(models.Slide).order_by(models.Slide.order.asc()).all()
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "subtitle": s.subtitle,
            "image_url": s.image_url,
            "link": s.link,
            "order": s.order,
            "active": s.active,
        }
        for s in slides
    ]

@router.post("/slides", response_model=SlideResponse, status_code=201)
def create_slide(data: SlideSchema, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    slide = models.Slide(
        title=data.title,
        subtitle=data.subtitle,
        image_url=data.image_url,
        link=data.link,
        order=data.order,
        active=data.active,
    )
    db.add(slide)
    db.commit()
    db.refresh(slide)
    return {
        "id": str(slide.id),
        "title": slide.title,
        "subtitle": slide.subtitle,
        "image_url": slide.image_url,
        "link": slide.link,
        "order": slide.order,
        "active": slide.active,
    }

@router.put("/slides/{sid}", response_model=SlideResponse)
def update_slide(sid: str, data: SlideSchema, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(sid)
    except Exception:
        raise HTTPException(400, "Invalid slide ID")
    slide = db.query(models.Slide).filter(models.Slide.id == oid).first()
    if not slide:
        raise HTTPException(404, "Slide not found")
    slide.title = data.title
    slide.subtitle = data.subtitle
    slide.image_url = data.image_url
    slide.link = data.link
    slide.order = data.order
    slide.active = data.active
    db.commit()
    db.refresh(slide)
    return {
        "id": str(slide.id),
        "title": slide.title,
        "subtitle": slide.subtitle,
        "image_url": slide.image_url,
        "link": slide.link,
        "order": slide.order,
        "active": slide.active,
    }

@router.delete("/slides/{sid}", status_code=200)
def delete_slide(sid: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(sid)
    except Exception:
        raise HTTPException(400, "Invalid slide ID")
    slide = db.query(models.Slide).filter(models.Slide.id == oid).first()
    if not slide:
        raise HTTPException(404, "Slide not found")
    db.delete(slide)
    db.commit()
    return {"message": "Deleted"}

# ── News ──────────────────────────────────────────────────────────────────────

@router.get("/news", response_model=list[NewsResponse])
def list_news(db: Session = Depends(database.get_db)):
    news_items = db.query(models.News).order_by(models.News.created_at.desc()).all()
    return [
        {
            "id": str(n.id),
            "title": n.title,
            "content": n.content,
            "image_url": n.image_url,
            "category": n.category,
            "published": n.published,
            "date": n.date,
            "created_at": n.created_at.isoformat() if n.created_at else datetime.utcnow().isoformat(),
        }
        for n in news_items
    ]

@router.post("/news", response_model=NewsResponse, status_code=201)
def create_news(data: NewsItem, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    news = models.News(
        title=data.title,
        content=data.content,
        image_url=data.image_url,
        category=data.category,
        published=data.published,
        date=data.date,
        created_at=datetime.utcnow(),
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return {
        "id": str(news.id),
        "title": news.title,
        "content": news.content,
        "image_url": news.image_url,
        "category": news.category,
        "published": news.published,
        "date": news.date,
        "created_at": news.created_at.isoformat(),
    }

@router.put("/news/{nid}", response_model=NewsResponse)
def update_news(nid: str, data: NewsItem, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(nid)
    except ValueError:
        raise HTTPException(404, "News not found")
    news = db.query(models.News).filter(models.News.id == oid).first()
    if not news:
        raise HTTPException(404, "News not found")
    news.title = data.title
    news.content = data.content
    news.image_url = data.image_url
    news.category = data.category
    news.published = data.published
    news.date = data.date
    db.commit()
    db.refresh(news)
    return {
        "id": str(news.id),
        "title": news.title,
        "content": news.content,
        "image_url": news.image_url,
        "category": news.category,
        "published": news.published,
        "date": news.date,
        "created_at": news.created_at.isoformat() if news.created_at else datetime.utcnow().isoformat(),
    }

@router.delete("/news/{nid}", status_code=200)
def delete_news(nid: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(nid)
    except Exception:
        raise HTTPException(400, "Invalid news ID")
    news = db.query(models.News).filter(models.News.id == oid).first()
    if not news:
        raise HTTPException(404, "News not found")
    db.delete(news)
    db.commit()
    return {"message": "Deleted"}

# ── Gallery ───────────────────────────────────────────────────────────────────

@router.get("/gallery", response_model=list[GalleryResponse])
def list_gallery(db: Session = Depends(database.get_db)):
    gallery_items = db.query(models.Gallery).order_by(models.Gallery.order.asc()).all()
    return [
        {
            "id": str(g.id),
            "title": g.title,
            "image_url": g.image_url,
            "category": g.category,
            "order": g.order,
            "created_at": g.created_at.isoformat() if g.created_at else datetime.utcnow().isoformat(),
        }
        for g in gallery_items
    ]

@router.post("/gallery", response_model=GalleryResponse, status_code=201)
def create_gallery(data: GalleryItem, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    item = models.Gallery(
        title=data.title,
        image_url=data.image_url,
        category=data.category,
        order=data.order,
        created_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "id": str(item.id),
        "title": item.title,
        "image_url": item.image_url,
        "category": item.category,
        "order": item.order,
        "created_at": item.created_at.isoformat(),
    }

@router.put("/gallery/{gid}", response_model=GalleryResponse)
def update_gallery(gid: str, data: GalleryItem, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(gid)
    except ValueError:
        raise HTTPException(404, "Gallery item not found")
    item = db.query(models.Gallery).filter(models.Gallery.id == oid).first()
    if not item:
        raise HTTPException(404, "Gallery item not found")
    item.title = data.title
    item.image_url = data.image_url
    item.category = data.category
    item.order = data.order
    db.commit()
    db.refresh(item)
    return {
        "id": str(item.id),
        "title": item.title,
        "image_url": item.image_url,
        "category": item.category,
        "order": item.order,
        "created_at": item.created_at.isoformat() if item.created_at else datetime.utcnow().isoformat(),
    }

@router.delete("/gallery/{gid}", status_code=200)
def delete_gallery(gid: str, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    try:
        oid = int(gid)
    except Exception:
        raise HTTPException(400, "Invalid gallery ID")
    item = db.query(models.Gallery).filter(models.Gallery.id == oid).first()
    if not item:
        raise HTTPException(404, "Gallery item not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
