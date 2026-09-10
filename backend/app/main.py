import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from sqlalchemy import text
from .config import settings, STATIC_DIR, FRONTEND_DIST_DIR
from .database import engine, Base, SessionLocal
from .services.seed_data import seed_database
from .routers import auth, screenings, cases, reports, audit, stats, settings as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Safe SQLite column migration for newly added fields
    with engine.connect() as conn:
        for col_def in [
            "mrz_result_json TEXT DEFAULT '{}'",
            "tampering_result_json TEXT DEFAULT '{}'",
            "face_result_json TEXT DEFAULT '{}'",
            "validation_result_json TEXT DEFAULT '{}'",
            "annotated_file_url VARCHAR(255)",
            "face_file_url VARCHAR(255)"
        ]:
            try:
                conn.execute(text(f"ALTER TABLE screening_cases ADD COLUMN {col_def}"))
                conn.commit()
            except Exception:
                pass

    # Run automatic seeding of fictional data and specimen images
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI-assisted identity and document screening defensive verification platform.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for document previews & generated sample images
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(screenings.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)
app.include_router(stats.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)

@app.get("/api/health")
def api_health():
    return {
        "service": "VERINEX AI-Based Identity & Document Screening API",
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "compliance": "Defensive Screening Prototype – Fictional Specimen Safe Testing"
    }

# Mount frontend production assets if dist exists
dist_assets = FRONTEND_DIST_DIR / "assets"
if dist_assets.exists():
    app.mount("/assets", StaticFiles(directory=str(dist_assets)), name="assets")

# Single Unified Route: Serves the React frontend SPA for root and all web pages
@app.get("/{full_path:path}")
async def serve_frontend_spa(full_path: str):
    # Check if a specific file was requested in dist root (e.g. favicon.svg, vite.svg)
    file_path = FRONTEND_DIST_DIR / full_path
    if full_path and file_path.is_file():
        return FileResponse(file_path)

    # Fallback to index.html for SPA routing
    index_file = FRONTEND_DIST_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend build not found. Please build the frontend.")
