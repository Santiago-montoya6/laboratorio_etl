from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION, MYSQL_URL

# ── MongoDB ──────────────────────────────────────────────
mongo_client     = MongoClient(MONGO_URI)
mongo_db         = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# ── MySQL / SQLAlchemy ────────────────────────────────────
engine       = create_engine(MYSQL_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()