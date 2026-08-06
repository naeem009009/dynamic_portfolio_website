import sys
import os

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import engine, Base, verify_db_connection
from seed_database import seed_database

def init_db():
    """Programmatically verify connection, create schema tables, and seed initial data."""
    print("=" * 60)
    print("[INIT] Starting programmatic Database Setup & Verification...")
    print("=" * 60)
    
    # 1. Health check connection
    connected = verify_db_connection()
    if not connected:
        print("[WARN] Proceeding with table setup attempt despite connection warning...")

    # 2. Create tables programmatically
    try:
        print("[INIT] Creating database tables if they do not exist...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Schema tables verified / created successfully.")
    except Exception as e:
        print(f"[ERROR] Error creating database tables: {e}")
        return False

    # 3. Seed initial database data
    try:
        print("[INIT] Seeding initial database data...")
        seed_database()
        print("[OK] Seeding completed.")
    except Exception as e:
        print(f"[ERROR] Error seeding database: {e}")
        return False

    print("=" * 60)
    print("[SUCCESS] Programmatic Database Initialization Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    init_db()
