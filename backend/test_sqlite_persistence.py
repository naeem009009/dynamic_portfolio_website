"""
test_sqlite_persistence.py
──────────────────────────
Standalone SQLite disk-persistence verification script.

Performs a complete CRUD lifecycle against an isolated test database file:
  Insert → Close Session → Reopen Session → Verify Read → Delete → Commit

Run directly:
    python test_sqlite_persistence.py

Expected output on success:
    [PASS] All SQLite persistence checks passed.
"""

import os
import sys

# ─── Ensure backend package is importable ────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ─── Isolated test database (cleaned up after the test) ──────────────────────
TEST_DB_PATH = os.path.join(BASE_DIR, "_test_portfolio.db")
TEST_DB_URL  = f"sqlite:///{TEST_DB_PATH}"

# ─── Minimal model for the test ──────────────────────────────────────────────
TestBase   = declarative_base()

class _TestRecord(TestBase):
    """Lightweight table used only during this persistence test."""
    __tablename__ = "persistence_test"
    id    = Column(Integer, primary_key=True, index=True)
    label = Column(String(120), nullable=False)


def _make_engine():
    return create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )


def _make_session(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def run_persistence_test() -> bool:
    """
    Execute the full CRUD lifecycle and return True on success.

    Steps
    -----
    1. Create schema in the test .db file.
    2. INSERT a record and commit.
    3. Close the session AND dispose the engine (simulates process restart /
       cloud container re-attach).
    4. Open a brand-new engine + session to the same file.
    5. READ back the record and assert its value.
    6. DELETE the record and commit.
    7. Assert the table is now empty.
    8. Clean up the test .db file from disk.
    """
    print("=" * 60)
    print("  SQLite Disk Persistence Test")
    print(f"  DB File : {TEST_DB_PATH}")
    print("=" * 60)

    # ── 1. Schema creation ────────────────────────────────────────────────────
    engine = _make_engine()
    TestBase.metadata.create_all(bind=engine)
    print("[STEP 1] Schema created.")

    # ── 2. INSERT ─────────────────────────────────────────────────────────────
    db = _make_session(engine)
    try:
        record = _TestRecord(label="persistence-check-value")
        db.add(record)
        db.commit()
        inserted_id = record.id
        print(f"[STEP 2] Inserted record id={inserted_id}, label='{record.label}'")
    finally:
        db.close()

    # ── 3. Close engine entirely (simulate restart) ───────────────────────────
    engine.dispose()
    print("[STEP 3] Engine disposed. Simulating process restart...")

    # ── 4. Reopen engine + session ────────────────────────────────────────────
    engine2 = _make_engine()
    db2     = _make_session(engine2)
    print("[STEP 4] Reopened fresh engine + session.")

    try:
        # ── 5. READ + VERIFY ──────────────────────────────────────────────────
        fetched = db2.query(_TestRecord).filter_by(id=inserted_id).first()
        assert fetched is not None, (
            f"[FAIL] Record id={inserted_id} not found after engine restart!"
        )
        assert fetched.label == "persistence-check-value", (
            f"[FAIL] Expected 'persistence-check-value', got '{fetched.label}'"
        )
        print(f"[STEP 5] Read-back verified: id={fetched.id}, label='{fetched.label}'")

        # ── 6. DELETE ─────────────────────────────────────────────────────────
        db2.delete(fetched)
        db2.commit()
        print("[STEP 6] Record deleted and committed.")

        # ── 7. Confirm empty ──────────────────────────────────────────────────
        remaining = db2.query(_TestRecord).count()
        assert remaining == 0, (
            f"[FAIL] Expected 0 records after delete, found {remaining}."
        )
        print(f"[STEP 7] Table confirmed empty (count={remaining}).")

    finally:
        db2.close()
        engine2.dispose()

    # ── 8. Disk cleanup ───────────────────────────────────────────────────────
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    # SQLite also creates a -shm and -wal file in WAL mode; clean those too.
    for suffix in ("-shm", "-wal"):
        side_file = TEST_DB_PATH + suffix
        if os.path.exists(side_file):
            os.remove(side_file)
    print(f"[STEP 8] Test database file removed from disk.")

    return True


if __name__ == "__main__":
    try:
        success = run_persistence_test()
        if success:
            print()
            print("=" * 60)
            print("  [PASS] All SQLite persistence checks passed.")
            print("=" * 60)
            sys.exit(0)
    except AssertionError as e:
        print()
        print(f"  {e}")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"  [ERROR] Unexpected error during persistence test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
