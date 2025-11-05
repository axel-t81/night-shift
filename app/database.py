import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Logic to handle database connections for both local dev and Cloud Run
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")  # This will be a path in Cloud Run

DATABASE_URL = None

# If the DB_HOST is a path (i.e., we are in Cloud Run), format the URL
# for a Unix socket connection.
if db_host and db_host.startswith("/cloudsql"):
    DATABASE_URL = (
        f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
        f"?host={db_host}"
    )
else:
    # Otherwise, for local development, use the full DATABASE_URL from the .env file
    # or fall back to SQLite if it's not set.
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./night_shift.db")

# Use connect_args for SQLite, but not for PostgreSQL
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

