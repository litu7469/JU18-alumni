from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.core.database import get_db
from app.core.auth_middleware import get_admin_user
from app.models.models import User, Member, UserRole, RegistrationStatus, Event, Memory, Message
from app.schemas.schemas import AdminApproveRequest
from app.services.email_service import send_approval_email, send_rejection_email

router = APIRouter()

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return {
        "total_members": db.query(User).filter(User.registration_status == RegistrationStatus.APPROVED).count(),
        "pending_approvals": db.query(User).filter(User.registration_status == RegistrationStatus.EMAIL_VERIFIED).count(),
        "total_registrations": db.query(User).count(),
        "total_events": db.query(Event).count(),
        "total_memories": db.query(Memory).count(),
        "total_messages": db.query(Message).count(),
    }

@router.get("/pending-members")
def get_pending_members(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).filter(
        User.registration_status == RegistrationStatus.EMAIL_VERIFIED
    ).all()

    result = []
    for u in users:
        m = u.member
        result.append({
            "user_id": u.id,
            "email": u.email,
            "full_name": m.full_name if m else "N/A",
            "department": m.department if m else None,
            "session": m.session if m else None,
            "phone": m.phone if m else None,
            "profession": m.profession if m else None,
            "registration_status": u.registration_status,
            "created_at": u.created_at,
        })
    return result

@router.post("/approve-member")
def approve_member(
    data: AdminApproveRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    member = user.member

    if data.action == "approve":
        user.registration_status = RegistrationStatus.APPROVED
        if member:
            member.approved_by = admin.id
            member.approved_at = datetime.utcnow()
        db.commit()
        send_approval_email(user.email, member.full_name if member else "Alumni")
        return {"message": f"{member.full_name if member else user.email} approved successfully"}

    elif data.action == "reject":
        user.registration_status = RegistrationStatus.REJECTED
        if member:
            member.rejected_reason = data.reason
        db.commit()
        send_rejection_email(user.email, member.full_name if member else "Alumni", data.reason or "")
        return {"message": "Member rejected"}

    raise HTTPException(status_code=400, detail="Invalid action")

@router.get("/all-members")
def get_all_members(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).all()
    result = []
    for u in users:
        m = u.member
        result.append({
            "user_id": u.id,
            "email": u.email,
            "role": u.role,
            "full_name": m.full_name if m else "N/A",
            "department": m.department if m else None,
            "registration_status": u.registration_status,
            "created_at": u.created_at,
            "last_login": u.last_login,
        })
    return result

@router.put("/member/{user_id}/role")
def update_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"message": "Role updated"}

@router.delete("/member/{user_id}")
def delete_member(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot delete super admin")
    db.delete(user)
    db.commit()
    return {"message": "Member deleted"}
