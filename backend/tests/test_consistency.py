import pytest
from backend.app.services.consistency_service import verify_ocr_mrz_consistency

def test_consistency_matching_records():
    ocr_data = {
        "full_name": "CLARA ELEANOR ABERNATHY",
        "document_number": "E84920194",
        "date_of_birth": "1989-05-14",
        "expiry_date": "2029-06-11",
        "nationality": "USA"
    }
    mrz_data = {
        "detected": True,
        "valid_structure": True,
        "parsed": {
            "surname": "ABERNATHY",
            "given_names": "CLARA ELEANOR",
            "document_number": "E84920194",
            "date_of_birth": "1989-05-14",
            "expiry_date": "2029-06-11",
            "nationality": "USA"
        }
    }
    res = verify_ocr_mrz_consistency(ocr_data, mrz_data)
    assert res["name_match"] is True
    assert res["document_number_match"] is True
    assert res["overall_status"] == "PASS"
    assert len(res["mismatches"]) == 0

def test_consistency_tampered_name_mismatch():
    ocr_data = {
        "full_name": "MARCUS REID",
        "document_number": "E84920194"
    }
    mrz_data = {
        "detected": True,
        "valid_structure": True,
        "parsed": {
            "surname": "JONES",
            "given_names": "DEVON",
            "document_number": "E84920194"
        }
    }
    res = verify_ocr_mrz_consistency(ocr_data, mrz_data)
    assert res["name_match"] is False
    assert res["document_number_match"] is True
    assert res["overall_status"] == "FAIL"
    assert any("Name mismatch" in m.get("reason", "") for m in res["mismatches"])
