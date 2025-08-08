from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = None
SessionLocal = None

# Only initialize SQLAlchemy engine if we are NOT using D1
if not settings.USE_D1:
    # The connection URI should be constructed from the postgres settings
    SQLALCHEMY_DATABASE_URI = settings.get_postgres_uri()
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # If using D1, SessionLocal will be None, and this dependency should
    # likely not be used. The API endpoint should use a D1-specific dependency.
    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 