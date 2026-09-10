import pytest
from backend.app.services.risk_engine import evaluate_document_risk

def test_risk_clean_document():
    quality = {"overall_score": 92.0}
    ocr = {"ocr_confidence": 95.0, "extracted_data": {"full_name": "CLARA ABERNATHY"}}
    mrz = {"detected": True, "valid_structure": True, "overall_status": "PASS"}
    consistency = {"overall_status": "PASS", "mismatches": []}
    tampering = {"tampering_score": 5.0, "status": "LOW", "indicators": []}
    doc_val = {"status": "VALID", "checks": []}
    face = {"face_detected": True, "match": True, "status": "MATCH"}

    res = evaluate_document_risk(
        extracted_data=ocr["extracted_data"],
        quality_metrics=quality,
        ocr_confidence=ocr["ocr_confidence"],
        document_type="PASSPORT",
        mrz_result=mrz,
        consistency_result=consistency,
        validation_result=doc_val,
        tampering_result=tampering,
        face_result=face
    )
    assert res["risk_level"] == "LOW"
    assert res["risk_score"] < 30
    assert "CLEAR" in res["recommendation"]

def test_risk_mrz_tampered_document():
    quality = {"overall_score": 90.0}
    ocr = {"ocr_confidence": 92.0, "extracted_data": {"full_name": "MARCUS REID"}}
    mrz = {"detected": True, "valid_structure": True, "overall_status": "PASS"}
    consistency = {
        "overall_status": "FAIL",
        "mismatches": ["Name mismatch: visual 'MARCUS REID' vs MRZ 'DEVON JONES'"]
    }
    tampering = {
        "tampering_score": 45.0,
        "status": "REVIEW",
        "indicators": ["Compression disparity detected in portrait region"]
    }
    doc_val = {"status": "VALID", "checks": []}
    face = None

    res = evaluate_document_risk(
        extracted_data=ocr["extracted_data"],
        quality_metrics=quality,
        ocr_confidence=ocr["ocr_confidence"],
        document_type="PASSPORT",
        mrz_result=mrz,
        consistency_result=consistency,
        validation_result=doc_val,
        tampering_result=tampering,
        face_result=face
    )
    assert res["risk_level"] in ["REVIEW", "HIGH"]
    assert res["risk_score"] >= 30
    assert len(res["indicators"]) > 0

def test_risk_expired_document_is_validity_warning():
    quality = {"overall_score": 88.0}
    ocr = {"ocr_confidence": 90.0, "extracted_data": {"full_name": "JOHN DOE"}}
    mrz = {"detected": False, "overall_status": "NOT_DETECTED"}
    consistency = {"overall_status": "NOT_APPLICABLE", "mismatches": []}
    tampering = {"tampering_score": 5.0, "status": "LOW", "indicators": []}
    doc_val = {
        "status": "VALIDITY_WARNING",
        "checks": [{"name": "Expiry Status", "status": "WARNING", "reason": "Document expired"}]
    }
    face = None

    res = evaluate_document_risk(
        extracted_data=ocr["extracted_data"],
        quality_metrics=quality,
        ocr_confidence=ocr["ocr_confidence"],
        document_type="PASSPORT",
        mrz_result=mrz,
        consistency_result=consistency,
        validation_result=doc_val,
        tampering_result=tampering,
        face_result=face
    )
    assert res["risk_level"] in ["LOW", "REVIEW"]
    assert res["risk_score"] < 60
