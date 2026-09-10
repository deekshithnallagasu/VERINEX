import pytest
from backend.app.services.document_validation import validate_document_logic

def test_date_validation_valid():
    extracted = {
        "full_name": "CLARA ABERNATHY",
        "document_number": "E84920194",
        "date_of_birth": "1989-05-14",
        "issue_date": "2019-06-11",
        "expiry_date": "2029-06-11",
        "nationality": "USA"
    }
    res = validate_document_logic(extracted, "PASSPORT")
    assert res["status"] in ["VALID", "VALIDITY_WARNING"]
    expiry_check = next((c for c in res["checks"] if "Expiry" in c["name"]), None)
    assert expiry_check is not None
    assert expiry_check["status"] == "PASS"

def test_date_validation_expired_warning_not_forgery():
    extracted = {
        "full_name": "JAMES MORGAN",
        "document_number": "D9812401",
        "date_of_birth": "1975-03-22",
        "issue_date": "2010-01-15",
        "expiry_date": "2020-01-15",
        "nationality": "USA"
    }
    res = validate_document_logic(extracted, "DRIVERS_LICENSE")
    assert res["status"] == "VALIDITY_WARNING"
    expiry_check = next((c for c in res["checks"] if "Expiry" in c["name"]), None)
    assert expiry_check is not None
    assert expiry_check["status"] == "WARNING"

def test_date_validation_future_dob():
    extracted = {
        "full_name": "FUTURE CITIZEN",
        "document_number": "X1234567",
        "date_of_birth": "2099-01-01"
    }
    res = validate_document_logic(extracted, "PASSPORT")
    dob_check = next((c for c in res["checks"] if "Date of Birth" in c["name"]), None)
    assert dob_check is not None
    assert dob_check["status"] == "FAIL"
