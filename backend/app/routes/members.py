from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.auth_middleware import get_current_user, get_approved_member
from app.models.models import User, Member, RegistrationStatus
from app.schemas.schemas import MemberProfileUpdate, MemberResponse
from app.core.config import settings
import os, shutil, uuid

router = APIRouter()

@router.get("/directory")
def get_directory(
    search: str = Query(None),
    department: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_approved_member),
    db: Session = Depends(get_db)
):
    query = db.query(Member).join(User).filter(
        User.registration_status == RegistrationStatus.APPROVED,
        Member.show_in_directory == True
    )

    if search:
        query = query.filter(
            or_(
                Member.full_name.ilike(f"%{search}%"),
                Member.profession.ilike(f"%{search}%"),
                Member.organization.ilike(f"%{search}%"),
                Member.department.ilike(f"%{search}%"),
            )
        )
    if department:
        query = query.filter(Member.department == department)

    total = query.count()
    members = query.offset((page - 1) * per_page).limit(per_page).all()

    result = []
    for m in members:
        member_data = {
            "id": m.id,
            "full_name": m.full_name,
            "bangla_name": m.bangla_name,
            "batch_roll": m.batch_roll,
            "department": m.department,
            "session": m.session,
            "profession": m.profession,
            "organization": m.organization,
            "designation": m.designation,
            "profile_photo": m.profile_photo,
            "bio": m.bio,
            "linkedin": m.linkedin,
            "facebook": m.facebook,
            "phone": m.phone if m.show_phone else None,
            "email": m.user.email if m.show_email else None,
        }
        result.append(member_data)

    return {"members": result, "total": total, "page": page, "per_page": per_page}

@router.get("/profile")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = current_user.member
    if not member:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": member.id,
        "full_name": member.full_name,
        "bangla_name": member.bangla_name,
        "batch_roll": member.batch_roll,
        "department": member.department,
        "session": member.session,
        "phone": member.phone,
        "whatsapp": member.whatsapp,
        "current_address": member.current_address,
        "permanent_address": member.permanent_address,
        "profession": member.profession,
        "organization": member.organization,
        "designation": member.designation,
        "linkedin": member.linkedin,
        "facebook": member.facebook,
        "profile_photo": member.profile_photo,
        "bio": member.bio,
        "show_in_directory": member.show_in_directory,
        "show_phone": member.show_phone,
        "show_email": member.show_email,
        "email": current_user.email,
        "registration_status": current_user.registration_status,
    }

@router.put("/profile")
def update_profile(
    data: MemberProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    member = current_user.member
    if not member:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in data.dict(exclude_none=True).items():
        setattr(member, field, value)

    db.commit()
    return {"message": "Profile updated successfully"}

@router.post("/profile/photo")
def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    os.makedirs(f"{settings.UPLOAD_DIR}/profiles", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = f"{settings.UPLOAD_DIR}/profiles/{filename}"

    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    current_user.member.profile_photo = f"/uploads/profiles/{filename}"
    db.commit()

    return {"photo_url": f"/uploads/profiles/{filename}"}

@router.get("/{member_id}")
def get_member(
    member_id: int,
    current_user: User = Depends(get_approved_member),
    db: Session = Depends(get_db)
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    return {
        "id": member.id,
        "full_name": member.full_name,
        "bangla_name": member.bangla_name,
        "department": member.department,
        "session": member.session,
        "profession": member.profession,
        "organization": member.organization,
        "designation": member.designation,
        "profile_photo": member.profile_photo,
        "bio": member.bio,
        "linkedin": member.linkedin,
        "facebook": member.facebook,
        "phone": member.phone if member.show_phone else None,
        "email": member.user.email if member.show_email else None,
    }
