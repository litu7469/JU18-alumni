from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from app.core.config import settings
from app.core.database import test_connection, Base, engine
import logging, os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JU 18th Batch Alumni API",
    description="Jahangirnagar University 18th Batch Alumni Association",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:8001,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Try multiple possible frontend paths (local vs Railway)
_possible_frontend_dirs = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend"),  # local: ../frontend
    "/app/../frontend",                                                                        # Railway: backend is /app
    os.path.join(os.getcwd(), "..", "frontend"),                                              # cwd/../frontend
    os.path.join(os.getcwd(), "frontend"),                                                    # cwd/frontend
    "/frontend",                                                                               # root /frontend
]
# Resolve symlinks and normalize
_possible_frontend_dirs = [os.path.normpath(d) for d in _possible_frontend_dirs]
FRONTEND_DIR = next((d for d in _possible_frontend_dirs if os.path.isdir(d)), None)
logger.info(f"CWD: {os.getcwd()}")
logger.info(f"__file__: {os.path.abspath(__file__)}")
logger.info(f"Frontend dir found: {FRONTEND_DIR}")
logger.info(f"Paths tried: {_possible_frontend_dirs}")
if FRONTEND_DIR and os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    assets_dir = os.path.join(FRONTEND_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    pages_dir = os.path.join(FRONTEND_DIR, "pages")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir), name="pages")
    admin_dir = os.path.join(FRONTEND_DIR, "admin")
    if os.path.exists(admin_dir):
        app.mount("/admin", StaticFiles(directory=admin_dir), name="admin_static")

from app.routes import auth, members, admin, public
app.include_router(auth.router,    prefix="/api/auth",    tags=["Auth"])
app.include_router(members.router, prefix="/api/members", tags=["Members"])
app.include_router(admin.router,   prefix="/api/admin",   tags=["Admin"])
app.include_router(public.router,  prefix="/api/public",  tags=["Public"])

@app.get("/health", tags=["System"])
def health_check():
    db_ok = test_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }

@app.get("/")
def serve_homepage():
    if FRONTEND_DIR:
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {"message": "JU 18th Batch Alumni API", "docs": "/api/docs", "frontend_dir": str(FRONTEND_DIR)}

@app.get("/index.html")
def serve_index():
    if FRONTEND_DIR:
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Not found"})

@app.get("/pages/{page_name}")
def serve_page(page_name: str):
    if FRONTEND_DIR:
        page_path = os.path.join(FRONTEND_DIR, "pages", page_name)
        if os.path.exists(page_path):
            return FileResponse(page_path)
    return JSONResponse(status_code=404, content={"detail": "Page not found"})

@app.get("/admin/{page_name}")
def serve_admin_page(page_name: str):
    if FRONTEND_DIR:
        page_path = os.path.join(FRONTEND_DIR, "admin", page_name)
        if os.path.exists(page_path):
            return FileResponse(page_path)
    return JSONResponse(status_code=404, content={"detail": "Page not found"})

@app.on_event("startup")
async def startup():
    logger.info("JU 18th Batch Alumni API starting...")
    logger.info("Database: OK" if test_connection() else "Database: FAILED")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})