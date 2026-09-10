from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..database import get_db
from ..models import ScreeningCase, AuditLog
from .screenings import _format_case_out

router = APIRouter(prefix="/stats", tags=["Analytics & Dashboard Stats"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    cases = db.query(ScreeningCase).all()
    total = len(cases)
    verified = sum(1 for c in cases if c.status == "VERIFIED")
    suspicious = sum(1 for c in cases if c.status in ["FLAGGED", "REJECTED"] or c.overall_risk_level == "HIGH")
    pending = sum(1 for c in cases if c.status == "IN_REVIEW")

    # Verification rate
    decided = sum(1 for c in cases if c.status in ["VERIFIED", "FLAGGED", "REJECTED"])
    verification_rate = round((verified / max(1, decided)) * 100, 1)

    # Risk distribution
    low_count = sum(1 for c in cases if c.overall_risk_level == "LOW")
    med_count = sum(1 for c in cases if c.overall_risk_level == "MEDIUM")
    high_count = sum(1 for c in cases if c.overall_risk_level == "HIGH")

    # Document type distribution
    doc_types = {}
    for c in cases:
        dt = c.document_type
        doc_types[dt] = doc_types.get(dt, 0) + 1

    # Simulated screening activity timeline (last 7 days / weekly distribution)
    now = datetime.utcnow()
    activity_chart = [
        {"day": (now - timedelta(days=6)).strftime("%b %d"), "verified": 8, "suspicious": 1, "pending": 2},
        {"day": (now - timedelta(days=5)).strftime("%b %d"), "verified": 12, "suspicious": 2, "pending": 3},
        {"day": (now - timedelta(days=4)).strftime("%b %d"), "verified": 15, "suspicious": 3, "pending": 1},
        {"day": (now - timedelta(days=3)).strftime("%b %d"), "verified": 11, "suspicious": 2, "pending": 4},
        {"day": (now - timedelta(days=2)).strftime("%b %d"), "verified": 19, "suspicious": 4, "pending": 2},
        {"day": (now - timedelta(days=1)).strftime("%b %d"), "verified": 14, "suspicious": 1, "pending": 3},
        {"day": now.strftime("%b %d"), "verified": verified, "suspicious": suspicious, "pending": pending},
    ]

    # Recent 6 cases for preview table
    recent_cases = db.query(ScreeningCase).order_by(ScreeningCase.created_at.desc()).limit(6).all()

    return {
        "metrics": {
            "total_screenings": total,
            "verified_documents": verified,
            "suspicious_documents": suspicious,
            "pending_reviews": pending,
            "verification_rate": verification_rate,
            "avg_processing_time_sec": 2.4
        },
        "risk_distribution": {
            "LOW": low_count,
            "MEDIUM": med_count,
            "HIGH": high_count
        },
        "document_type_distribution": doc_types,
        "activity_chart": activity_chart,
        "recent_screenings": [_format_case_out(c) for c in recent_cases]
    }
