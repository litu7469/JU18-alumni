from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member, get_admin_user
from app.models.models import User, Member, Announcement
from pydantic import BaseModel

router = APIRouter()

class AnnouncementCreate(BaseModel):
    title: str
    content: Optional[str] = None
    body: Optional[str] = None  # accepted as an alias for 'content' for backwards compatibility
    priority: Optional[str] = "normal"
    is_pinned: Optional[bool] = None
    is_published: Optional[bool] = True
    expires_at: Optional[str] = None
    send_email: Optional[bool] = False

    def resolved_content(self) -> str:
        return self.content if self.content is not None else (self.body or "")

    def resolved_is_pinned(self) -> bool:
        return self.is_pinned if self.is_pinned is not None else (self.priority == "urgent")


def _serialize_announcement(a: Announcement) -> dict:
    return {
        "id": a.id,
        "title": a.title,
        # Both naming conventions are returned since different pages consume
        # different field names (member dashboard uses body/priority, admin
        # dashboard uses content/is_pinned/expires_at).
        "body": a.content,
        "content": a.content,
        "priority": "urgent" if a.is_pinned else "normal",
        "is_pinned": a.is_pinned,
        "is_active": a.is_published,
        "is_published": a.is_published,
        "expires_at": str(a.expires_at) if a.expires_at else None,
        "created_at": str(a.created_at),
        "created_by": "Admin",
    }


@router.get("")
def get_announcements(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    items = db.query(Announcement).filter(Announcement.is_published == True).order_by(Announcement.created_at.desc()).limit(10).all()
    return [_serialize_announcement(a) for a in items]

@router.post("")
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    content = data.resolved_content()
    if not data.title or not content:
        raise HTTPException(status_code=422, detail="Title and content are required")

    expires = None
    if data.expires_at:
        try:
            expires = datetime.fromisoformat(data.expires_at)
        except ValueError:
            expires = None

    ann = Announcement(
        title=data.title,
        content=content,
        is_published=data.is_published if data.is_published is not None else True,
        is_pinned=data.resolved_is_pinned(),
        expires_at=expires,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)

    sent = 0
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
                <p style="color:#444;line-height:1.6;">{content.replace(chr(10), '<br>')}</p>
            </div>
            <div style="background:#f4f7fb;padding:16px;text-align:center;font-size:12px;color:#666;">
                JU 18th Batch Alumni Association
            </div>
        </div>
        """
        sent = sum(1 for u in users if send_email(u.email, f"📢 {data.title}", html))

    msg = f"Announcement created and emailed to {sent} members" if data.send_email else "Announcement created!"
    return {"message": msg, "id": ann.id}

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    ann = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not ann:
        raise HTTPException(status_code=404, detail="Not found")
    ann.is_published = False
    db.commit()
    return {"message": "Announcement removed"}

@router.get("/admin/all")
def admin_get_announcements(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    items = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return [_serialize_announcement(a) for a in items]
