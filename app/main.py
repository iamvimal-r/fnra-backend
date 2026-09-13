import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from app.routers import (
    auth_router,
    notices_router,
    complaints_router,
    billing_router,
    house_router,
    expenses_router,
    incomes_router,
    management_router,
    contacts_router,
    cms_router,
    committee_router,
)
from app.database import engine, Base, SessionLocal
from app import models

# Create all MySQL tables automatically if they do not exist
Base.metadata.create_all(bind=engine)

# Ensure uploads directory exists
os.makedirs("static/profile_images", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Residance API",
    description="FastAPI + MySQL backend for the Residance Association App",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    try:
        from datetime import datetime
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE slides ADD COLUMN tag VARCHAR(100) NULL;"))
                conn.commit()
            except Exception:
                pass
        db = SessionLocal()
        try:
            if db.query(models.Income).count() == 0:
                mock_incomes = [
                    models.Income(
                        title="Community Hall Rental",
                        amount=5000.0,
                        category="Rentals",
                        income_date="2026-05-05",
                        description="Rental charges for block C family gathering.",
                        created_by="system",
                        created_at=datetime.utcnow()
                    ),
                    models.Income(
                        title="Donation for Sports Day",
                        amount=10000.0,
                        category="Donations",
                        income_date="2026-05-12",
                        description="Special donation received from resident in Block A.",
                        created_by="system",
                        created_at=datetime.utcnow()
                    ),
                    models.Income(
                        title="Advertisement Banner Space",
                        amount=3500.0,
                        category="Advertising",
                        income_date="2026-05-15",
                        description="Monthly rent for advertising banner at main entrance gate.",
                        created_by="system",
                        created_at=datetime.utcnow()
                    ),
                    models.Income(
                        title="Interest Credit on FD",
                        amount=4200.0,
                        category="Interest",
                        income_date="2026-05-20",
                        description="Interest received from Fixed Deposit in SBI bank account.",
                        created_by="system",
                        created_at=datetime.utcnow()
                    )
                ]
                db.add_all(mock_incomes)
                db.commit()
                logger.info("Startup DB Migration: Seeded mock other incomes.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed startup migrations: {e}")


# ── CORS ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global error handler ──────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)},
    )

# ── Routers ───────────────────────────────────
app.include_router(auth_router.router)
app.include_router(notices_router.router)
app.include_router(complaints_router.router)
app.include_router(billing_router.router)
app.include_router(house_router.router)
app.include_router(expenses_router.router)
app.include_router(incomes_router.router)
app.include_router(management_router.router)
app.include_router(contacts_router.router)
app.include_router(cms_router.router)
app.include_router(committee_router.router)

# ── Health / utility ──────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "Residance API v2 (MySQL) is running 🚀"}

@app.get("/health", tags=["Health"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}
