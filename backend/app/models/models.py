from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    MEMBER = "member"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class RegistrationStatus(str, enum.Enum):
    PENDING = "pending"
    EMAIL_VERIFIED = "email_verified"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id                     = Column(Integer, primary_key=True, index=True)
    email                  = Column(String, unique=True, index=True, nullable=False)
    password_hash          = Column(String, nullable=False)
    role                   = Column(Enum(UserRole), default=UserRole.MEMBER)
    is_active              = Column(Boolean, default=True)
    registration_status    = Column(Enum(RegistrationStatus), default=RegistrationStatus.PENDING)
    email_verified         = Column(Boolean, default=False)
    email_verify_token     = Column(String, nullable=True)
    email_verify_expires   = Column(DateTime, nullable=True)
    reset_password_token   = Column(String, nullable=True)
    reset_password_expires = Column(DateTime, nullable=True)
    created_at             = Column(DateTime, server_default=func.now())
    updated_at             = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login             = Column(DateTime, nullable=True)

    member = relationship("Member", back_populates="user", uselist=False, foreign_keys="[Member.user_id]")


class Member(Base):
    __tablename__ = "members"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Personal info
    full_name         = Column(String, nullable=False)
    bangla_name       = Column(String, nullable=True)
    nick_name         = Column(String, nullable=True)
    batch_roll        = Column(String, nullable=True)
    department        = Column(String, nullable=True)
    session           = Column(String, nullable=True)
    student_id        = Column(String, nullable=True)
    date_of_birth     = Column(Date, nullable=True)

    # Contact
    phone             = Column(String, nullable=True)
    whatsapp          = Column(String, nullable=True)
    current_address   = Column(Text, nullable=True)
    permanent_address = Column(Text, nullable=True)
    current_location  = Column(String, nullable=True)
    hall              = Column(String, nullable=True)

    # Professional
    profession        = Column(String, nullable=True)
    organization      = Column(String, nullable=True)
    designation       = Column(String, nullable=True)
    linkedin          = Column(String, nullable=True)
    facebook          = Column(String, nullable=True)

    # Profile
    profile_photo     = Column(String, nullable=True)
    bio               = Column(Text, nullable=True)
    show_in_directory = Column(Boolean, default=True)
    show_phone        = Column(Boolean, default=False)
    show_email        = Column(Boolean, default=False)

    # Admin notes
    admin_notes       = Column(Text, nullable=True)
    approved_by       = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at       = Column(DateTime, nullable=True)
    rejected_reason   = Column(Text, nullable=True)

    created_at        = Column(DateTime, server_default=func.now())
    updated_at        = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="member", foreign_keys=[user_id])


class Event(Base):
    __tablename__ = "events"

    id                    = Column(Integer, primary_key=True, index=True)
    title                 = Column(String, nullable=False)
    description           = Column(Text, nullable=True)
    event_date            = Column(DateTime, nullable=False)
    location              = Column(String, nullable=True)
    image                 = Column(String, nullable=True)
    is_published          = Column(Boolean, default=True)
    registration_required = Column(Boolean, default=False)
    max_attendees         = Column(Integer, nullable=True)
    created_by            = Column(Integer, ForeignKey("users.id"))
    created_at            = Column(DateTime, server_default=func.now())
    updated_at            = Column(DateTime, server_default=func.now(), onupdate=func.now())

    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user"),)

    id            = Column(Integer, primary_key=True, index=True)
    event_id      = Column(Integer, ForeignKey("events.id"))
    user_id       = Column(Integer, ForeignKey("users.id"))
    registered_at = Column(DateTime, server_default=func.now())

    event = relationship("Event", back_populates="registrations")


class Memory(Base):
    __tablename__ = "memories"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, nullable=False)
    description  = Column(Text, nullable=True)
    image        = Column(String, nullable=True)
    year         = Column(Integer, nullable=True)
    category     = Column(String, nullable=True)
    is_approved  = Column(Boolean, default=False)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    approved_by  = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at   = Column(DateTime, server_default=func.now())
    updated_at   = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    is_pinned  = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    parent_id  = Column(Integer, ForeignKey("messages.id"), nullable=True)
    author_id  = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    replies   = relationship("Message", backref="parent", remote_side=[id])
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")


class MessageReaction(Base):
    __tablename__ = "message_reactions"
    __table_args__ = (UniqueConstraint("message_id", "user_id", name="uq_reaction_user"),)

    id         = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    user_id    = Column(Integer, ForeignKey("users.id"))
    reaction   = Column(String, default="like")
    created_at = Column(DateTime, server_default=func.now())

    message = relationship("Message", back_populates="reactions")


class SliderImage(Base):
    __tablename__ = "slider_images"

    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(String, nullable=True)
    subtitle      = Column(String, nullable=True)
    image         = Column(String, nullable=False)
    display_order = Column(Integer, default=0)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())


class Announcement(Base):
    __tablename__ = "announcements"

    id           = Column(Integer, primary_key=True, index=True)
    title        = Column(String, nullable=False)
    content      = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True)
    is_pinned    = Column(Boolean, default=False)
    created_by   = Column(Integer, ForeignKey("users.id"))
    created_at   = Column(DateTime, server_default=func.now())
    expires_at   = Column(DateTime, nullable=True)


class CommitteeMember(Base):
    __tablename__ = "committee_members"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    position      = Column(String, nullable=False)
    photo         = Column(String, nullable=True)
    email         = Column(String, nullable=True)
    phone         = Column(String, nullable=True)
    display_order = Column(Integer, default=0)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())


class SiteSetting(Base):
    __tablename__ = "site_settings"

    id         = Column(Integer, primary_key=True, index=True)
    key        = Column(String, unique=True, nullable=False)
    value      = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
