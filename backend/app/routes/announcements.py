from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member, get_admin_user
from app.models.models import User, Member
from pydantic import BaseModel

router = APIRouter()

class AnnouncementCreate(BaseModel):
    title: str
    body: str
    priority: Optional[str] = "normal"  # normal, important, urgent
    send_email: Optional[bool] = False

# In-memory store (replace with DB model later)
announcements = []
_next_id = 1

@router.get("")
def get_announcements(current_user: User = Depends(get_approved_member)):
    return [a for a in reversed(announcements) if a["is_active"]]

@router.post("")
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    global _next_id
    admin_member = db.query(Member).filter(Member.user_id == current_user.id).first()
    
    announcement = {
        "id": _next_id,
        "title": data.title,
        "body": data.body,
        "priority": data.priority or "normal",
        "created_by": admin_member.full_name if admin_member else current_user.email,
        "created_at": datetime.utcnow().isoformat(),
        "is_active": True,
    }
    announcements.append(announcement)
    _next_id += 1

    # Send email if requested
    if data.send_email:
        from app.services.email_service import send_email
        from app.models.models import RegistrationStatus
        users = db.query(User).filter(User.registration_status == RegistrationStatus.APPROVED).all()
        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:#1a3a5c;padding:24px;text-align:center;">
                <h1 style="color:#c9a84c;margin:0;font-size:22px;">JU 18th Batch Alumni</h1>
                <p style="color:rgba(255,255,255,0.8);margin:8px 0 0;">📢 New Announcement</p>
            </div>
            <div style="padding:32px;background:#fff;">
                <h2 style="color:#1a3a5c;">{data.title}</h2>
                <p style="color:#444;line-height:1.6;">{data.body.replace(chr(10), "<br>")}</p>
            </div>
            <div style="background:#f4f7fb;padding:16px;text-align:center;font-size:12px;color:#666;">
                JU 18th Batch Alumni Association
            </div>
        </div>
        """
        sent = sum(1 for u in users if send_email(u.email, f"📢 {data.title}", html))
        return {"message": f"Announcement created and emailed to {sent} members", "id": announcement["id"]}

    return {"message": "Announcement created!", "id": announcement["id"]}

@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    current_user: User = Depends(get_admin_user)
):
    global announcements
    ann = next((a for a in announcements if a["id"] == announcement_id), None)
    if not ann:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann["is_active"] = False
    return {"message": "Announcement removed"}

@router.get("/admin/all")
def admin_get_announcements(current_user: User = Depends(get_admin_user)):
    return list(reversed(announcements))
