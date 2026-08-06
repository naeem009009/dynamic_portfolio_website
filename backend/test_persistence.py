import sys
import os

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from database import SessionLocal, verify_db_connection, engine, Base
from models import ProjectModel

def run_persistence_test():
    print("=" * 60)
    print("   MySQL Absolute Data Persistence Test Script")
    print("=" * 60)

    # 1. Health check MySQL connection
    print("\n1. Verifying MySQL database connection...")
    if not verify_db_connection():
        print("[FAIL] MySQL connection could not be established!")
        sys.exit(1)

    # Ensure schema exists
    Base.metadata.create_all(bind=engine)

    # 2. Test INSERT Operation
    print("\n2. Executing INSERT test into 'projects' table...")
    session_1 = SessionLocal()
    test_project = ProjectModel(
        title="MySQL Persistence Test Project",
        description="Testing permanent CRUD operations to MySQL disk storage",
        features="INSERT, UPDATE, SELECT, DELETE verification",
        tech_stack="FastAPI, PyMySQL, SQLAlchemy",
        image_url="/images/test-persistence.svg"
    )
    session_1.add(test_project)
    session_1.commit()
    session_1.refresh(test_project)
    created_id = test_project.id
    print(f"   [OK] Successfully inserted record with ID: {created_id}")
    session_1.close()

    # 3. Test UPDATE Operation
    print("\n3. Executing UPDATE test on record ID:", created_id)
    session_2 = SessionLocal()
    fetched_project = session_2.query(ProjectModel).filter(ProjectModel.id == created_id).first()
    assert fetched_project is not None, f"Record with ID {created_id} not found!"
    
    updated_title = "MySQL Persistence Test Project (UPDATED)"
    fetched_project.title = updated_title
    session_2.commit()
    print(f"   [OK] Successfully updated title to: '{updated_title}'")
    session_2.close()

    # 4. Test SELECT Verification across fresh independent Session
    print("\n4. Executing SELECT test across NEW session lifecycle...")
    session_3 = SessionLocal()
    persisted_project = session_3.query(ProjectModel).filter(ProjectModel.id == created_id).first()
    assert persisted_project is not None, "Failed to retrieve project from disk storage!"
    assert persisted_project.title == updated_title, f"Expected '{updated_title}', got '{persisted_project.title}'"
    print(f"   [OK] Verified permanent disk persistence! Record ID {created_id} has title: '{persisted_project.title}'")

    # 5. Cleanup Test Record
    print("\n5. Cleaning up test record...")
    session_3.delete(persisted_project)
    session_3.commit()
    session_3.close()
    print(f"   [OK] Test record ID {created_id} cleaned up.")

    print("\n" + "=" * 60)
    print("[SUCCESS] MySQL Absolute Data Persistence Verified 100%!")
    print("=" * 60)

if __name__ == "__main__":
    run_persistence_test()
