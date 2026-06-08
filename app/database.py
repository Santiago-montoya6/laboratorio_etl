from pymongo import MongoClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION, MYSQL_URL, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
import mysql.connector

# ── MongoDB ──────────────────────────────────────────────
mongo_client     = MongoClient(MONGO_URI)
mongo_db         = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# ── MySQL / SQLAlchemy ────────────────────────────────────
engine       = create_engine(MYSQL_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()

def create_database():
    """Crea la base de datos si no existe."""
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Base de datos '{MYSQL_DB}' lista")
    except Exception as e:
        print(f"❌ Error creando BD: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
