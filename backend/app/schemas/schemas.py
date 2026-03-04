from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.models import UserRole, RegistrationStatus

# ── Auth Schemas ──────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    bangla_name: Optional[str] = None
    batch_roll: Optional[str] = None
    department: Optional[str] = None
    session: Optional[str] = None
    phone: Optional[str] = None
    profession: Optional[str] = None
    organization: Optional[str] = None

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# ── Member Schemas ──────────────────────────────────────────
class MemberProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bangla_name: Optional[str] = None
    batch_roll: Optional[str] = None
    department: Optional[str] = None
    session: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    profession: Optional[str] = None
    organization: Optional[str] = None
    designation: Optional[str] = None
    linkedin: Optional[str] = None
    facebook: Optional[str] = None
    bio: Optional[str] = None
    show_in_directory: Optional[bool] = None
    show_phone: Optional[bool] = None
    show_email: Optional[bool] = None

class MemberResponse(BaseModel):
    id: int
    full_name: str
    bangla_name: Optional[str]
    batch_roll: Optional[str]
    department: Optional[str]
    session: Optional[str]
    profession: Optional[str]
    organization: Optional[str]
    designation: Optional[str]
    profile_photo: Optional[str]
    bio: Optional[str]
    linkedin: Optional[str]
    facebook: Optional[str]
    show_phone: bool
    show_email: bool
    phone: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

# ── Event Schemas ──────────────────────────────────────────
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    registration_required: bool = False
    max_attendees: Optional[int] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_date: datetime
    location: Optional[str]
    image: Optional[str]
    is_published: bool
    registration_required: bool
    max_attendees: Optional[int]
    created_at: datetime
    attendee_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ── Admin Schemas ──────────────────────────────────────────
class AdminApproveRequest(BaseModel):
    user_id: int
    action: str  # "approve" or "reject"
    reason: Optional[str] = None

class PendingMemberResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    department: Optional[str]
    session: Optional[str]
    phone: Optional[str]
    profession: Optional[str]
    registration_status: str
    created_at: datetime

    class Config:
        from_attributes = True
