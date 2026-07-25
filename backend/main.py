import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import engine, Base
from routers import auth, projects, skills, services, messages
from seed_database import seed_database

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    # Seed initial database data if empty
    try:
        seed_database()
    except Exception as e:
        print(f"[STARTUP WARN] Error during startup seeding: {e}")
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Portfolio API",
    description="Backend API for Portfolio Website with Admin Panel & JWT Security",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

# Parse CORS Origins from environment
cors_env = os.getenv("CORS_ORIGINS", "")
if cors_env:
    origins = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

# If origins does not include '*', allow credentials.
allow_credentials = "*" not in origins

# Add CORS Middleware supporting Vercel previews and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(skills.router)
app.include_router(services.router)
app.include_router(messages.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Portfolio API is running successfully!",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}