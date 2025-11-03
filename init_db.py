"""
Database initialization script
Run this to create all tables in the database
"""
from app.database import engine, Base
from app.models import Category, Block, Task, Quote
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")

if __name__ == "__main__":
    init_database()

