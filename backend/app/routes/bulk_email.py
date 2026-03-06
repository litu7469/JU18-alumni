from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.core.database import get_db
from app.core.auth_middleware import get_admin_user
from app.models.models import User, Member, UserRole, RegistrationStatus
from app.services.email_service import send_email
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BulkEmailRequest(BaseModel):
    subject: str
    body: str
    recipient_type: str  # "all", "department", "hall", "custom"
    department: Optional[str] = None
    hall: Optional[str] = None
    custom_emails: Optional[List[str]] = None

class EmailLog(BaseModel):
    subject: str
    recipient_count: int
    recipient_type: str
    sent_at: str
    sent_by: str

# In-memory log (replace with DB later)
sent_logs = []

@router.post("/send")
def send_bulk_email(
    data: BulkEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    # Build recipient list
    query = db.query(User).join(Member, Member.user_id == User.id).filter(
        User.registration_status == RegistrationStatus.APPROVED
    )
    
    if data.recipient_type == "department" and data.department:
        query = query.filter(Member.department == data.department)
    elif data.recipient_type == "hall" and data.hall:
        query = query.filter(Member.hall == data.hall)
    elif data.recipient_type == "custom" and data.custom_emails:
        query = query.filter(User.email.in_(data.custom_emails))
    
    users = query.all()
    if not users:
        raise HTTPException(status_code=400, detail="No recipients found")

    # Build HTML email body
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 24px; text-align: center;">
            <h1 style="color: #c9a84c; margin: 0; font-size: 22px;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 32px; background: #ffffff;">
            {data.body.replace(chr(10), "<br>")}
        </div>
        <div style="background: #f4f7fb; padding: 16px; text-align: center; font-size: 12px; color: #666;">
            JU 18th Batch Alumni Association &mdash; ju18-alumni-production.up.railway.app
        </div>
    </div>
    """

    sent = 0
    failed = 0
    for user in users:
        try:
            success = send_email(user.email, data.subject, html_body)
            if success:
                sent += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Failed to send to {user.email}: {e}")
            failed += 1

    # Log it
    admin_member = db.query(Member).filter(Member.user_id == current_user.id).first()
    sent_logs.append({
        "subject": data.subject,
        "recipient_type": data.recipient_type,
        "recipient_count": sent,
        "sent_at": datetime.utcnow().isoformat(),
        "sent_by": admin_member.full_name if admin_member else current_user.email,
    })

    return {
        "message": f"Email sent to {sent} members",
        "sent": sent,
        "failed": failed,
        "total": len(users)
    }

@router.get("/logs")
def get_email_logs(current_user: User = Depends(get_admin_user)):
    return list(reversed(sent_logs))

@router.get("/recipients/preview")
def preview_recipients(
    recipient_type: str,
    department: Optional[str] = None,
    hall: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    query = db.query(User).join(Member, Member.user_id == User.id).filter(
        User.registration_status == RegistrationStatus.APPROVED
    )
    if recipient_type == "department" and department:
        query = query.filter(Member.department == department)
    elif recipient_type == "hall" and hall:
        query = query.filter(Member.hall == hall)
    
    users = query.all()
    return {
        "count": len(users),
        "emails": [u.email for u in users[:10]],  # preview first 10
        "note": f"Showing first 10 of {len(users)} recipients"
    }
