import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Logic to handle database connections for both local dev and Cloud Run
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")  # Can be host or Unix socket path
db_port = os.environ.get("DB_PORT", "5432")
instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")
db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")

database_url_env = os.environ.get("DATABASE_URL")
sqlite_fallback = os.environ.get("SQLITE_PATH", "sqlite:///./night_shift.db")

DATABASE_URL = None

# Preference order:
# 1. Full DATABASE_URL (explicit override)
# 2. Cloud SQL Unix socket connection
# 3. Direct TCP Postgres connection
# 4. SQLite fallback (development)
if database_url_env:
    DATABASE_URL = database_url_env
else:
    unix_socket_host = None

    if instance_connection_name:
        unix_socket_host = os.path.join(db_socket_dir, instance_connection_name)

    if db_host and db_host.startswith("/cloudsql"):
        unix_socket_host = db_host

    if unix_socket_host and db_user and db_pass and db_name:
        DATABASE_URL = (
            f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}"
            f"?host={unix_socket_host}"
        )
    elif db_user and db_pass and db_name and db_host:
        DATABASE_URL = (
            f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )
    else:
        DATABASE_URL = sqlite_fallback

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

