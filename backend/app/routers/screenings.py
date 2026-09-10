import os
import uuid
import json
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import ScreeningCase, User
from ..schemas import ScreeningCaseOut, SampleDocumentItem
from ..config import UPLOADS_DIR, SAMPLES_DIR
from ..services.quality_service import analyze_document_quality
from ..services.ocr_service import extract_document_text
from ..services.risk_engine import evaluate_document_risk
from ..services.audit_service import log_audit_event
from .auth import get_current_user

router = APIRouter(prefix="/screenings", tags=["Document Screening"])

SAMPLE_PRESETS = [
    {
        "id": "CLEAN_PASSPORT",
        "title": "Fictional Passport (Clean / Valid)",
        "description": "Standard authentic-style passport with unexpired dates, consistent MRZ checksums, and high resolution.",
        "document_type": "PASSPORT",
        "expected_risk": "LOW",
        "image_url": "/static/samples/sample_passport_clean.png",
        "badge_label": "Standard Clean Pass"
    },
    {
        "id": "EXPIRED_LICENSE",
        "title": "Fictional Driver's License (Expired)",
        "description": "State driver's license with passed expiration date (2023). Demonstrates temporal integrity rule.",
        "document_type": "DRIVERS_LICENSE",
        "expected_risk": "MEDIUM",
        "image_url": "/static/samples/sample_license_expired.png",
        "badge_label": "Temporal Invalidation"
    },
    {
        "id": "TAMPERED_MRZ_ID",
        "title": "Fictional National ID (Tampered MRZ)",
        "description": "Identity card with mismatched visual name ('Marcus Reid') vs MRZ name ('Devon Jones'). Demonstrates cross-zone verification.",
        "document_type": "NATIONAL_ID",
        "expected_risk": "HIGH",
        "image_url": "/static/samples/sample_national_id_tampered.png",
        "badge_label": "Critical Tamper Flag"
    },
    {
        "id": "BLURRY_CARD",
        "title": "Fictional Residence Permit (Blurry / Glare)",
        "description": "Degraded image with optical blur and central specular glare. Demonstrates image forensic quality thresholds.",
        "document_type": "RESIDENCE_PERMIT",
        "expected_risk": "MEDIUM",
        "image_url": "/static/samples/sample_residence_blurry.png",
        "badge_label": "Low Optical Sharpness"
    }
]

@router.get("/samples/list", response_model=List[SampleDocumentItem])
def get_sample_document_presets():
    """Returns pre-configured fictional test specimens for zero-effort 1-click testing."""
    return SAMPLE_PRESETS

