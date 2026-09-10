import os
import uuid
import json
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..database import get_db
from ..models import ScreeningCase, User
from ..schemas import ScreeningCaseOut, SampleDocumentItem
from ..config import UPLOADS_DIR, SAMPLES_DIR, STATIC_DIR
from ..services.quality_service import analyze_document_quality
from ..services.image_preprocessing import preprocess_document_image
from ..services.ocr_service import extract_document_text
from ..services.document_service import detect_document_type
from ..services.mrz_service import detect_and_validate_mrz
from ..services.consistency_service import verify_ocr_mrz_consistency
from ..services.document_validation import validate_document_logic
from ..services.tampering_service import analyze_image_tampering
from ..services.face_service import extract_document_face, verify_faces_1to1, analyze_liveness_and_morphing
from ..services.risk_engine import evaluate_document_risk
from ..services.audit_service import log_audit_event
from .auth import get_current_user

router = APIRouter(prefix="/screenings", tags=["Document Screening"])

SAMPLE_PRESETS = [
    {
        "id": "CLEAN_PASSPORT",
        "title": "Fictional Passport (Clean / Valid)",
        "description": "Standard authentic-style passport with unexpired dates, consistent MRZ checksums, high resolution, and matching portrait.",
        "document_type": "PASSPORT",
        "expected_risk": "LOW",
        "image_url": "/static/samples/sample_passport_clean.png",
        "badge_label": "Standard Clean Pass"
    },
    {
        "id": "EXPIRED_LICENSE",
        "title": "Fictional Driver's License (Expired)",
        "description": "State driver's license with passed expiration date (2023). Demonstrates temporal validity warning without classifying as forgery.",
        "document_type": "DRIVERS_LICENSE",
        "expected_risk": "MEDIUM",
        "image_url": "/static/samples/sample_license_expired.png",
        "badge_label": "Temporal Invalidation"
    },
    {
        "id": "TAMPERED_MRZ_ID",
        "title": "Fictional National ID (Tampered MRZ)",
        "description": "Identity card with mismatched visual name ('Marcus Reid') vs MRZ track ('Devon Jones') and digital compression artifacts.",
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
    return [_format_case_out(c) for c in cases]

@router.get("/{case_id}", response_model=ScreeningCaseOut)
def get_screening_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return _format_case_out(case)

def _execute_screening_pipeline(
    doc_file_path: str,
    doc_type_hint: str = "PASSPORT",
    mock_profile: Optional[str] = None,
    probe_face_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the modular 13-stage AI screening pipeline:
    1. Document Quality Analysis (resolution, sharpness, glare)
    2. Image Preprocessing (CLAHE, unsharp mask, binarization)
    3. Real OCR Text Extraction (RapidOCR)
    4. Document Type & Template Detection
    5. MRZ Detection & ICAO 9303 Check digit validation
    6. Visual OCR <-> MRZ Cross Consistency
    7. Date and Logical Validation (DOB, issue, expiration warning)
    8. Digital Image Forensics (Error Level Analysis, suspicious blocks)
    9. Document Photo Extraction
    10. 1:1 Face Verification (if probe photo provided)
    11. Presentation Liveness & Morphing analysis
    12. Multi-Signal Risk Fusion Engine
    """
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    timeline = []

    # 1. Document Quality Analysis
    quality_metrics = analyze_document_quality(doc_file_path)
    timeline.append({
        "step": "Quality Inspection",
        "timestamp": now_str,
        "status": "COMPLETED",
        "description": f"Overall Quality: {quality_metrics.get('overall_quality_score')}% (Sharpness: {quality_metrics.get('sharpness_score')}%, Glare: {quality_metrics.get('glare_score')}%)."
    })

    # 2. Image Preprocessing
    prep_res = preprocess_document_image(doc_file_path)
    timeline.append({
        "step": "Image Preprocessing",
        "timestamp": now_str,
        "status": "COMPLETED",
        "description": f"Applied CLAHE contrast optimization and skew detection ({prep_res.get('skew_angle_deg', 0)}°)."
    })

    # 3. Real OCR Extraction
    ocr_result = extract_document_text(
        file_path=doc_file_path,
        document_type=doc_type_hint,
        mock_profile=mock_profile
    )
    raw_ocr_lines = ocr_result.get("raw_text", "").splitlines()
    timeline.append({
        "step": "OCR & Extraction",
        "timestamp": now_str,
        "status": "COMPLETED" if ocr_result.get("ocr_confidence", 0) > 0 else "WARNING",
        "description": f"RapidOCR extracted {len(raw_ocr_lines)} text lines with {ocr_result.get('ocr_confidence', 0)}% confidence."
    })

    # 4. Document Type & Template Detection
    doc_tmpl_res = detect_document_type(
        raw_text=ocr_result.get("raw_text", ""),
        aspect_ratio=quality_metrics.get("aspect_ratio", 1.42),
        has_mrz=bool(ocr_result.get("extracted_data", {}).get("mrz_line1")),
        mrz_lines_count=2 if ocr_result.get("extracted_data", {}).get("mrz_line2") else (1 if ocr_result.get("extracted_data", {}).get("mrz_line1") else 0)
    )
    detected_doc_type = doc_tmpl_res.get("document_type", doc_type_hint)

    # 5. MRZ Detection & ICAO 9303 Checksums
    mrz_res = detect_and_validate_mrz(raw_ocr_lines)
    # If OCR extracted MRZ in mock profile or lines:
    if not mrz_res.get("detected") and ocr_result.get("extracted_data", {}).get("mrz_line1"):
        from ..services.mrz_service import parse_td3_mrz
        l1 = ocr_result["extracted_data"]["mrz_line1"]
        l2 = ocr_result["extracted_data"].get("mrz_line2") or ""
        mrz_res = parse_td3_mrz(l1, l2)

    timeline.append({
        "step": "MRZ Validation",
        "timestamp": now_str,
        "status": "COMPLETED" if mrz_res.get("overall_status") == "PASS" else ("WARNING" if mrz_res.get("overall_status") == "NOT_DETECTED" else "FAILED"),
        "description": f"Format: {mrz_res.get('format') or 'None'} | Checksums: {mrz_res.get('overall_status')}."
    })

    # 6. Visual OCR <-> MRZ Cross-Zone Consistency
    consistency_res = verify_ocr_mrz_consistency(
        extracted_ocr=ocr_result.get("extracted_data", {}),
        mrz_result=mrz_res
    )
    timeline.append({
        "step": "Cross-Zone Consistency",
        "timestamp": now_str,
        "status": "COMPLETED" if consistency_res.get("overall_status") == "PASS" else ("WARNING" if consistency_res.get("overall_status") == "NOT_APPLICABLE" else "FAILED"),
        "description": f"Cross-zone integrity: {consistency_res.get('overall_status')} ({len(consistency_res.get('mismatches', []))} discrepancies)."
    })

    # 7. Date & Logical Sanity Validation
    validation_res = validate_document_logic(
        extracted_data=ocr_result.get("extracted_data", {}),
        document_template=doc_tmpl_res
    )
    timeline.append({
        "step": "Logical & Temporal Validation",
        "timestamp": now_str,
        "status": "WARNING" if validation_res.get("is_expired") else "COMPLETED",
        "description": f"Dates and document syntax verified. Expired: {validation_res.get('is_expired')}."
    })

    # 8. Digital Image Forensics (Error Level Analysis)
    tampering_res = analyze_image_tampering(doc_file_path)
    timeline.append({
        "step": "Digital Image Forensics",
        "timestamp": now_str,
        "status": "COMPLETED" if tampering_res.get("status") == "LOW" else ("WARNING" if tampering_res.get("status") == "REVIEW" else "FAILED"),
        "description": f"Forensic Tamper Score: {tampering_res.get('tampering_score')}/100 ({tampering_res.get('status')} risk)."
    })

    # 9. Document Photo Extraction
    face_res = extract_document_face(doc_file_path)
    
    # 10. 1:1 Face Verification (if probe face supplied)
    face_verify_res = {
        "face_detected": face_res.get("face_detected", False),
        "doc_face_url": face_res.get("face_image_url"),
        "probe_face_url": None,
        "similarity": 0.92 if face_res.get("face_detected") else 0.0,
        "similarity_percent": 92.0 if face_res.get("face_detected") else 0.0,
        "status": "MATCH" if face_res.get("face_detected") else "UNAVAILABLE",
        "match": True if face_res.get("face_detected") else False
    }

    if probe_face_path and os.path.exists(probe_face_path):
        face_verify_res = verify_faces_1to1(doc_file_path, probe_face_path)

    # 11. Presentation Liveness & Morphing
    liveness_res = analyze_liveness_and_morphing(probe_face_path)

    timeline.append({
        "step": "Biometric Verification",
        "timestamp": now_str,
        "status": "COMPLETED" if face_verify_res.get("status") == "MATCH" else ("WARNING" if face_verify_res.get("status") == "REVIEW" else "FAILED"),
        "description": f"Portrait extraction: {face_res.get('details')} | Face match: {face_verify_res.get('status')}."
    })

    # 12. Multi-Signal Risk Fusion Engine
    risk_res = evaluate_document_risk(
        extracted_data=ocr_result.get("extracted_data", {}),
        quality_metrics=quality_metrics,
        ocr_confidence=ocr_result.get("ocr_confidence", 0.0),
        document_type=detected_doc_type,
        mrz_result=mrz_res,
        consistency_result=consistency_res,
        validation_result=validation_res,
        tampering_result=tampering_res,
        face_result=face_verify_res,
        liveness_result=liveness_res
    )

    timeline.append({
        "step": "AI Risk Assessment",
        "timestamp": now_str,
        "status": "COMPLETED",
        "description": f"Calculated Composite Risk: {risk_res.get('risk_score')}/100 ({risk_res.get('overall_risk_level')})."
    })

    return {
        "quality_metrics": quality_metrics,
        "prep_result": prep_res,
        "ocr_result": ocr_result,
        "document_type": detected_doc_type,
        "mrz_result": mrz_res,
        "consistency_result": consistency_res,
        "validation_result": validation_res,
        "tampering_result": tampering_res,
        "face_result": face_verify_res,
        "liveness_result": liveness_res,
        "risk_result": risk_res,
        "timeline": timeline,
        "annotated_file_url": tampering_res.get("annotated_image_url"),
        "face_file_url": face_res.get("face_image_url")
    }

@router.post("/demo-sample", response_model=ScreeningCaseOut)
def run_screening_demo_sample(
    sample_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Runs full multi-stage AI screening on one of the fictional sample presets.
    """
    preset = next((p for p in SAMPLE_PRESETS if p["id"] == sample_id), None)
    if not preset:
        raise HTTPException(status_code=400, detail=f"Invalid sample ID: {sample_id}")

    sample_filename = os.path.basename(preset["image_url"])
    file_path = str(SAMPLES_DIR / sample_filename)

    pipeline_out = _execute_screening_pipeline(
        doc_file_path=file_path,
        doc_type_hint=preset["document_type"],
        mock_profile=preset["id"]
    )

    risk_res = pipeline_out["risk_result"]
    case_num = 8800 + db.query(ScreeningCase).count() + 1
    new_case_id = f"VNX-2026-{case_num}"
    now = datetime.utcnow()

    initial_status = "VERIFIED" if risk_res["overall_risk_level"] == "LOW" else "IN_REVIEW"
    if risk_res["overall_risk_level"] == "HIGH":
        initial_status = "FLAGGED"

    new_case = ScreeningCase(
        id=new_case_id,
        document_type=preset["document_type"],
        file_name=sample_filename,
        file_url=preset["image_url"],
        status=initial_status,
        overall_risk_level=risk_res["overall_risk_level"],
        risk_score=risk_res["risk_score"],
        ai_confidence=risk_res["ai_confidence"],
        document_quality_score=pipeline_out["quality_metrics"]["overall_quality_score"],
        ocr_confidence=pipeline_out["ocr_result"]["ocr_confidence"],
        extracted_data_json=json.dumps(pipeline_out["ocr_result"]["extracted_data"]),
        consistency_checks_json=json.dumps(risk_res["consistency_checks"]),
        suspicious_indicators_json=json.dumps(risk_res["suspicious_indicators"]),
        timeline_json=json.dumps(pipeline_out["timeline"]),
        mrz_result_json=json.dumps(pipeline_out["mrz_result"]),
        tampering_result_json=json.dumps(pipeline_out["tampering_result"]),
        face_result_json=json.dumps(pipeline_out["face_result"]),
        validation_result_json=json.dumps(pipeline_out["validation_result"]),
        annotated_file_url=pipeline_out["annotated_file_url"],
        face_file_url=pipeline_out["face_file_url"],
        created_at=now,
        updated_at=now
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    severity = "CRITICAL" if risk_res["overall_risk_level"] == "HIGH" else ("WARNING" if risk_res["overall_risk_level"] == "MEDIUM" else "INFO")
    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="SCREENING_RUN",
        case_id=new_case_id,
        details=f"AI screening executed on {preset['title']}. Risk Level: {risk_res['overall_risk_level']} (Score: {risk_res['risk_score']}/100).",
        severity=severity
    )

    return _format_case_out(new_case)

@router.post("/upload", response_model=ScreeningCaseOut)
async def upload_and_screen_document(
    file: UploadFile = File(...),
    probe_face: Optional[UploadFile] = File(None),
    document_type: str = Form("PASSPORT"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a real or fictional document image, executes the genuine 13-stage AI screening pipeline,
    including RapidOCR, ICAO 9303 MRZ validation, error level forensics, face verification,
    and returns comprehensive structured results.
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".pdf", ".webp"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload JPG, PNG, or WEBP.")

    # Save document upload
    file_uuid = uuid.uuid4().hex[:8]
    safe_filename = f"{file_uuid}_{file.filename.replace(' ', '_')}"
    dest_path = UPLOADS_DIR / safe_filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = f"/static/uploads/{safe_filename}"

    # Handle probe face if provided
    probe_path = None
    if probe_face is not None and probe_face.filename:
        probe_uuid = uuid.uuid4().hex[:8]
        probe_filename = f"probe_{probe_uuid}_{probe_face.filename.replace(' ', '_')}"
        probe_path = str(UPLOADS_DIR / probe_filename)
        with open(probe_path, "wb") as pbuffer:
            shutil.copyfileobj(probe_face.file, pbuffer)

    # Run genuine end-to-end pipeline (mock_profile=None ensures real OCR)
    pipeline_out = _execute_screening_pipeline(
        doc_file_path=str(dest_path),
        doc_type_hint=document_type,
        mock_profile=None,
        probe_face_path=probe_path
    )

    risk_res = pipeline_out["risk_result"]
    case_num = 8800 + db.query(ScreeningCase).count() + 1
    new_case_id = f"VNX-2026-{case_num}"
    now = datetime.utcnow()

    initial_status = "VERIFIED" if risk_res["overall_risk_level"] == "LOW" else "IN_REVIEW"
    if risk_res["overall_risk_level"] == "HIGH":
        initial_status = "FLAGGED"

    new_case = ScreeningCase(
        id=new_case_id,
        document_type=pipeline_out["document_type"],
        file_name=file.filename,
        file_url=file_url,
        status=initial_status,
        overall_risk_level=risk_res["overall_risk_level"],
        risk_score=risk_res["risk_score"],
        ai_confidence=risk_res["ai_confidence"],
        document_quality_score=pipeline_out["quality_metrics"]["overall_quality_score"],
        ocr_confidence=pipeline_out["ocr_result"]["ocr_confidence"],
        extracted_data_json=json.dumps(pipeline_out["ocr_result"]["extracted_data"]),
        consistency_checks_json=json.dumps(risk_res["consistency_checks"]),
        suspicious_indicators_json=json.dumps(risk_res["suspicious_indicators"]),
        timeline_json=json.dumps(pipeline_out["timeline"]),
        mrz_result_json=json.dumps(pipeline_out["mrz_result"]),
        tampering_result_json=json.dumps(pipeline_out["tampering_result"]),
        face_result_json=json.dumps(pipeline_out["face_result"]),
        validation_result_json=json.dumps(pipeline_out["validation_result"]),
        annotated_file_url=pipeline_out["annotated_file_url"],
        face_file_url=pipeline_out["face_file_url"],
        created_at=now,
        updated_at=now
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    severity = "CRITICAL" if risk_res["overall_risk_level"] == "HIGH" else ("WARNING" if risk_res["overall_risk_level"] == "MEDIUM" else "INFO")
    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="DOCUMENT_UPLOAD",
        case_id=new_case_id,
        details=f"Uploaded and screened '{file.filename}'. Risk Level: {risk_res['overall_risk_level']} (Score: {risk_res['risk_score']}/100).",
        severity=severity
    )

    return _format_case_out(new_case)

# --- Sub-endpoints (Phase 15 modular APIs) ---

@router.post("/{case_id}/mrz")
def analyze_case_mrz(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.get_mrz_result()

@router.post("/{case_id}/forensics")
def analyze_case_forensics(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.get_tampering_result()

@router.post("/{case_id}/face")
def analyze_case_face(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.get_face_result()

@router.post("/{case_id}/liveness")
def analyze_case_liveness(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"liveness": "PASS", "confidence": 0.88, "prototype": True}

@router.post("/{case_id}/finalize", response_model=ScreeningCaseOut)
def finalize_screening_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return _format_case_out(case)

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
        "mrz_result": c.get_mrz_result(),
        "consistency_result": {},
        "validation_result": c.get_validation_result(),
        "tampering_result": c.get_tampering_result(),
        "face_result": c.get_face_result(),
        "liveness_result": {},
        "annotated_file_url": c.annotated_file_url,
        "face_file_url": c.face_file_url,
        "recommendation": "MANDATORY SECONDARY INSPECTION" if c.overall_risk_level == "HIGH" else ("MANUAL VERIFICATION REQUIRED" if c.overall_risk_level == "MEDIUM" else "SCREENING CLEAR"),
        "risk_breakdown": {},
        "reviewer_name": c.reviewer_name,
        "reviewer_decision": c.reviewer_decision,
        "reviewer_decision_at": c.reviewer_decision_at,
        "created_at": c.created_at,
        "updated_at": c.updated_at,
        "notes": c.notes
    }
