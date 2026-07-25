import sys
import os

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from main import app
from seed_database import seed_database

def run_tests():
    print("==================================================")
    print("   FastAPI Single Admin Auth & Data Flow Test")
    print("==================================================")
    
    # Step 1: Initialize DB & Seed Admin 'muneer'
    print("\n1. Upserting Admin 'muneer' and Seeding Database...")
    seed_database()
    
    client = TestClient(app)
    
    # Step 2: Test Public GET Endpoints
    print("\n2. Testing Public GET Endpoints...")
    res_proj = client.get("/projects/")
    assert res_proj.status_code == 200, f"GET /projects/ failed: {res_proj.text}"
    projects = res_proj.json()
    print(f"   [OK] GET /projects/ returned {len(projects)} projects")
    assert len(projects) > 0, "Projects list is empty after seeding!"

    res_skills = client.get("/skills/")
    assert res_skills.status_code == 200, f"GET /skills/ failed: {res_skills.text}"
    skills = res_skills.json()
    print(f"   [OK] GET /skills/ returned {len(skills)} skills")
    assert len(skills) > 0, "Skills list is empty after seeding!"

    res_services = client.get("/services/")
    assert res_services.status_code == 200, f"GET /services/ failed: {res_services.text}"
    services = res_services.json()
    print(f"   [OK] GET /services/ returned {len(services)} services")
    assert len(services) > 0, "Services list is empty after seeding!"

    # Step 3: Test Login with Single Admin Credentials (muneer / muneer037) via JSON
    print("\n3. Testing Login with 'muneer' / 'muneer037' via JSON payload...")
    res_login_json = client.post(
        "/auth/login",
        json={"username": "muneer", "password": "muneer037"}
    )
    assert res_login_json.status_code == 200, f"JSON Login failed: {res_login_json.text}"
    token_data = res_login_json.json()
    assert "access_token" in token_data, "No access_token returned!"
    token = token_data["access_token"]
    print(f"   [OK] Single Admin JSON Login successful!")

    # Step 4: Test Login with Single Admin Credentials via Form payload (OAuth2 standard)
    print("\n4. Testing Login via Form payload (Swagger UI OAuth2 compatible)...")
    res_login_form = client.post(
        "/auth/login",
        data={"username": "muneer", "password": "muneer037"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res_login_form.status_code == 200, f"Form Login failed: {res_login_form.text}"
    assert "access_token" in res_login_form.json()
    print(f"   [OK] Single Admin Form Login successful!")

    # Step 5: Test /auth/me
    print("\n5. Testing /auth/me with Bearer token...")
    res_me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_me.status_code == 200, f"GET /auth/me failed: {res_me.text}"
    user_info = res_me.json()
    assert user_info["username"] == "muneer"
    print(f"   [OK] Verified admin user: {user_info['username']} ({user_info['email']})")

    # Step 6: Verify Registration is Disabled
    print("\n6. Testing Disabled Public Registration (/auth/register)...")
    res_reg = client.post("/auth/register", json={"username": "hacker", "password": "123"})
    assert res_reg.status_code in [404, 405], f"Registration endpoint should be disabled, got {res_reg.status_code}"
    print(f"   [OK] Public registration endpoint is disabled (404/405)")

    # Step 7: Test Protected Routes
    print("\n7. Testing Protected Write Operations (POST & DELETE /projects/)...")
    res_unauth = client.post("/projects/", json={"title": "Test", "description": "X", "features": "Y", "tech_stack": "Z"})
    assert res_unauth.status_code == 401
    print(f"   [OK] Unauthenticated write correctly rejected (401)")

    res_create = client.post(
        "/projects/",
        json={
            "title": "Admin Project Test",
            "description": "Created by admin muneer",
            "features": "Single Admin",
            "tech_stack": "FastAPI, Python",
            "image_url": ""
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_create.status_code == 201
    project_id = res_create.json()["id"]

    res_delete = client.delete(
        f"/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_delete.status_code == 200
    print(f"   [OK] Authenticated write operations fully working!")

    print("\n==================================================")
    print("   SINGLE ADMIN AUTH TESTS PASSED! (100% Verified)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
