from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import SkillModel
from schemas import SkillCreate, Skill
from routers.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("/", response_model=List[Skill])
async def get_skills(db: Session = Depends(get_db)):
    try:
        skills = db.query(SkillModel).all()
        return skills
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch skills: {str(e)}"
        )

@router.get("/{skill_id}", response_model=Skill)
async def get_skill(skill_id: int, db: Session = Depends(get_db)):
    try:
        skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        return skill
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch skill: {str(e)}"
        )

@router.post("/", response_model=Skill)
async def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        data = skill.model_dump() if hasattr(skill, "model_dump") else skill.dict()
        new_skill = SkillModel(**data)
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
        return new_skill
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create skill: {str(e)}"
        )

@router.put("/{skill_id}", response_model=Skill)
async def update_skill(
    skill_id: int,
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        db_skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
        if not db_skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        data = skill.model_dump() if hasattr(skill, "model_dump") else skill.dict()
        for key, value in data.items():
            setattr(db_skill, key, value)
        
        db.commit()
        db.refresh(db_skill)
        return db_skill
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update skill: {str(e)}"
        )

@router.delete("/{skill_id}")
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        db_skill = db.query(SkillModel).filter(SkillModel.id == skill_id).first()
        if not db_skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        db.delete(db_skill)
        db.commit()
        return {"message": "Skill deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete skill: {str(e)}"
        )

