from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, generate_token, decode_token
from app.core.auth_middleware import get_current_user
from app.models.models import User, Member, UserRole, RegistrationStatus
from app.schemas.schemas import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.services.email_service import send_password_reset_email
from pydantic import BaseModel, EmailStr
from typing import Optional
from jose import JWTError
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    department: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Normalize email to lowercase
    email = data.email.strip().lower()

    # Check duplicate in users table
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Admin email cannot register as member
    if email == "admin@ju18alumni.org":
        raise HTTPException(status_code=400, detail="This email cannot be used for registration")

    # Validate required fields
    if not data.full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required")
    if not data.phone.strip():
        raise HTTPException(status_code=400, detail="Phone number is required")
    if not data.department.strip():
        raise HTTPException(status_code=400, detail="Department is required")

    try:
        user = User(
            email=email,
            password_hash=hash_password("PLACEHOLDER_NOT_USABLE"),
            role=UserRole.MEMBER,
            email_verified=True,
            registration_status=RegistrationStatus.EMAIL_VERIFIED,
            is_active=True,
        )
        db.add(user)
        db.flush()  # get user.id without committing

        member = Member(
            user_id=user.id,
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),
            department=data.department.strip(),
        )
        db.add(member)
        db.commit()
        logger.info(f"New registration: {email}")

    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed for {email}: {e}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

    return {
        "message": "Registration submitted! Awaiting admin approval.",
        "email": email
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    # Generic message to prevent email enumeration
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled. Contact admin.")
    if user.registration_status == RegistrationStatus.REJECTED:
        raise HTTPException(status_code=401, detail="Your registration was not approved.")
    if user.registration_status != RegistrationStatus.APPROVED and user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=401, detail="Your account is pending admin approval.")

    # Check if password has been set (not placeholder)
    if not verify_password("PLACEHOLDER_NOT_USABLE", user.password_hash) is False:
        # Double-check: if password is still placeholder
        if verify_password("PLACEHOLDER_NOT_USABLE", user.password_hash):
            raise HTTPException(status_code=401, detail="Please set your password using the link sent to your email.")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    member = user.member

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "registration_status": user.registration_status,
            "full_name": member.full_name if member else "",
            "profile_photo": member.profile_photo if member else None,
        }
    )


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user and user.registration_status == RegistrationStatus.APPROVED:
        token = generate_token()
        user.reset_password_token = token
        user.reset_password_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        db.commit()
        member = user.member
        name = member.full_name if member else "Alumni"
        background_tasks.add_task(send_password_reset_email, email, name, token)
    # Always return same message (security)
    return {"message": "If your email is registered and approved, you will receive a reset link shortly."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.reset_password_token == data.token,
        User.reset_password_expires > datetime.now(timezone.utc)
    ).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired link. Please request a new one.")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    user.password_hash = hash_password(data.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()
    logger.info(f"Password set for user {user.id}")
    return {"message": "Password set successfully. You can now login."}


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    member = current_user.member
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "registration_status": current_user.registration_status,
        "email_verified": current_user.email_verified,
        "full_name": member.full_name if member else "",
        "profile_photo": member.profile_photo if member else None,
        "department": member.department if member else None,
    }


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or disabled")
        access_token = create_access_token({"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
