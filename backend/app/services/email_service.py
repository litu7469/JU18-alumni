import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    try:
        api_key = settings.BREVO_API_KEY if hasattr(settings, 'BREVO_API_KEY') else None
        import os
        api_key = api_key or os.getenv("BREVO_API_KEY", "")

        if not api_key:
            logger.error("BREVO_API_KEY not set")
            return False

        response = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": api_key,
                "content-type": "application/json",
            },
            json={
                "sender": {
                    "name": settings.FROM_NAME or "JU 18th Batch Alumni",
                    "email": settings.GMAIL_USER or to_email,
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_body,
            },
            timeout=15,
        )
        if response.status_code in [200, 201]:
            logger.info(f"Email sent to {to_email}")
            return True
        else:
            logger.error(f"Brevo error: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


def send_set_password_email(to_email: str, name: str, token: str) -> bool:
    set_url = f"{settings.FRONTEND_URL}/pages/set-password.html?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
            <p style="color: #c9a84c; margin: 8px 0 0;">Alumni Association Portal</p>
        </div>
        <div style="padding: 36px 30px; background: #f9f9f9;">
            <h2 style="color: #1a3a5c;">🎉 Welcome, {name}!</h2>
            <p style="color: #555; line-height: 1.7;">Your registration has been <strong>approved</strong> by the admin. You are now a member of the JU 18th Batch Alumni network!</p>
            <p style="color: #555; line-height: 1.7;">Please click the button below to <strong>set your password</strong> and access the alumni portal.</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{set_url}" style="background: #1a3a5c; color: white; padding: 15px 36px; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                    Set My Password &amp; Login
                </a>
            </div>
            <p style="color: #888; font-size: 13px;">This link expires in <strong>24 hours</strong>.</p>
        </div>
        <div style="background: #1a3a5c; padding: 16px; text-align: center;">
            <p style="color: #aaa; margin: 0; font-size: 12px;">Jahangirnagar University 18th Batch Alumni Association</p>
        </div>
    </div>
    """
    return send_email(to_email, "🎉 Registration Approved — Set Your Password", html)


def send_rejection_email(to_email: str, name: str, reason: str = "") -> bool:
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <h2 style="color: #c0392b;">Registration Update</h2>
            <p style="color: #555; line-height: 1.7;">Dear {name},</p>
            <p style="color: #555; line-height: 1.7;">We regret to inform you that your registration could not be approved at this time.</p>
            {f'<p style="color: #555;"><strong>Reason:</strong> {reason}</p>' if reason else ''}
            <p style="color: #555;">Please contact the admin for more information.</p>
        </div>
        <div style="background: #1a3a5c; padding: 16px; text-align: center;">
            <p style="color: #aaa; margin: 0; font-size: 12px;">Jahangirnagar University 18th Batch Alumni Association</p>
        </div>
    </div>
    """
    return send_email(to_email, "Registration Status Update", html)


def send_password_reset_email(to_email: str, name: str, token: str) -> bool:
    reset_url = f"{settings.FRONTEND_URL}/pages/forgot-password.html?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #1a3a5c; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">JU 18th Batch Alumni</h1>
        </div>
        <div style="padding: 36px 30px; background: #f9f9f9;">
            <h2 style="color: #1a3a5c;">🔑 Password Reset Request</h2>
            <p style="color: #555; line-height: 1.7;">Dear {name},</p>
            <p style="color: #555; line-height: 1.7;">Click the button below to reset your password. This link expires in <strong>24 hours</strong>.</p>
            <div style="text-align: center; margin: 32px 0;">
                <a href="{reset_url}" style="background: #1a3a5c; color: white; padding: 15px 36px; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                    Reset My Password
                </a>
            </div>
            <p style="color: #888; font-size: 13px;">If you did not request this, please ignore this email.</p>
        </div>
        <div style="background: #1a3a5c; padding: 16px; text-align: center;">
            <p style="color: #aaa; margin: 0; font-size: 12px;">Jahangirnagar University 18th Batch Alumni Association</p>
        </div>
    </div>
    """
    return send_email(to_email, "🔑 Password Reset — JU 18th Batch Alumni", html)
