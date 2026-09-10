import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings, STATIC_DIR
from .database import engine, Base, SessionLocal
from .services.seed_data import seed_database
from .routers import auth, screenings, cases, reports, audit, stats, settings as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
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
    allow_origins=["*"],  # Permits dev frontend on any local port
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

@app.get("/")
def root():
    return {
        "service": "VERINEX AI-Based Identity & Document Screening API",
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "compliance": "Defensive Screening Prototype – Fictional Specimen Safe Testing",
        "endpoints": {
            "docs": "/docs",
            "stats": "/api/stats/dashboard",
            "samples": "/api/screenings/samples/list"
        }
    }
