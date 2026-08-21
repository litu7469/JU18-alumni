from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.core.database import get_db
from app.core.auth_middleware import get_admin_user
from app.core.security import generate_token
from app.models.models import User, Member, UserRole, RegistrationStatus, Event, Memory, Message
from app.schemas.schemas import AdminApproveRequest
from app.services.email_service import send_set_password_email, send_rejection_email, send_password_reset_email
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return {
        "total_members":      db.query(User).filter(User.registration_status == RegistrationStatus.APPROVED).count(),
        "pending_approvals":  db.query(User).filter(User.registration_status == RegistrationStatus.EMAIL_VERIFIED).count(),
        "total_registrations": db.query(User).filter(User.role == UserRole.MEMBER).count(),
        "total_events":       db.query(Event).count(),
        "total_memories":     db.query(Memory).count(),
        "total_messages":     db.query(Message).count(),
    }


@router.get("/pending-members")
def get_pending_members(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    users = db.query(User).filter(
        User.registration_status == RegistrationStatus.EMAIL_VERIFIED,
        User.role == UserRole.MEMBER
    ).order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        m = u.member
        result.append({
            "user_id": u.id,
            "email": u.email,
            "full_name": m.full_name if m else "N/A",
            "department": m.department if m else None,
            "phone": m.phone if m else None,
            "registration_status": u.registration_status,
            "created_at": u.created_at,
        })
    return result


@router.post("/approve-member")
def approve_member(
    data: AdminApproveRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent approving admin account
    if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=400, detail="Cannot change approval status of admin accounts")

    member = user.member

    if data.action == "approve":
        token = generate_token()
        user.registration_status = RegistrationStatus.APPROVED
        user.reset_password_token = token
        user.reset_password_expires = datetime.now(timezone.utc) + timedelta(hours=48)
        if member:
            member.approved_by = admin.id
            member.approved_at = datetime.now(timezone.utc)
        db.commit()

        name = member.full_name if member else "Alumni"
        background_tasks.add_task(send_set_password_email, user.email, name, token)
        logger.info(f"Admin {admin.id} approved user {user.id} ({user.email})")
        return {"message": f"{name} approved! Password setup email sent."}

    elif data.action == "reject":
        user.registration_status = RegistrationStatus.REJECTED
        if member:
            member.rejected_reason = data.reason
        db.commit()

        name = member.full_name if member else "Alumni"
        background_tasks.add_task(send_rejection_email, user.email, name, data.reason or "")
        logger.info(f"Admin {admin.id} rejected user {user.id} ({user.email})")
        return {"message": "Member rejected and notified."}

    raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")


@router.get("/all-members")
def get_all_members(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    # Exclude super admin from the list
    users = db.query(User).filter(
        User.role != UserRole.SUPER_ADMIN
    ).order_by(User.created_at.desc()).all()

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
            "is_active": u.is_active,
            "created_at": u.created_at,
            "last_login": u.last_login,
        })
    return result


@router.post("/member/{user_id}/make-admin")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    # Only super admin can assign admin role
    if admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can assign admin role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot change super admin role")
    if user.registration_status != RegistrationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="User must be an approved member first")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user.role = UserRole.ADMIN
    db.commit()
    logger.info(f"Super admin {admin.id} made user {user_id} an admin")
    return {"message": f"{user.email} is now an Admin"}


@router.post("/member/{user_id}/revoke-admin")
def revoke_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    # Only super admin can revoke admin role
    if admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can revoke admin role")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot change super admin role")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user.role = UserRole.MEMBER
    db.commit()
    logger.info(f"Super admin {admin.id} revoked admin from user {user_id}")
    return {"message": f"{user.email} admin role revoked"}


@router.post("/member/{user_id}/reset-password")
def admin_reset_password(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot reset super admin password this way")
    if user.registration_status != RegistrationStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Member must be approved before a password reset can be sent")

    token = generate_token()
    user.reset_password_token = token
    user.reset_password_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    db.commit()

    member = user.member
    name = member.full_name if member else "Alumni"
    background_tasks.add_task(send_password_reset_email, user.email, name, token)
    logger.info(f"Admin {admin.id} sent password reset link to user {user.id} ({user.email})")
    return {"message": f"Password reset link sent to {user.email}"}


@router.post("/member/{user_id}/toggle-active")
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot disable super admin")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")

    user.is_active = not user.is_active
    db.commit()
    status = "enabled" if user.is_active else "disabled"
    logger.info(f"Admin {admin.id} {status} user {user_id}")
    return {"message": f"Account {status}", "is_active": user.is_active}


@router.delete("/member/{user_id}")
def delete_member(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    # Only super admin can delete
    if admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admin can delete members")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Cannot delete super admin")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    # Soft delete — deactivate instead of hard delete to preserve data integrity
    user.is_active = False
    user.registration_status = RegistrationStatus.REJECTED
    db.commit()
    logger.info(f"Super admin {admin.id} soft-deleted user {user_id}")
    return {"message": "Member removed successfully"}