@router.get("", response_model=List[ScreeningCaseOut])
def list_screenings(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(ScreeningCase)
    if status and status != "ALL":
        query = query.filter(ScreeningCase.status == status)
    if risk_level and risk_level != "ALL":
        query = query.filter(ScreeningCase.overall_risk_level == risk_level)
    if doc_type and doc_type != "ALL":
        query = query.filter(ScreeningCase.document_type == doc_type)
    if search:
        query = query.filter(
            (ScreeningCase.id.ilike(f"%{search}%")) |
            (ScreeningCase.extracted_data_json.ilike(f"%{search}%")) |
            (ScreeningCase.file_name.ilike(f"%{search}%"))
        )
    
    cases = query.order_by(ScreeningCase.created_at.desc()).limit(limit).all()

    # Transform for schema
    results = []
    for c in cases:
        results.append(_format_case_out(c))
    return results

@router.get("/{case_id}", response_model=ScreeningCaseOut)
def get_screening_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return _format_case_out(case)

@router.post("/demo-sample", response_model=ScreeningCaseOut)
def run_screening_demo_sample(
    sample_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Runs instant AI screening on one of the pre-configured fictional test documents.
    """
    preset = next((p for p in SAMPLE_PRESETS if p["id"] == sample_id), None)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Invalid sample ID: {sample_id}")

    sample_filename = os.path.basename(preset["image_url"])
    file_path = str(SAMPLES_DIR / sample_filename)

    # 1. Quality Analysis
    quality_metrics = analyze_document_quality(file_path)

    # 2. OCR Extraction
    ocr_result = extract_document_text(
        file_path=file_path,
        document_type=preset["document_type"],
        mock_profile=preset["id"]
    )

    # 3. AI Risk Assessment
    risk_result = evaluate_document_risk(
        extracted_data=ocr_result["extracted_data"],
        quality_metrics=quality_metrics,
        ocr_confidence=ocr_result["ocr_confidence"],
        document_type=preset["document_type"]
    )

    # Generate new Case ID
    case_num = 8800 + db.query(ScreeningCase).count() + 1
    new_case_id = f"VNX-2026-{case_num}"
    now = datetime.utcnow()

    # Set initial status based on risk
    initial_status = "VERIFIED" if risk_result["overall_risk_level"] == "LOW" else "IN_REVIEW"
    if risk_result["overall_risk_level"] == "HIGH":
        initial_status = "FLAGGED"

    timeline = [
        {"step": "Uploaded", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Test document '{preset['title']}' loaded."},
        {"step": "Quality Inspection", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Image quality score: {quality_metrics['overall_quality_score']}%."},
        {"step": "OCR & Extraction", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Extracted structured fields with {ocr_result['ocr_confidence']}% confidence."},
        {"step": "AI Risk Assessment", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Risk Score {risk_result['risk_score']}/100 ({risk_result['overall_risk_level']} Risk)."},
        {"step": "Status Assigned", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "IN_PROGRESS" if initial_status == "IN_REVIEW" else "COMPLETED", "description": f"Assigned state: {initial_status}."}
    ]

    new_case = ScreeningCase(
        id=new_case_id,
        document_type=preset["document_type"],
        file_name=sample_filename,
        file_url=preset["image_url"],
        status=initial_status,
        overall_risk_level=risk_result["overall_risk_level"],
        risk_score=risk_result["risk_score"],
        ai_confidence=risk_result["ai_confidence"],
        document_quality_score=quality_metrics["overall_quality_score"],
        ocr_confidence=ocr_result["ocr_confidence"],
        extracted_data_json=json.dumps(ocr_result["extracted_data"]),
        consistency_checks_json=json.dumps(risk_result["consistency_checks"]),
        suspicious_indicators_json=json.dumps(risk_result["suspicious_indicators"]),
        timeline_json=json.dumps(timeline),
        created_at=now,
        updated_at=now
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # Log to Audit Trail
    severity = "CRITICAL" if risk_result["overall_risk_level"] == "HIGH" else ("WARNING" if risk_result["overall_risk_level"] == "MEDIUM" else "INFO")
    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="SCREENING_RUN",
        case_id=new_case_id,
        details=f"AI screening executed on {preset['title']}. Risk Level: {risk_result['overall_risk_level']} (Score: {risk_result['risk_score']}/100).",
        severity=severity
    )

    return _format_case_out(new_case)

@router.post("/upload", response_model=ScreeningCaseOut)
async def upload_and_screen_document(
    file: UploadFile = File(...),
    document_type: str = Form("PASSPORT"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a fictional test document file (PNG/JPG/PDF) and performs full AI screening pipeline.
    """
    # Validation of file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".pdf", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload JPG, PNG, or PDF.")

    # Save uploaded file
    file_uuid = uuid.uuid4().hex[:8]
    safe_filename = f"{file_uuid}_{file.filename.replace(' ', '_')}"
    dest_path = UPLOADS_DIR / safe_filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/static/uploads/{safe_filename}"

    # 1. Quality Analysis
    quality_metrics = analyze_document_quality(str(dest_path))

    # 2. OCR Extraction
    ocr_result = extract_document_text(
        file_path=str(dest_path),
        document_type=document_type
    )

    # 3. AI Risk Assessment
    risk_result = evaluate_document_risk(
        extracted_data=ocr_result["extracted_data"],
        quality_metrics=quality_metrics,
        ocr_confidence=ocr_result["ocr_confidence"],
        document_type=document_type
    )

    # Generate Case ID
    case_num = 8800 + db.query(ScreeningCase).count() + 1
    new_case_id = f"VNX-2026-{case_num}"
    now = datetime.utcnow()

    initial_status = "VERIFIED" if risk_result["overall_risk_level"] == "LOW" else "IN_REVIEW"
    if risk_result["overall_risk_level"] == "HIGH":
        initial_status = "FLAGGED"

    timeline = [
        {"step": "Uploaded", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"File '{file.filename}' uploaded by {current_user.full_name}."},
        {"step": "Quality Inspection", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Quality score: {quality_metrics['overall_quality_score']}%."},
        {"step": "OCR & Extraction", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"OCR Confidence: {ocr_result['ocr_confidence']}%."},
        {"step": "AI Risk Assessment", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "COMPLETED", "description": f"Calculated Risk: {risk_result['overall_risk_level']} ({risk_result['risk_score']}/100)."},
        {"step": "Case Enqueued", "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"), "status": "IN_PROGRESS", "description": f"Case assigned status '{initial_status}'."}
    ]

    new_case = ScreeningCase(
        id=new_case_id,
        document_type=document_type,
        file_name=file.filename,
        file_url=file_url,
        status=initial_status,
        overall_risk_level=risk_result["overall_risk_level"],
        risk_score=risk_result["risk_score"],
        ai_confidence=risk_result["ai_confidence"],
        document_quality_score=quality_metrics["overall_quality_score"],
        ocr_confidence=ocr_result["ocr_confidence"],
        extracted_data_json=json.dumps(ocr_result["extracted_data"]),
        consistency_checks_json=json.dumps(risk_result["consistency_checks"]),
        suspicious_indicators_json=json.dumps(risk_result["suspicious_indicators"]),
        timeline_json=json.dumps(timeline),
        created_at=now,
        updated_at=now
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # Log to Audit Log
    severity = "CRITICAL" if risk_result["overall_risk_level"] == "HIGH" else ("WARNING" if risk_result["overall_risk_level"] == "MEDIUM" else "INFO")
    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="DOCUMENT_UPLOAD",
        case_id=new_case_id,
        details=f"Uploaded and screened '{file.filename}'. Risk Level: {risk_result['overall_risk_level']} (Score: {risk_result['risk_score']}/100).",
        severity=severity
    )

    return _format_case_out(new_case)

def _format_case_out(c: ScreeningCase) -> dict:
    return {
        "id": c.id,
        "document_type": c.document_type,
        "file_name": c.file_name,
        "file_url": c.file_url,
        "status": c.status,
        "overall_risk_level": c.overall_risk_level,
        "risk_score": c.risk_score,
        "ai_confidence": c.ai_confidence,
        "document_quality_score": c.document_quality_score,
        "ocr_confidence": c.ocr_confidence,
        "extracted_data": c.get_extracted_data(),
        "consistency_checks": c.get_consistency_checks(),
        "suspicious_indicators": c.get_suspicious_indicators(),
        "timeline": c.get_timeline(),
        "reviewer_name": c.reviewer_name,
        "reviewer_decision": c.reviewer_decision,
        "reviewer_decision_at": c.reviewer_decision_at,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "notes": c.notes
    }
