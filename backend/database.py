import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ─────────────────────────────────────────────────────────────────────────────
# Environment Setup
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ─────────────────────────────────────────────────────────────────────────────
# Database URL Resolution
#
# Priority order:
#   1. DATABASE_URL environment variable (cloud persistent volume or custom path)
#   2. Local fallback: SQLite file next to this module (backend/portfolio.db)
#
# Cloud examples:
#   Render  persistent disk → DATABASE_URL=sqlite:////data/portfolio.db
#   Railway volume mount    → DATABASE_URL=sqlite:////mnt/data/portfolio.db
#   FastAPI Cloud           → DATABASE_URL=sqlite:////data/portfolio.db
#
# Local development (default):
#   DATABASE_URL=sqlite:///./portfolio.db
# ─────────────────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portfolio.db")

# Resolve relative SQLite paths (sqlite:///./...) against BASE_DIR so the
# .db file always lands in the backend directory regardless of the working
# directory the server is launched from.
if DATABASE_URL.startswith("sqlite:///./") or DATABASE_URL.startswith("sqlite:///.\\"):
    relative_path = DATABASE_URL[len("sqlite:///./"):]
    abs_path = os.path.join(BASE_DIR, relative_path)
    DATABASE_URL = f"sqlite:///{abs_path}"

# ─────────────────────────────────────────────────────────────────────────────
# SQLite Engine
#
# Notes:
#   - check_same_thread=False is required when FastAPI's async handlers share
#     a single SQLite connection across threads.
#   - pool_pre_ping is kept for safety; it is a no-op for SQLite but harmless.
#   - MySQL-only kwargs (pool_size, max_overflow, pool_recycle) are intentionally
#     omitted — they are unsupported by the SQLite dialect and will raise errors.
# ─────────────────────────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base shared by all models
Base = declarative_base()


# ─────────────────────────────────────────────────────────────────────────────
# Connection Health Check
# ─────────────────────────────────────────────────────────────────────────────
def verify_db_connection() -> bool:
    """Verify the SQLite database file is accessible and the engine responds."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        # Log just the file path portion for readability
        db_path = DATABASE_URL.replace("sqlite:///", "")
        print(f"[DATABASE] Connected successfully to SQLite: {db_path}")
        return True
    except Exception as e:
        print(f"[DATABASE ERROR] SQLite connection failed ({DATABASE_URL}): {e}")
        return False


# Backward-compatibility alias (used in init_db.py / main.py)
check_db_connection = verify_db_connection


# ─────────────────────────────────────────────────────────────────────────────
# Session Dependency (FastAPI / dependency injection)
# ─────────────────────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a database session.

    Guarantees:
    - Commits on clean exit
    - Rolls back on any exception
    - Always closes the session in the finally block
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()