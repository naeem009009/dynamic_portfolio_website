from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from database import get_db
from models import ProjectModel, User
from schemas import ProjectCreate, Project
from routers.auth import get_current_user
from seed_database import seed_database

logger = logging.getLogger("projects_router")

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/", response_model=List[Project])
async def get_projects(db: Session = Depends(get_db)):
    try:
        projects = db.query(ProjectModel).all()
        if not projects:
            logger.info("[DEBUG] No projects found in database. Running auto-seeding fallback...")
            print("[DEBUG] No projects found in database. Running auto-seeding fallback...")
            seed_database()
            projects = db.query(ProjectModel).all()
        return projects
    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = project.model_dump() if hasattr(project, "model_dump") else project.dict()
        new_project = ProjectModel(**data)
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        return new_project
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        data = project.model_dump() if hasattr(project, "model_dump") else project.dict()
        for key, value in data.items():
            setattr(db_project, key, value)

        db.commit()
        db.refresh(db_project)
        return db_project
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(db_project)
        db.commit()
        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
