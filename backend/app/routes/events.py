from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.core.database import get_db
from app.core.auth_middleware import get_approved_member, get_admin_user
from app.models.models import User, Event, Member, EventRegistration
from pydantic import BaseModel
import shutil, uuid, os

router = APIRouter()

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: str
    event_time: Optional[str] = None
    venue: Optional[str] = None
    location: Optional[str] = None
    event_type: Optional[str] = "general"
    is_rsvp_enabled: Optional[bool] = True
    is_published: Optional[bool] = True
    max_attendees: Optional[int] = 0

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

def format_event(e, db, current_user_id=None):
    rsvp_count = 0
    user_rsvpd = False
    if hasattr(e, 'rsvps'):
        rsvp_count = len(e.rsvps) if e.rsvps else 0
    # Check RSVP table
    try:
        from app.models.models import EventRegistration
        rsvp_count = db.query(EventRegistration).filter(EventRegistration.event_id == e.id).count()
        if current_user_id:
            user_rsvpd = db.query(EventRegistration).filter(
                EventRegistration.event_id == e.id,
                EventRegistration.user_id == current_user_id
            ).first() is not None
    except:
        pass
    return {
        "id": e.id,
        "title": e.title,
        "description": getattr(e, 'description', None),
        "event_date": str(e.event_date) if e.event_date else None,
        "event_time": str(getattr(e, 'event_time', None) or ''),
        "venue": getattr(e, 'venue', None) or getattr(e, 'location', None),
        "event_type": getattr(e, 'event_type', 'general'),
        "is_rsvp_enabled": getattr(e, 'is_rsvp_enabled', None) if hasattr(e, 'is_rsvp_enabled') else getattr(e, 'registration_required', True),
        "max_attendees": getattr(e, 'max_attendees', None),
        "is_published": getattr(e, 'is_published', True),
        "banner_image": getattr(e, 'banner_image', None),
        "created_by": getattr(e, 'created_by', None),
        "created_at": str(e.created_at) if e.created_at else None,
        "rsvp_count": rsvp_count,
        "user_rsvpd": user_rsvpd,
    }

# ── Public / Member endpoints ──────────────────────────────────────────────

@router.get("")
def get_events(db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    events = db.query(Event).filter(
        Event.is_published == True
    ).order_by(Event.event_date.asc()).all()
    return [format_event(e, db, current_user.id) for e in events]

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return format_event(e, db, current_user.id)

@router.post("/{event_id}/rsvp")
def toggle_rsvp(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_approved_member)):
    e = db.query(Event).filter(Event.id == event_id, Event.is_published == True).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    if not getattr(e, 'is_rsvp_enabled', True):
        raise HTTPException(status_code=400, detail="RSVP not enabled for this event")
    try:
        from app.models.models import EventRegistration
        existing = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == current_user.id
        ).first()
        if existing:
            db.delete(existing)
            db.commit()
            return {"message": "RSVP cancelled", "rsvpd": False}
        else:
            max_att = getattr(e, 'max_attendees', None)
            if max_att:
                count = db.query(EventRegistration).filter(EventRegistration.event_id == event_id).count()
                if count >= max_att:
                    raise HTTPException(status_code=400, detail="Event is full")
            rsvp = EventRegistration(event_id=event_id, user_id=current_user.id, created_at=datetime.utcnow())
            db.add(rsvp)
            db.commit()
            return {"message": "RSVP confirmed", "rsvpd": True}
    except HTTPException:
        raise
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"RSVP error: {str(ex)}")

# ── Admin endpoints ────────────────────────────────────────────────────────

@router.get("/admin/all")
def admin_get_events(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    events = db.query(Event).order_by(Event.event_date.desc()).all()
    return [format_event(e, db) for e in events]

@router.post("/admin/create")
def create_event(data: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    event = Event(
        title=data.title,
        description=data.description,
        event_date=datetime.strptime(data.event_date, "%Y-%m-%d").date(),
        location=data.venue or data.location if hasattr(data, 'location') else data.venue,
        max_attendees=data.max_attendees,
        is_published=True,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    # Set optional columns if they exist on the model
    for col, val in [('event_time', data.event_time), ('event_type', data.event_type or 'general'), ('registration_required', data.is_rsvp_enabled), ('is_rsvp_enabled', data.is_rsvp_enabled)]:
        try:
            setattr(event, col, val)
        except:
            pass
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"message": "Event created!", "id": event.id}

@router.put("/admin/{event_id}")
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    field_map = {"venue": "location", "is_rsvp_enabled": "registration_required"}
    for key, value in data.dict(exclude_unset=True).items():
        if key == 'event_date' and value:
            value = datetime.strptime(value, "%Y-%m-%d").date()
        actual_key = field_map.get(key, key)
        if hasattr(event, actual_key):
            setattr(event, actual_key, value)
    event.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Event updated!"}

@router.delete("/admin/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted!"}

@router.get("/admin/{event_id}/attendees")
def get_attendees(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    try:
        from app.models.models import EventRegistration
        rsvps = db.query(EventRegistration).filter(EventRegistration.event_id == event_id).all()
        result = []
        for r in rsvps:
            member = db.query(Member).filter(Member.user_id == r.user_id).first()
            result.append({
                "user_id": r.user_id,
                "full_name": member.full_name if member else "Unknown",
                "department": getattr(member, 'department', None) if member else None,
                "phone": getattr(member, 'phone', None) if member else None,
                "rsvp_date": str(r.created_at),
            })
        return result
    except Exception as ex:
        return []
