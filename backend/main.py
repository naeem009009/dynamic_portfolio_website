from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from routers import auth, projects, skills, services, messages
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio API",
    description="Backend API for Portfolio Website with Admin Panel",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(services.router)
app.include_router(messages.router)

@app.get("/")
async def root():
    frontend_index = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "Portfolio API is running", "docs": "/docs"}

@app.get("/admin")
@app.get("/admin/")
@app.get("/admin-panel")
async def admin_panel():
    admin_dashboard = os.path.join(os.path.dirname(__file__), "..", "frontend", "admin", "dashboard.html")
    if os.path.exists(admin_dashboard):
        return FileResponse(admin_dashboard)
    return {"message": "Admin Panel file not found"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount static files for frontend and admin
# /admin must come before /frontend so it isn't shadowed by the broader mount
app.mount("/admin", StaticFiles(directory="../frontend/admin"), name="admin")
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")
