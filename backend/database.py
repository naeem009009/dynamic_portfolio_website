import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Get BASE_DIR (points to backend root directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Extract MySQL environment variables with sensible local development fallbacks
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "portfolio_db")

# Build MySQL connection string fallback
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
DEFAULT_MYSQL_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Resolve DATABASE_URL from environment or fallback to MySQL URL
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_MYSQL_URL)

# Ensure correct SQLAlchemy MySQL dialect prefix
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure MySQL engine with production-ready connection pool settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Automatically reconnect dropped connections
    pool_recycle=3600,   # Recycle connections older than 1 hour
    pool_size=10,        # Maximum steady state pool connections
    max_overflow=20      # Allow temporary connection bursts
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def verify_db_connection() -> bool:
    """Programmatically verify the MySQL database connection at application startup."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(f"[OK] Database connection verified successfully ({DATABASE_URL.split('@')[-1]})")
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

# Backward compatibility alias
check_db_connection = verify_db_connection

# Dependency to get database session with full persistence guarantee
def get_db():
    """Dependency for yielding database session with automated commit and safe teardown."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()