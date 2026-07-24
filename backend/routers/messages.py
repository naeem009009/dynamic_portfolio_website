from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import MessageModel
from schemas import MessageCreate, Message

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=Message)
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    try:
        data = message.model_dump() if hasattr(message, "model_dump") else message.dict()
        new_message = MessageModel(**data)
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        return new_message
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )

@router.get("/", response_model=List[Message])
async def get_messages(db: Session = Depends(get_db)):
    try:
        messages = db.query(MessageModel).order_by(MessageModel.created_at.desc()).all()
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )

@router.get("/{message_id}", response_model=Message)
async def get_message(message_id: int, db: Session = Depends(get_db)):
    try:
        message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch message: {str(e)}"
        )

@router.delete("/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    try:
        db_message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if not db_message:
            raise HTTPException(status_code=404, detail="Message not found")

        db.delete(db_message)
        db.commit()
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete message: {str(e)}"
        )

@router.patch("/{message_id}/read")
async def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    try:
        db_message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
        if not db_message:
            raise HTTPException(status_code=404, detail="Message not found")

        db_message.is_read = True
        db.commit()
        db.refresh(db_message)
        return db_message
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark message as read: {str(e)}"
        )
