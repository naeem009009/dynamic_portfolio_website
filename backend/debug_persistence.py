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

def run_debug_persistence_test():
    print("=" * 70)
    print("   STANDALONE MYSQL PERSISTENCE DEBUG UTILITY (Laragon MySQL)")
    print("=" * 70)

    # 1. Health check & log MySQL connection target
    print("\n[STEP 1] Verifying active MySQL database connection target...")
    if not verify_db_connection():
        print("[FAIL] Could not connect to Laragon MySQL database!")
        sys.exit(1)

    # Ensure metadata tables are created on target MySQL
    Base.metadata.create_all(bind=engine)

    # 2. STEP 1: Insert dummy record via Session 1 and commit
    print("\n[STEP 2] Inserting dummy test record into MySQL via Session 1...")
    session_1 = SessionLocal()
    dummy_project = ProjectModel(
        title="[DEBUG_PERSISTENCE_TEST_RECORD]",
        description="Testing permanent CRUD persistence on Laragon MySQL disk storage",
        features="Insert -> Close Session -> New Session Query -> Delete",
        tech_stack="FastAPI, PyMySQL, SQLAlchemy",
        image_url="/images/debug-persistence.svg"
    )
    session_1.add(dummy_project)
    session_1.commit()
    session_1.refresh(dummy_project)
    created_id = dummy_project.id
    print(f"   -> Successfully inserted dummy project with ID: {created_id}")

    # 3. STEP 2: Close DB session completely
    print("\n[STEP 3] Closing Session 1 completely (destroying in-memory reference)...")
    session_1.close()
    print("   -> Session 1 closed successfully.")

    # 4. STEP 3: Open NEW independent Session 2 and query MySQL disk
    print("\n[STEP 4] Opening NEW independent Session 2 & querying record from MySQL disk...")
    session_2 = SessionLocal()
    queried_project = session_2.query(ProjectModel).filter(ProjectModel.id == created_id).first()

    if queried_project is None:
        print(f"[ERROR] Persistence verification failed! Record ID {created_id} was NOT found on MySQL disk!")
        session_2.close()
        sys.exit(1)

    print(f"   -> [VERIFIED] Found record on MySQL disk!")
    print(f"      ID: {queried_project.id}")
    print(f"      Title: '{queried_project.title}'")
    print(f"      Tech Stack: '{queried_project.tech_stack}'")

    # 5. STEP 4: Delete dummy record via Session 2 and commit
    print("\n[STEP 5] Deleting dummy test record via Session 2 & committing changes...")
    session_2.delete(queried_project)
    session_2.commit()
    session_2.close()
    print(f"   -> [CLEANUP] Dummy record ID {created_id} deleted and session closed.")

    # 6. Verification: Ensure deleted record is no longer in MySQL
    session_3 = SessionLocal()
    check_deleted = session_3.query(ProjectModel).filter(ProjectModel.id == created_id).first()
    session_3.close()
    
    if check_deleted is not None:
        print(f"[ERROR] Deletion failed! Record ID {created_id} still exists on MySQL disk.")
        sys.exit(1)

    print("   -> [VERIFIED] Record confirmed permanently deleted from MySQL disk.")

    print("\n" + "=" * 70)
    print("   [SUCCESS] MYSQL DATA PERSISTENCE VERIFIED 100% ON DISK!")
    print("=" * 70)

if __name__ == "__main__":
    run_debug_persistence_test()
