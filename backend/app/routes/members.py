from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member
from app.models.models import User, Memory, Member
from pydantic import BaseModel
from typing import Optional
import shutil, uuid

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
        "profession": getattr(member, "profession", None),
        "bio": getattr(member, "bio", None),
        "profile_photo": getattr(member, "profile_photo", None),
        "current_location": getattr(member, "current_location", None),
        "nick_name": getattr(member, "nick_name", None),
        "hall": getattr(member, "hall", None),
        "whatsapp": getattr(member, "whatsapp", None),
        "organization": getattr(member, "organization", None),
        "designation": getattr(member, "designation", None),
        "linkedin": getattr(member, "linkedin", None),
        "facebook": getattr(member, "facebook", None),
        "date_of_birth": getattr(member, "date_of_birth", None),
        "show_in_directory": getattr(member, "show_in_directory", True),
        "show_phone": getattr(member, "show_phone", False),
        "show_email": getattr(member, "show_email", False),
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

@router.post("/profile/photo")
async def upload_profile_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    import os
    if photo.size and photo.size > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 2MB")
    ext = photo.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg','jpeg','png','gif','webp']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    os.makedirs("uploads/profiles", exist_ok=True)
    filename = f"profiles/{uuid.uuid4().hex}.{ext}"
    with open(f"uploads/{filename}", "wb") as f:
        shutil.copyfileobj(photo.file, f)
    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.profile_photo = filename
    db.commit()
    return {"profile_photo": filename}


@router.get("/directory")
def get_directory(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    from app.models.models import RegistrationStatus
    members = db.query(Member).join(User, Member.user_id == User.id).filter(
        User.registration_status == RegistrationStatus.APPROVED
    ).all()
    result = []
    for m in members:
        result.append({
            "id": m.user_id,
            "full_name": m.full_name,
            "department": getattr(m, "department", None),
            "profession": getattr(m, "profession", None),
            "current_location": getattr(m, "current_location", None),
            "profile_photo": getattr(m, "profile_photo", None),
            "batch_roll": getattr(m, "batch_roll", None),
            "session": getattr(m, "session", None),
        })
    return result


@router.get("/memories")
def get_memories(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    memories = db.query(Memory).filter(Memory.is_approved == True).order_by(Memory.created_at.desc()).all()
    result = []
    for m in memories:
        author = db.query(Member).filter(Member.user_id == m.submitted_by).first()
        # photos stored as comma-separated in image field
        photos = [p.strip() for p in m.image.split(',')] if m.image else []
        result.append({
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "photos": photos,
            "year": m.year,
            "category": m.category,
            "author_name": author.full_name if author else "Alumni",
            "submitted_by": m.submitted_by,
            "created_at": m.created_at,
        })
    return result

@router.post("/memories")
async def create_memory(
    title: str = Form(...),
    description: str = Form(""),
    year: str = Form(""),
    category: str = Form("general"),
    photos: list[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    import os
    os.makedirs("uploads/memories", exist_ok=True)
    photo_paths = []
    for photo in photos[:3]:
        if photo and photo.filename:
            ext = photo.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg','jpeg','png','gif','webp']:
                continue
            filename = f"memories/{uuid.uuid4().hex}.{ext}"
            with open(f"uploads/{filename}", "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            photo_paths.append(filename)

    memory = Memory(
        submitted_by=current_user.id,
        title=title,
        description=description or None,
        image=','.join(photo_paths) if photo_paths else None,
        year=year or None,
        category=category or 'general',
        is_approved=True,
        created_at=datetime.utcnow(),
    )
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return {"message": "Memory shared!", "id": memory.id}

@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    # Only owner or admin can delete
    from app.models.models import UserRole
    if memory.submitted_by != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(memory)
    db.commit()
    return {"message": "Memory deleted"}
