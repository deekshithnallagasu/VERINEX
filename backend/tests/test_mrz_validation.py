import pytest
from backend.app.services.mrz_service import detect_and_validate_mrz

def test_mrz_valid_td3_passport():
    lines = [
        "P<USAABERNATHY<<CLARA<ELEANOR<<<<<<<<<<<<<<<",
        "E849201943USA8905145F2906117<<<<<<<<<<<<<<04"
    ]
    res = detect_and_validate_mrz(lines)
    assert res["detected"] is True
    assert res["format"] == "TD3"
    assert res["valid_structure"] is True
    assert res["parsed"]["surname"] == "ABERNATHY"
    assert "CLARA" in res["parsed"]["given_names"]
    assert res["parsed"]["document_number"] == "E84920194"
    assert res["check_digits"]["document_number"] is True
    assert res["check_digits"]["date_of_birth"] is True
    assert res["check_digits"]["expiry_date"] is True

def test_mrz_invalid_check_digit():
    # Intentionally corrupt the document number check digit from 3 to 9
    lines = [
        "P<USAABERNATHY<<CLARA<ELEANOR<<<<<<<<<<<<<<<",
        "E849201949USA8905145F2906117<<<<<<<<<<<<<<04"
    ]
    res = detect_and_validate_mrz(lines)
    assert res["detected"] is True
    assert res["check_digits"]["document_number"] is False
    assert res["overall_status"] == "FAIL"

def test_mrz_not_detected():
    lines = ["NO MRZ HERE", "JUST RANDOM TEXT"]
    res = detect_and_validate_mrz(lines)
    assert res["detected"] is False
    assert res["overall_status"] == "NOT_DETECTED"
