import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
SAMPLES_DIR = STATIC_DIR / "samples"
UPLOADS_DIR = STATIC_DIR / "uploads"
ANALYSIS_DIR = STATIC_DIR / "analysis"
FACES_DIR = STATIC_DIR / "faces"
PREPROCESSED_DIR = STATIC_DIR / "preprocessed"
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
FACES_DIR.mkdir(parents=True, exist_ok=True)
PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "VERINEX – AI-Based Identity & Document Screening System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "verinex-super-secret-security-screening-token-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day for demo ease
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/verinex.db")
    
    # Sensitivity Thresholds (configurable via Settings API)
    RISK_LOW_MAX: int = 29
    RISK_MED_MAX: int = 69
    AUTO_FLAG_THRESHOLD: int = 70
    DOCUMENT_TYPE_CONFIDENCE_THRESHOLD: float = float(os.getenv("DOC_TYPE_CONFIDENCE_THRESHOLD", 75.0))

settings = Settings()
