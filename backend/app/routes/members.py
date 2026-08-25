from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member
from app.core.cloud_storage import upload_image
from app.models.models import User, Memory, Member
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

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
        "registration_status": current_user.registration_status,
        "last_login": current_user.last_login,
        # Personal
        "full_name": member.full_name,
        "bangla_name": member.bangla_name,
        "nick_name": member.nick_name,
        "batch_roll": member.batch_roll,
        "department": member.department,
        "session": member.session,
        "student_id": member.student_id,
        "date_of_birth": str(member.date_of_birth) if member.date_of_birth else None,
        # Contact
        "phone": member.phone,
        "whatsapp": member.whatsapp,
        "current_address": member.current_address,
        "permanent_address": member.permanent_address,
        "current_location": member.current_location,
        "hall": member.hall,
        # Professional
        "profession": member.profession,
        "organization": member.organization,
        "designation": member.designation,
        "linkedin": member.linkedin,
        "facebook": member.facebook,
        # Profile
        "profile_photo": member.profile_photo,
        "bio": member.bio,
        "show_in_directory": member.show_in_directory,
        "show_phone": member.show_phone,
        "show_email": member.show_email,
    }

@router.put("/profile")
async def update_profile(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    try:
        data = await request.json()
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Profile not found")

    allowed = [
        "full_name", "nick_name", "phone", "whatsapp",
        "profession", "organization", "designation",
        "bio", "batch_roll", "session",
        "linkedin", "facebook",
        "current_location", "current_address", "permanent_address",
        "date_of_birth", "hall",
        "show_in_directory", "show_phone", "show_email"
    ]
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
    if photo.size and photo.size > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 2MB")
    ext = photo.filename.rsplit('.', 1)[-1].lower()
    if ext not in ['jpg','jpeg','png','gif','webp']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    try:
        url = upload_image(photo.file, "profiles")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    member = db.query(Member).filter(Member.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.profile_photo = url
    db.commit()
    return {"profile_photo": url}


@router.get("/directory")
def get_directory(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    from app.models.models import RegistrationStatus
    members = db.query(Member).join(User, Member.user_id == User.id).filter(
        User.registration_status == RegistrationStatus.APPROVED
    ).all()
    result = []
    for m in members:
        if not m.show_in_directory:
            continue
        entry = {
            "id": m.user_id,
            "full_name": m.full_name,
            "bangla_name": m.bangla_name,
            "nick_name": m.nick_name,
            "department": m.department,
            "session": m.session,
            "batch_roll": m.batch_roll,
            "student_id": m.student_id,
            "hall": m.hall,
            "date_of_birth": str(m.date_of_birth) if m.date_of_birth else None,
            "profession": m.profession,
            "designation": m.designation,
            "organization": m.organization,
            "current_location": m.current_location,
            "profile_photo": m.profile_photo,
            "linkedin": m.linkedin,
            "facebook": m.facebook,
            "bio": m.bio,
            "whatsapp": m.whatsapp,
            # Privacy-controlled fields
            "show_phone": m.show_phone,
            "show_email": m.show_email,
            "phone": m.phone if m.show_phone else None,
            "email": m.user.email if m.show_email else None,
        }
        result.append(entry)
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
            "is_approved": m.is_approved,
            "created_at": str(m.created_at)[:10] if m.created_at else "",
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
    photo_paths = []
    upload_errors = []
    for photo in photos[:3]:
        if photo and photo.filename:
            ext = photo.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg','jpeg','png','gif','webp']:
                upload_errors.append(f"{photo.filename}: unsupported file type")
                continue
            try:
                url = upload_image(photo.file, "memories")
            except RuntimeError as e:
                logger.error(f"Memory photo upload failed for {photo.filename}: {e}")
                upload_errors.append(f"{photo.filename}: {e}")
                continue
            photo_paths.append(url)

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
    response = {"message": "Memory shared!", "id": memory.id}
    if upload_errors:
        response["message"] = "Memory shared, but some photos failed to upload."
        response["photo_errors"] = upload_errors
    return response

@router.patch("/memories/{memory_id}/approve")
def approve_memory(memory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    if current_user.role.value not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    memory.is_approved = True
    db.commit()
    return {"message": "Memory approved"}

@router.put("/memories/{memory_id}")
async def update_memory(
    memory_id: int,
    title: str = Form(...),
    description: str = Form(""),
    year: str = Form(""),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    if memory.submitted_by != current_user.id and current_user.role.value not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Not authorized")
    memory.title = title
    memory.description = description or None
    memory.year = year or None
    memory.category = category or 'general'
    db.commit()
    return {"message": "Memory updated"}

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
