import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.FROM_NAME} <{settings.GMAIL_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
            server.sendmail(settings.GMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False

def send_verification_email(to_email: str, name: str, token: str) -> bool:
    verify_url = f"{settings.BASE_URL}/api/auth/verify-email?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2>Hello, {name}!</h2>
            <p>Thank you for registering. Please verify your email address to continue.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}" style="background: #1a3a5c; color: white; padding: 15px 30px; 
                   text-decoration: none; border-radius: 5px; font-size: 16px;">
                   Verify Email Address
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">This link expires in 24 hours.</p>
            <p style="color: #666; font-size: 14px;">If you didn't register, ignore this email.</p>
        </div>
        <div style="background: #1a3a5c; padding: 15px; text-align: center;">
            <p style="color: #aaa; margin: 0; font-size: 12px;">
                Jahangirnagar University 18th Batch Alumni Association
            </p>
        </div>
    </div>
    """
    return send_email(to_email, "Verify Your Email — JU 18th Batch Alumni", html)

def send_approval_email(to_email: str, name: str) -> bool:
    login_url = f"{settings.FRONTEND_URL}/pages/login.html"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2>🎉 Welcome, {name}!</h2>
            <p>Your registration has been <strong>approved</strong> by the admin.</p>
            <p>You can now login and access the member portal.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{login_url}" style="background: #1a3a5c; color: white; padding: 15px 30px; 
                   text-decoration: none; border-radius: 5px; font-size: 16px;">
                   Login Now
                </a>
            </div>
        </div>
        <div style="background: #1a3a5c; padding: 15px; text-align: center;">
            <p style="color: #aaa; margin: 0; font-size: 12px;">
                Jahangirnagar University 18th Batch Alumni Association
            </p>
        </div>
    </div>
    """
    return send_email(to_email, "Registration Approved — JU 18th Batch Alumni", html)

def send_rejection_email(to_email: str, name: str, reason: str = "") -> bool:
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2>Hello, {name}</h2>
            <p>We regret to inform you that your registration could not be approved at this time.</p>
            {f'<p><strong>Reason:</strong> {reason}</p>' if reason else ''}
            <p>Please contact the admin for more information.</p>
        </div>
    </div>
    """
    return send_email(to_email, "Registration Update — JU 18th Batch Alumni", html)

def send_password_reset_email(to_email: str, name: str, token: str) -> bool:
    reset_url = f"{settings.FRONTEND_URL}/pages/reset-password.html?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2>Password Reset Request</h2>
            <p>Hello {name}, we received a request to reset your password.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background: #c0392b; color: white; padding: 15px 30px; 
                   text-decoration: none; border-radius: 5px; font-size: 16px;">
                   Reset Password
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">This link expires in 1 hour.</p>
            <p style="color: #666; font-size: 14px;">If you didn't request this, ignore this email.</p>
        </div>
    </div>
    """
    return send_email(to_email, "Password Reset — JU 18th Batch Alumni", html)
