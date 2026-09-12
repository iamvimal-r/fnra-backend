"""
Auth Router — /auth prefix
Endpoints:
  POST /auth/register   → create account
  POST /auth/login      → get access + refresh tokens
  POST /auth/refresh    → exchange refresh token for new access token
  POST /auth/logout     → (client-side; endpoint just ACKs)
  GET  /auth/me         → current user profile
  PUT  /auth/me         → update own profile
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import shutil
import os

from app import schemas, auth, database, models

router = APIRouter(prefix="/auth", tags=["Auth"])


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _user_to_response(user: models.User) -> dict:
    """Safely convert a User ORM instance to a UserResponse-compatible dict."""
    return {
        "id": str(user.id),
        "name": user.name,
        "username": user.username or user.name,
        "email": user.email,
        "role": user.role,
        "profile_image": user.profile_image,
    }


def _make_tokens(user: models.User) -> dict:
    """Build the Token response payload for a given user."""
    token_data = {"sub": user.email}
    access_token = auth.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = auth.create_refresh_token(data=token_data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": _user_to_response(user),
    }


# ──────────────────────────────────────────────
# Public routes
# ──────────────────────────────────────────────

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserRegister, db: Session = Depends(database.get_db)):
    """Create a new user account and return tokens immediately (auto-login)."""
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    if db.query(models.User).filter(func.lower(models.User.username) == payload.username.strip().lower()).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username already exists.",
        )

    hashed_password = auth.get_password_hash(payload.password)
    new_user = models.User(
        name=payload.name,
        username=payload.username.strip(),
        email=payload.email,
        hashed_password=hashed_password,
        role="resident",
        profile_image=None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return _make_tokens(new_user)


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Authenticate with email + password and receive access + refresh tokens."""
    identifier = payload.email.strip().lower()
    user = db.query(models.User).filter(
        or_(
            func.lower(models.User.email) == identifier,
            func.lower(models.User.username) == identifier,
            func.lower(models.User.name) == identifier
        )
    ).first()

    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )
    return _make_tokens(user)


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(payload: schemas.RefreshRequest, db: Session = Depends(database.get_db)):
    """Exchange a valid refresh token for a new access token (+ new refresh token)."""
    token_payload = auth.decode_refresh_token(payload.refresh_token)
    email = token_payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return _make_tokens(user)


@router.post("/logout")
def logout():
    """
    Stateless logout acknowledgement.
    The client must delete its stored tokens on receipt.
    """
    return {"message": "Logged out successfully."}


# ──────────────────────────────────────────────
# Protected routes
# ──────────────────────────────────────────────

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    """Return the currently authenticated user's profile."""
    return _user_to_response(current_user)


@router.put("/me", response_model=schemas.UserResponse)
def update_me(
    data: dict,
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
):
    """Update own name / profile fields (not password, not role)."""
    if "name" in data:
        current_user.name = str(data["name"]).strip()
    else:
        raise HTTPException(status_code=400, detail="No valid fields provided.")

    db.commit()
    db.refresh(current_user)
    return _user_to_response(current_user)


@router.post("/me/profile-image", response_model=schemas.UserResponse)
async def upload_profile_image(
    current_user: Annotated[models.User, Depends(auth.get_current_user)],
    db: Session = Depends(database.get_db),
    file: UploadFile = File(...),
):
    """Upload a profile image for the current user."""
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images allowed.")

    ext = file.filename.split(".")[-1].lower()
    filename = f"user_{current_user.id}.{ext}"
    save_path = f"static/profile_images/{filename}"
    os.makedirs("static/profile_images", exist_ok=True)

    with open(save_path, "wb+") as f:
        shutil.copyfileobj(file.file, f)

    image_url = f"/static/profile_images/{filename}"
    current_user.profile_image = image_url
    db.commit()
    db.refresh(current_user)
    return _user_to_response(current_user)


# ──────────────────────────────────────────────
# Admin-only routes
# ──────────────────────────────────────────────

@router.get("/users", response_model=list[schemas.UserResponse])
def list_users(
    _admin: Annotated[models.User, Depends(auth.require_admin)],
    db: Session = Depends(database.get_db),
):
    """List all users (admin only)."""
    users = db.query(models.User).all()
    return [_user_to_response(u) for u in users]


@router.post("/users", response_model=schemas.UserResponse, status_code=201)
def admin_create_user(
    payload: schemas.UserCreate,
    _admin: Annotated[models.User, Depends(auth.require_admin)],
    db: Session = Depends(database.get_db),
):
    """Admin creates a user with a specific role."""
    if db.query(models.User).filter(models.User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered.")
    if db.query(models.User).filter(func.lower(models.User.username) == payload.username.strip().lower()).first():
        raise HTTPException(status_code=409, detail="Username already registered.")

    new_user = models.User(
        name=payload.name,
        username=payload.username.strip(),
        email=payload.email,
        hashed_password=auth.get_password_hash(payload.password),
        role=payload.role,
        profile_image=None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return _user_to_response(new_user)


@router.put("/users/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: str,
    data: dict,
    _admin: Annotated[models.User, Depends(auth.require_admin)],
    db: Session = Depends(database.get_db),
):
    """Change a user's role (admin only)."""
    allowed_roles = {"admin", "resident", "security"}
    role = data.get("role", "")
    if role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of: {allowed_roles}")

    try:
        uid = int(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found.")

    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.role = role
    db.commit()
    db.refresh(user)
    return _user_to_response(user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    _admin: Annotated[models.User, Depends(auth.require_admin)],
    db: Session = Depends(database.get_db),
):
    """Delete a user account (admin only)."""
    try:
        uid = int(user_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found.")

    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully."}
