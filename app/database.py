import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://root:root@pressclub_db:3306/fnra_db")


def ensure_database_exists(db_url: str):
    if not db_url or "sqlite" in db_url:
        return
    try:
        sync_url = db_url
        if "mysql+asyncmy://" in sync_url:
            sync_url = sync_url.replace("mysql+asyncmy://", "mysql+pymysql://")
        url_obj = make_url(sync_url)
        db_name = url_obj.database
        if db_name:
            server_url = url_obj.set(database="")
            temp_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
            with temp_engine.connect() as conn:
                conn.execute(
                    text(
                        f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                    )
                )
            temp_engine.dispose()
    except Exception:
        pass


ensure_database_exists(DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()