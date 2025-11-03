import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# New database connection logic for Cloud Run and Cloud SQL
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST") # This will be the private IP of the Cloud SQL instance

# The DATABASE_URL will be constructed from environment variables
# Format for PostgreSQL: postgresql://<user>:<password>@<host>/<dbname>
DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}" if db_user else os.getenv("DATABASE_URL", "sqlite:///./night_shift.db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

