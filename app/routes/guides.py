# app/routes/guides.py
from fastapi import APIRouter, Depends, HTTPException, status # <-- Add 'status'
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from .. import database, models, auth
from ..schemas import GuideCreate, Guide

router = APIRouter()

# --- NEW DELETE ENDPOINT ---
@router.delete("/{guide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guide(
    guide_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Find the guide
    db_guide = db.query(models.Guide).filter(models.Guide.id == guide_id).first()

    # 2. Check if it exists
    if not db_guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guide not found")

    # 3. CRITICAL: Check if the current user owns this guide
    if db_guide.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this guide")

    # 4. If all checks pass, delete it
    try:
        db.delete(db_guide)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting guide: {e}")
    
    # A 204 response has no body, so we return None
    return None

# --- PUBLIC SEARCH ENDPOINT (Unchanged) ---
@router.get("/public", response_model=List[Guide])
async def search_public_guides(search: str = "", db: Session = Depends(database.get_db)):
    # ... (rest of this function is unchanged)
    if search:
        search_term = f"%{search}%"
        return db.query(models.Guide).filter(
            or_(
                models.Guide.name.ilike(search_term),
                models.Guide.description.ilike(search_term)
            )
        ).all()
    return db.query(models.Guide).all()

# --- CREATE GUIDE ENDPOINT (Unchanged) ---
@router.post("/", status_code=201, response_model=Guide)
async def create_guide(
    guide: GuideCreate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    # ... (rest of this function is unchanged)
    existing_guide = db.query(models.Guide).filter(
        models.Guide.owner_id == current_user.id,
        models.Guide.shortcut == guide.shortcut
    ).first()
    if existing_guide:
        raise HTTPException(status_code=400, detail="A guide with this shortcut already exists.")
    try:
        db_guide = models.Guide(
            name=guide.name, 
            shortcut=guide.shortcut,
            description=guide.description,
            owner_id=current_user.id
        )
        db.add(db_guide)
        db.flush() 
        for i, step_data in enumerate(guide.steps):
            db_step = models.Step(
                step_number=i + 1,
                selector=step_data.selector,
                instruction=step_data.instruction,
                guide_id=db_guide.id
            )
            db.add(db_step)
        db.commit()
        db.refresh(db_guide)
        return db_guide
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating guide: {e}")

# --- GET MY GUIDES ENDPOINT (Unchanged) ---
@router.get("/", response_model=List[Guide])
async def get_user_guides(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.User).filter(models.User.id == current_user.id).first().guides