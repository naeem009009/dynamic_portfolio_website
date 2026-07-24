from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Allowed CORS Origins
# In production, replace "*" with your exact Vercel URL for better security
origins = [
    "*",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
]

# CORS Middleware (Allows your Vercel frontend to talk to this FastAPI backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

@app.get("/")
async def root():
    return {
        "message": "Portfolio API is running successfully!",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}