from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from app.core.config import settings
from app.core.database import test_connection, Base, engine
import logging
import os

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ── Create tables ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI App ───────────────────────────────────────────────
app = FastAPI(
    title="JU 18th Batch Alumni API",
    description="Jahangirnagar University 18th Batch Alumni Association",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files ──────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
os.makedirs("../frontend", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Routers ───────────────────────────────────────────────────
from app.routes import auth, members, admin, public
app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(members.router, prefix="/api/members", tags=["Members"])
app.include_router(admin.router,   prefix="/api/admin",   tags=["Admin"])
app.include_router(public.router,  prefix="/api/public",  tags=["Public"])

# ── Health check ──────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    db_ok = test_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }

# ── Serve frontend ────────────────────────────────────────────
@app.get("/")
def serve_homepage():
    frontend_path = "../frontend/index.html"
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "JU 18th Batch Alumni API", "docs": "/api/docs"}

# ── Startup ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("JU 18th Batch Alumni API starting...")
    if test_connection():
        logger.info("Database: OK")
    else:
        logger.error("Database: FAILED")

# ── Exception handler ─────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
