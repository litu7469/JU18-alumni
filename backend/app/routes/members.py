from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member
from app.models.models import User, Memory, Member
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "full_name": member.full_name,
        "phone": getattr(member, "phone", None),
        "department": getattr(member, "department", None),
        "batch_roll": getattr(member, "batch_roll", None),
        "session": getattr(member, "session", None),
        "profession": getattr(member, "profession", None),
        "bio": getattr(member, "bio", None),
        "profile_photo": getattr(member, "profile_photo", None),
        "linkedin_url": getattr(member, "linkedin_url", None),
        "facebook_url": getattr(member, "facebook_url", None),
        "current_location": getattr(member, "current_location", None),
        "registration_status": current_user.registration_status,
        "last_login": current_user.last_login,
    }

@router.put("/profile")
def update_profile(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Profile not found")
    allowed = ["full_name", "phone", "profession", "bio", "batch_roll", "session", "linkedin_url", "facebook_url", "current_location"]
    for key, value in data.items():
        if key in allowed and hasattr(member, key):
            setattr(member, key, value)
    db.commit()
    return {"message": "Profile updated successfully"}

@router.get("/directory")
def get_directory(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    from app.models.models import RegistrationStatus, UserRole
    members = db.query(Member).join(User).filter(
        User.registration_status == RegistrationStatus.APPROVED
    ).all()
    return [{
        "id": m.user_id,
        "full_name": m.full_name,
        "department": m.department,
        "profession": m.profession,
        "current_location": m.current_location,
        "profile_photo": m.profile_photo,
        "batch_roll": m.batch_roll,
    } for m in members]


class MemoryCreate(BaseModel):
    title: str
    description: Optional[str] = None

@router.get("/memories")
def get_memories(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    memories = db.query(Memory).order_by(Memory.created_at.desc()).all()
    result = []
    for m in memories:
        author = db.query(Member).filter(Member.user_id == m.user_id).first()
        result.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "author_name": author.full_name if author else "Alumni",
            "created_at": m.created_at,
        })
    return result

@router.post("/memories")
def create_memory(data: MemoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    memory = Memory(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        created_at=datetime.utcnow(),
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return {"message": "Memory shared!", "id": memory.id}
