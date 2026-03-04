from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, generate_token, decode_token
from app.core.auth_middleware import get_current_user
from app.models.models import User, Member, UserRole, RegistrationStatus
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
from app.services.email_service import send_verification_email, send_password_reset_email
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    verify_token = generate_token()
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        email_verify_token=verify_token,
        email_verify_expires=datetime.utcnow() + timedelta(hours=24),
        registration_status=RegistrationStatus.PENDING
    )
    db.add(user)
    db.flush()

    # Create member profile
    member = Member(
        user_id=user.id,
        full_name=data.full_name,
        bangla_name=data.bangla_name,
        batch_roll=data.batch_roll,
        department=data.department,
        session=data.session,
        phone=data.phone,
        profession=data.profession,
        organization=data.organization,
    )
    db.add(member)
    db.commit()

    # Send verification email
    send_verification_email(data.email, data.full_name, verify_token)

    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "email": data.email
    }

@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email_verify_token == token,
        User.email_verify_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    user.email_verified = True
    user.email_verify_token = None
    user.email_verify_expires = None
    user.registration_status = RegistrationStatus.EMAIL_VERIFIED
    db.commit()

    # Redirect to frontend
    from fastapi.responses import RedirectResponse
    from app.core.config import settings
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/pages/login.html?verified=true")

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.email_verified:
        raise HTTPException(status_code=401, detail="Please verify your email first")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

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
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        token = generate_token()
        user.reset_password_token = token
        user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        member = user.member
        name = member.full_name if member else "Alumni"
        send_password_reset_email(data.email, name, token)

    return {"message": "If your email is registered, you will receive a reset link shortly."}

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.reset_password_token == data.token,
        User.reset_password_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    user.password_hash = hash_password(data.new_password)
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()

    return {"message": "Password reset successful. You can now login."}

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

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
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        access_token = create_access_token({"sub": user.id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
