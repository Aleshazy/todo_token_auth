from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import DATABASE_URL

# Engine is a global DB connector.
# If using SQLite (local file) we need to set `check_same_thread`.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal creates one DB session per request.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base is parent class for all ORM models.
Base = declarative_base()


# Provide DB session per request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()