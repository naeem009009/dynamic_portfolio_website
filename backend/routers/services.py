from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from database import get_db
from models import ServiceModel, User
from schemas import ServiceCreate, Service
from routers.auth import get_current_user
from seed_database import seed_database

logger = logging.getLogger("services_router")

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("/", response_model=List[Service])
async def get_services(db: Session = Depends(get_db)):
    try:
        services = db.query(ServiceModel).all()
        return services
    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch services: {str(e)}"
        )

@router.get("/{service_id}", response_model=Service)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    try:
        service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch service: {str(e)}"
        )

@router.post("/", response_model=Service, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = service.model_dump() if hasattr(service, "model_dump") else service.dict()
        new_service = ServiceModel(**data)
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
        return new_service
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )

@router.put("/{service_id}", response_model=Service)
async def update_service(
    service_id: int,
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not db_service:
            raise HTTPException(status_code=404, detail="Service not found")

        data = service.model_dump() if hasattr(service, "model_dump") else service.dict()
        for key, value in data.items():
            setattr(db_service, key, value)

        db.commit()
        db.refresh(db_service)
        return db_service
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update service: {str(e)}"
        )

@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
        if not db_service:
            raise HTTPException(status_code=404, detail="Service not found")

        db.delete(db_service)
        db.commit()
        return {"message": "Service deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )
