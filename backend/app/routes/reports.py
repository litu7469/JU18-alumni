from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.auth_middleware import get_admin_user
from app.models.models import User, Member, UserRole, RegistrationStatus, Event, EventRegistration
import csv, io

router = APIRouter()

@router.get("/members")
def export_members(
    department: str = None,
    hall: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    query = db.query(User, Member).join(Member, Member.user_id == User.id)
    if department:
        query = query.filter(Member.department == department)
    if hall:
        query = query.filter(Member.hall == hall)
    if status:
        query = query.filter(User.registration_status == status)

    rows = query.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "SL", "Full Name", "Nick Name", "Email", "Phone", "WhatsApp",
        "Department", "Hall", "Profession", "Organization",
        "Designation", "Current Location", "Bio",
        "LinkedIn", "Facebook", "Status", "Role",
        "Registration Date"
    ])
    for i, (user, member) in enumerate(rows, 1):
        writer.writerow([
            i,
            member.full_name,
            getattr(member, "nick_name", "") or "",
            user.email,
            getattr(member, "phone", "") or "",
            getattr(member, "whatsapp", "") or "",
            getattr(member, "department", "") or "",
            getattr(member, "hall", "") or "",
            getattr(member, "profession", "") or "",
            getattr(member, "organization", "") or "",
            getattr(member, "designation", "") or "",
            getattr(member, "current_location", "") or "",
            getattr(member, "bio", "") or "",
            getattr(member, "linkedin", "") or "",
            getattr(member, "facebook", "") or "",
            str(user.registration_status.value) if user.registration_status else "",
            str(user.role.value) if user.role else "",
            str(user.created_at)[:10] if user.created_at else "",
        ])

    output.seek(0)
    filename = f"members_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    total = db.query(User).count()
    approved = db.query(User).filter(User.registration_status == RegistrationStatus.APPROVED).count()
    pending = db.query(User).filter(User.registration_status == RegistrationStatus.EMAIL_VERIFIED).count()
    rejected = db.query(User).filter(User.registration_status == RegistrationStatus.REJECTED).count()
    
    # By department
    from sqlalchemy import func
    dept_stats = db.query(Member.department, func.count(Member.id)).group_by(Member.department).all()
    
    # By hall
    hall_stats = db.query(Member.hall, func.count(Member.id)).filter(Member.hall != None).group_by(Member.hall).all()

    # Events
    try:
        total_events = db.query(Event).count()
    except:
        total_events = 0

    return {
        "members": {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
        },
        "by_department": [{"department": d or "Unknown", "count": c} for d, c in dept_stats],
        "by_hall": [{"hall": h or "Unknown", "count": c} for h, c in hall_stats],
        "events": {"total": total_events},
    }

@router.get("/events")
def export_events(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    events = db.query(Event).order_by(Event.event_date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["SL", "Title", "Date", "Time", "Venue", "Type", "RSVP Count", "Max Attendees", "Published", "Created At"])
    
    for i, e in enumerate(events, 1):
        rsvp_count = 0
        try:
            from app.models.models import EventRegistration
            rsvp_count = db.query(EventRegistration).filter(EventRegistration.event_id == e.id).count()
        except:
            pass
        writer.writerow([
            i, e.title,
            str(e.event_date)[:10] if e.event_date else "",
            str(getattr(e, "event_time", "")) or "",
            getattr(e, "venue", "") or "",
            getattr(e, "event_type", "") or "",
            rsvp_count,
            getattr(e, "max_attendees", "") or "",
            getattr(e, "is_published", True),
            str(e.created_at)[:10] if e.created_at else "",
        ])

    output.seek(0)
    filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/event-registrations")
def export_event_registrations(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    try:
        from sqlalchemy import text
        rows = db.execute(text("""
            SELECT e.title, e.event_date, m.full_name, m.department, u.email, m.phone, er.registered_at
            FROM event_registrations er
            JOIN events e ON e.id = er.event_id
            JOIN users u ON u.id = er.user_id
            JOIN members m ON m.user_id = er.user_id
            ORDER BY e.event_date DESC, m.full_name
        """)).fetchall()
    except Exception as ex:
        rows = []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event", "Event Date", "Member Name", "Department", "Email", "Phone", "RSVP Date"])
    for row in rows:
        writer.writerow([str(c) if c else "" for c in row])

    output.seek(0)
    filename = f"event_registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
