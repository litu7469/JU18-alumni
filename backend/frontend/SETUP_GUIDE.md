# JU 18th Batch Alumni — Phase 2 & 3 Setup Guide

## What's Included

### Backend (FastAPI)
- ✅ 11 database tables (users, members, events, etc.)
- ✅ Authentication (register, login, JWT, email verify)
- ✅ Member management API
- ✅ Admin approval workflow
- ✅ Gmail SMTP email service
- ✅ File upload support
- ✅ Railway deployment ready

### Frontend Pages
- ✅ pages/register.html — 3-step registration form
- ✅ pages/login.html — Login with JWT
- ✅ pages/dashboard.html — Member portal with directory
- ✅ pages/pending.html — Awaiting approval screen
- ✅ admin/dashboard.html — Admin approval panel
- ✅ js/auth.js — Shared auth helper

---

## Local Setup

### Step 1 — Install Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Step 2 — Create Database
```sql
createdb ju18_alumni
```

### Step 3 — Configure .env
```bash
copy .env.example .env
notepad .env
```

Fill in:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost/ju18_alumni
SECRET_KEY=generate-a-long-random-string
GMAIL_USER=your-gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### Step 4 — Get Gmail App Password
1. Go to myaccount.google.com
2. Security → 2-Step Verification (enable if not)
3. Security → App Passwords
4. Create password for "Mail" → "Windows Computer"
5. Copy the 16-character password

### Step 5 — Run Migrations & Seed
```bash
alembic upgrade head
python seed_data.py
```

### Step 6 — Start Server
```bash
uvicorn main:app --reload --port 8000
```

Open: http://localhost:8000
API Docs: http://localhost:8000/api/docs
Admin Login: admin@ju18alumni.org / Admin@2026

---

## Railway Deployment

### Step 1 — Push to GitHub
```bash
cd JU18-Alumni-Website
git init
git add .
git commit -m "Phase 2 & 3 complete"
git remote add origin https://github.com/YOUR_USERNAME/ju18-alumni
git push -u origin main
```

### Step 2 — Create Railway Project
1. railway.app → New Project → GitHub repo
2. Root Directory: backend
3. Add PostgreSQL service

### Step 3 — Set Environment Variables
```
DATABASE_URL=postgresql://... (from Railway Postgres)
SECRET_KEY=your-strong-random-key
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
BASE_URL=https://your-app.up.railway.app
FRONTEND_URL=https://your-app.up.railway.app
ALLOWED_ORIGINS=https://your-app.up.railway.app
ENVIRONMENT=production
```

### Step 4 — Deploy
Railway auto-deploys. Start command runs:
```
alembic upgrade head && python seed_data.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Default Admin Account
- Email: admin@ju18alumni.org
- Password: Admin@2026
⚠️ Change password immediately after first login!

---

## API Endpoints

### Public
- GET /api/public/homepage — Homepage data
- GET /api/public/events — All events

### Auth
- POST /api/auth/register — Register
- GET /api/auth/verify-email?token=... — Verify email
- POST /api/auth/login — Login
- POST /api/auth/forgot-password — Forgot password
- POST /api/auth/reset-password — Reset password
- GET /api/auth/me — Get current user

### Members (requires login + approved)
- GET /api/members/profile — My profile
- PUT /api/members/profile — Update profile
- POST /api/members/profile/photo — Upload photo
- GET /api/members/directory — Member directory

### Admin (requires admin role)
- GET /api/admin/stats — Dashboard stats
- GET /api/admin/pending-members — Pending approvals
- POST /api/admin/approve-member — Approve/reject
- GET /api/admin/all-members — All members

---

## File Structure
```
backend/
├── main.py                    FastAPI app
├── requirements.txt
├── railway.json
├── alembic.ini
├── seed_data.py
├── alembic/
│   └── env.py
└── app/
    ├── core/
    │   ├── config.py          Settings
    │   ├── database.py        DB connection
    │   ├── security.py        JWT & passwords
    │   └── auth_middleware.py Auth dependencies
    ├── models/
    │   └── models.py          All SQLAlchemy models
    ├── schemas/
    │   └── schemas.py         Pydantic schemas
    ├── routes/
    │   ├── auth.py            Auth endpoints
    │   ├── members.py         Member endpoints
    │   ├── admin.py           Admin endpoints
    │   └── public.py          Public endpoints
    └── services/
        └── email_service.py   Gmail SMTP

frontend/
├── js/
│   └── auth.js               Auth helper (shared)
├── pages/
│   ├── register.html          3-step registration
│   ├── login.html             Login page
│   ├── dashboard.html         Member portal
│   └── pending.html           Awaiting approval
└── admin/
    └── dashboard.html         Admin panel
```
