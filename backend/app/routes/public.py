from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.core.database import get_db
from app.models.models import Event, SliderImage, Announcement, CommitteeMember, SiteSetting, Member, User, RegistrationStatus

router = APIRouter()


@router.get("/homepage")
def get_homepage_data(db: Session = Depends(get_db)):
    # Slider images
    sliders = db.query(SliderImage).filter(
        SliderImage.is_active == True
    ).order_by(SliderImage.display_order).all()

    # Latest 3 events — upcoming first, then recent past ones if fewer than 3 upcoming
    upcoming_events = db.query(Event).filter(
        Event.is_published == True,
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).limit(3).all()

    # If fewer than 3 upcoming, fill with most recent past events
    if len(upcoming_events) < 3:
        needed = 3 - len(upcoming_events)
        upcoming_ids = [e.id for e in upcoming_events]
        past_events = db.query(Event).filter(
            Event.is_published == True,
            Event.event_date < datetime.utcnow(),
            ~Event.id.in_(upcoming_ids) if upcoming_ids else True
        ).order_by(Event.event_date.desc()).limit(needed).all()
        events = upcoming_events + past_events
    else:
        events = upcoming_events

    # Announcements
    announcements = db.query(Announcement).filter(
        Announcement.is_published == True
    ).order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).limit(5).all()

    # Committee
    committee = db.query(CommitteeMember).filter(
        CommitteeMember.is_active == True
    ).order_by(CommitteeMember.display_order).all()

    # Stats
    total_members = db.query(User).filter(
        User.registration_status == RegistrationStatus.APPROVED
    ).count()

    # Site settings
    settings_list = db.query(SiteSetting).all()
    site_settings = {s.key: s.value for s in settings_list}

    return {
        "sliders": [
            {
                "id": s.id,
                "title": s.title,
                "subtitle": s.subtitle,
                "image": s.image
            } for s in sliders
        ],
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "event_date": str(e.event_date) if e.event_date else None,
                "location": e.location,
                "image": e.image,
                "is_upcoming": e.event_date >= datetime.utcnow().date() if e.event_date else False,
            } for e in events
        ],
        "announcements": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "is_pinned": a.is_pinned,
                "created_at": str(a.created_at)
            } for a in announcements
        ],
        "committee": [
            {
                "id": c.id,
                "name": c.name,
                "position": c.position,
                "photo": c.photo
            } for c in committee
        ],
        "stats": {
            "total_members": total_members
        },
        "settings": site_settings,
    }


@router.get("/events")
def get_public_events(db: Session = Depends(get_db)):
    events = db.query(Event).filter(
        Event.is_published == True
    ).order_by(Event.event_date.desc()).all()

    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "event_date": str(e.event_date) if e.event_date else None,
            "location": e.location,
            "image": e.image,
        } for e in events
    ]


@router.get("/events/{event_id}")
def get_public_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.is_published == True
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "event_date": str(event.event_date) if event.event_date else None,
        "location": event.location,
        "image": event.image,
        "registration_required": event.registration_required,
        "max_attendees": event.max_attendees,
    }
