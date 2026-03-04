"""
Seed initial data for JU 18th Batch Alumni website.
Run: python seed_data.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.models import User, Member, UserRole, RegistrationStatus, SiteSetting, CommitteeMember, SliderImage
from datetime import datetime

def seed():
    db = SessionLocal()
    print("=" * 50)
    print("JU 18th Batch Alumni — Database Seeder")
    print("=" * 50)

    # ── Super Admin ───────────────────────────────────────────
    print("\n👤 Creating super admin...")
    if not db.query(User).filter(User.email == "admin@ju18alumni.org").first():
        admin = User(
            email="admin@ju18alumni.org",
            password_hash=hash_password("Admin@2026"),
            role=UserRole.SUPER_ADMIN,
            email_verified=True,
            registration_status=RegistrationStatus.APPROVED,
            is_active=True,
        )
        db.add(admin)
        db.flush()
        member = Member(
            user_id=admin.id,
            full_name="System Administrator",
            department="Administration",
        )
        db.add(member)
        print("   ✅ Super admin created: admin@ju18alumni.org / Admin@2026")
    else:
        print("   — Skipped (exists): admin@ju18alumni.org")

    # ── Site Settings ─────────────────────────────────────────
    print("\n⚙️  Seeding site settings...")
    default_settings = {
        "site_title": "JU 18th Batch Alumni Association",
        "site_subtitle": "জাহাঙ্গীরনগর বিশ্ববিদ্যালয় ১৮তম ব্যাচ",
        "presidents_message": "Dear fellow alumni, it is my great pleasure to welcome you to our alumni association portal. Together we can build a stronger network and support each other in our professional journeys.",
        "presidents_name": "President Name",
        "presidents_designation": "President, JU 18th Batch Alumni Association",
        "contact_email": "info@ju18alumni.org",
        "contact_phone": "+880-XXX-XXXXXXX",
        "facebook_page": "",
        "vision": "To build a strong and connected alumni network that fosters lifelong friendships, professional collaboration, and mutual support among Jahangirnagar University 18th batch graduates.",
        "mission": "To organize regular reunions and events, facilitate professional networking, support current students, and preserve the memories and legacy of our batch.",
    }
    for key, value in default_settings.items():
        if not db.query(SiteSetting).filter(SiteSetting.key == key).first():
            db.add(SiteSetting(key=key, value=value))
            print(f"   ✅ Added: {key}")
        else:
            print(f"   — Skipped: {key}")

    # ── Committee Members ─────────────────────────────────────
    print("\n🏛️  Seeding committee...")
    committee = [
        {"name": "Member Name", "position": "President", "order": 1},
        {"name": "Member Name", "position": "General Secretary", "order": 2},
        {"name": "Member Name", "position": "Treasurer", "order": 3},
        {"name": "Member Name", "position": "Joint Secretary", "order": 4},
    ]
    if db.query(CommitteeMember).count() == 0:
        for c in committee:
            db.add(CommitteeMember(**c))
        print(f"   ✅ Added {len(committee)} committee members")
    else:
        print("   — Skipped (already exists)")

    # ── Slider Placeholders ───────────────────────────────────
    print("\n🖼️  Seeding slider placeholders...")
    if db.query(SliderImage).count() == 0:
        sliders = [
            {"title": "Welcome to JU 18th Batch", "subtitle": "Connecting Alumni Across the World", "image": "/assets/images/slider/slide1.jpg", "order": 1},
            {"title": "Reunion 2024", "subtitle": "Memories That Last Forever", "image": "/assets/images/slider/slide2.jpg", "order": 2},
            {"title": "Our Network", "subtitle": "400+ Alumni Strong", "image": "/assets/images/slider/slide3.jpg", "order": 3},
        ]
        for s in sliders:
            db.add(SliderImage(**s))
        print(f"   ✅ Added {len(sliders)} slider images")
    else:
        print("   — Skipped (already exists)")

    db.commit()
    print("\n" + "=" * 50)
    print("✅ Seeding complete!")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Change admin password after first login!")
    print("   Email: admin@ju18alumni.org")
    print("   Password: Admin@2026")
    db.close()

if __name__ == "__main__":
    seed()
