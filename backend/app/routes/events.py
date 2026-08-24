from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member, get_admin_user
from app.models.models import User, Event, Member, EventRegistration
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Schemas ────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: str
    event_time: Optional[str] = None
    venue: Optional[str] = None
    event_type: Optional[str] = "general"
    is_rsvp_enabled: Optional[bool] = True
    is_published: Optional[bool] = True
    max_attendees: Optional[int] = 0
    registration_fee: Optional[float] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    venue: Optional[str] = None
    event_type: Optional[str] = None
    is_rsvp_enabled: Optional[bool] = None
    max_attendees: Optional[int] = None
    is_published: Optional[bool] = None
    registration_fee: Optional[float] = None


# ── Helper ─────────────────────────────────────────────────────────────────

def format_event(e, db, current_user_id=None):
    rsvp_count = 0
    user_rsvpd = False
    try:
        rsvp_count = db.query(EventRegistration).filter(
            EventRegistration.event_id == e.id
        ).count()
        if current_user_id:
            user_rsvpd = db.query(EventRegistration).filter(
                EventRegistration.event_id == e.id,
                EventRegistration.user_id == current_user_id
            ).first() is not None
    except Exception as ex:
        logger.error(f"Error fetching RSVP info for event {e.id}: {ex}")

    return {
        "id": e.id,
        "title": e.title,
        "description": e.description,
        "event_date": str(e.event_date) if e.event_date else None,
        "event_time": str(e.location or ""),   # stored in location for now
        "venue": e.location,
        "event_type": "general",
        "is_rsvp_enabled": e.registration_required,
        "registration_fee": float(e.registration_fee) if e.registration_fee else 0,
        "max_attendees": e.max_attendees,
        "is_published": e.is_published,
        "image": e.image,
        "created_by": e.created_by,
        "created_at": str(e.created_at) if e.created_at else None,
        "rsvp_count": rsvp_count,
        "user_rsvpd": user_rsvpd,
    }


# ── IMPORTANT: Admin routes MUST come before /{event_id} ──────────────────

@router.get("/admin/all")
def admin_get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    events = db.query(Event).order_by(Event.event_date.desc()).all()
    return [format_event(e, db) for e in events]


@router.post("/admin/create")
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    try:
        event_date = datetime.strptime(data.event_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    event = Event(
        title=data.title,
        description=data.description,
        event_date=event_date,
        location=data.venue,
        max_attendees=data.max_attendees if data.max_attendees else None,
        registration_required=data.is_rsvp_enabled,
        registration_fee=data.registration_fee if data.registration_fee else None,
        is_published=data.is_published,
        created_by=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(f"Event created: {event.id} by admin {current_user.id}")
    return {"message": "Event created!", "id": event.id}


@router.put("/admin/{event_id}")
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    field_map = {
        "venue": "location",
        "is_rsvp_enabled": "registration_required"
    }

    for key, value in data.dict(exclude_unset=True).items():
        if value is None:
            continue
        if key == "event_date":
            try:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        actual_key = field_map.get(key, key)
        if hasattr(event, actual_key):
            setattr(event, actual_key, value)

    event.updated_at = datetime.utcnow()
    db.commit()
    logger.info(f"Event updated: {event_id} by admin {current_user.id}")
    return {"message": "Event updated!"}


@router.delete("/admin/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    logger.info(f"Event deleted: {event_id} by admin {current_user.id}")
    return {"message": "Event deleted!"}


@router.get("/admin/{event_id}/attendees")
def get_attendees(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    rsvps = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id
    ).all()

    result = []
    for r in rsvps:
        member = db.query(Member).filter(Member.user_id == r.user_id).first()
        result.append({
            "user_id": r.user_id,
            "full_name": member.full_name if member else "Unknown",
            "department": member.department if member else None,
            "phone": member.phone if member else None,
            "rsvp_date": str(r.registered_at) if r.registered_at else "",
        })
    return result


# ── Member endpoints (AFTER admin routes) ─────────────────────────────────

@router.get("")
def get_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    events = db.query(Event).filter(
        Event.is_published == True
    ).order_by(Event.event_date.asc()).all()
    return [format_event(e, db, current_user.id) for e in events]


@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return format_event(e, db, current_user.id)


@router.post("/{event_id}/rsvp")
def toggle_rsvp(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_approved_member)
):
    e = db.query(Event).filter(
        Event.id == event_id,
        Event.is_published == True
    ).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    if not e.registration_required:
        raise HTTPException(status_code=400, detail="RSVP not enabled for this event")

    existing = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"message": "RSVP cancelled", "rsvpd": False}

    # Check capacity
    if e.max_attendees:
        count = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id
        ).count()
        if count >= e.max_attendees:
            raise HTTPException(status_code=400, detail="Event is full")

    rsvp = EventRegistration(event_id=event_id, user_id=current_user.id)
    db.add(rsvp)
    db.commit()
    return {"message": "RSVP confirmed", "rsvpd": True}