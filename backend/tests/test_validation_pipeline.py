import pytest
from pathlib import Path
from backend.app.routers.screenings import _execute_screening_pipeline, _format_case_out
from backend.app.models import ScreeningCase
from backend.app.config import SAMPLES_DIR

def test_pipeline_matching_passport():
    doc_path = str(SAMPLES_DIR / "sample_passport_clean.png")
    out = _execute_screening_pipeline(doc_path, doc_type_hint="PASSPORT")
    
    assert out["is_mismatched"] is False
    assert out["document_type"] == "PASSPORT"
    assert out["classification_result"]["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert out["classification_result"]["is_match"] is True
    assert out["risk_result"]["overall_risk_level"] == "LOW"
    # Verify timeline has Document Type Classification step
    timeline_steps = [t["step"] for t in out["timeline"]]
    assert "Document Type Classification" in timeline_steps
    assert "Document Type Match" in timeline_steps

def test_pipeline_signature_mismatch_halts():
    doc_path = str(SAMPLES_DIR / "sample_signature.png")
    out = _execute_screening_pipeline(doc_path, doc_type_hint="PASSPORT")
    
    # Must halt pipeline immediately and mark as mismatched
    assert out["is_mismatched"] is True
    assert out["classification_result"]["validation_status"] in ["DOCUMENT_TYPE_MISMATCH", "UNKNOWN_DOCUMENT"]
    assert out["risk_result"]["overall_risk_level"] == "HIGH"
    assert out["risk_result"]["risk_score"] >= 80
    assert out["ocr_result"]["ocr_confidence"] == 0.0  # Pipeline halted before OCR
    # Timeline must record halted status
    timeline_steps = [t["step"] for t in out["timeline"]]
    assert "Verification Pipeline Halted" in timeline_steps
    # Must contain mismatch indicator
    indicators = [i["title"] for i in out["risk_result"]["suspicious_indicators"]]
    assert any("Document Type Mismatch" in ind for ind in indicators)

def test_pipeline_aadhaar_when_passport_selected_halts():
    doc_path = str(SAMPLES_DIR / "sample_aadhaar.png")
    out = _execute_screening_pipeline(doc_path, doc_type_hint="PASSPORT")
    
    assert out["is_mismatched"] is True
    assert out["classification_result"]["detected_document_type"] == "AADHAAR"
    assert out["classification_result"]["validation_status"] == "DOCUMENT_TYPE_MISMATCH"
    assert out["risk_result"]["overall_risk_level"] == "HIGH"

def test_pipeline_blank_paper_when_passport_selected_halts():
    doc_path = str(SAMPLES_DIR / "sample_blank.png")
    out = _execute_screening_pipeline(doc_path, doc_type_hint="PASSPORT")
    
    assert out["is_mismatched"] is True
    assert out["classification_result"]["validation_status"] in ["UNKNOWN_DOCUMENT", "INVALID_INPUT", "DOCUMENT_TYPE_MISMATCH"]
    assert out["risk_result"]["overall_risk_level"] == "HIGH"

def test_format_case_out_includes_classification():
    case = ScreeningCase(
        id="VNX-2026-TEST",
        document_type="PASSPORT",
        selected_document_type="PASSPORT",
        file_name="test.png",
        file_url="/static/test.png",
        status="VERIFIED",
        overall_risk_level="LOW",
        risk_score=15,
        ai_confidence=95.0,
        document_quality_score=90.0,
        ocr_confidence=92.0,
        classification_result_json='{"validation_status": "DOCUMENT_TYPE_CONFIRMED", "classification_confidence": 96.0}'
    )
    formatted = _format_case_out(case)
    assert formatted["selected_document_type"] == "PASSPORT"
    assert formatted["classification_result"]["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert formatted["classification_result"]["classification_confidence"] == 96.0
