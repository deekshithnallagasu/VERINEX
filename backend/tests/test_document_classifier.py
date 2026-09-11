import os
import pytest
from pathlib import Path
from PIL import Image

from backend.app.services.document_classifier import DocumentTypeClassifier
from backend.app.services.sample_generator import generate_sample_documents
from backend.app.config import SAMPLES_DIR

@pytest.fixture(scope="module")
def sample_files():
    """Ensures all fictional specimen images exist before running tests."""
    return generate_sample_documents()

@pytest.fixture
def classifier():
    return DocumentTypeClassifier(confidence_threshold=75.0)

# 1. Passport selected + valid passport = PASS (DOCUMENT_TYPE_CONFIRMED)
def test_passport_selected_valid_passport(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_passport_clean.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert res["detected_document_type"] == "PASSPORT"
    assert res["is_match"] is True
    assert res["classification_confidence"] >= 75.0

# 2. Passport selected + Aadhaar = MISMATCH (DOCUMENT_TYPE_MISMATCH)
def test_passport_selected_aadhaar_mismatch(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_aadhaar.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] == "DOCUMENT_TYPE_MISMATCH"
    assert res["detected_document_type"] == "AADHAAR"
    assert res["is_match"] is False
    assert "Aadhaar" in res["warning_message"]

# 3. Passport selected + PAN = MISMATCH (DOCUMENT_TYPE_MISMATCH)
def test_passport_selected_pan_mismatch(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_pan_card.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] == "DOCUMENT_TYPE_MISMATCH"
    assert res["detected_document_type"] == "PAN_CARD"
    assert res["is_match"] is False
    assert "PAN" in res["warning_message"] or "Permanent Account Number" in res["warning_message"]

# 4. Passport selected + Driving Licence = MISMATCH (DOCUMENT_TYPE_MISMATCH)
def test_passport_selected_dl_mismatch(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_license_expired.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] == "DOCUMENT_TYPE_MISMATCH"
    assert res["detected_document_type"] == "DRIVERS_LICENSE"
    assert res["is_match"] is False

# 5. Passport selected + signature image = UNKNOWN/MISMATCH
def test_passport_selected_signature_mismatch(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_signature.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] in ["DOCUMENT_TYPE_MISMATCH", "UNKNOWN_DOCUMENT"]
    assert res["detected_document_type"] == "UNKNOWN"
    assert res["is_match"] is False
    assert "Signature" in res["detected_document_name"] or "Non-Document" in res["detected_document_name"]

# 6. Passport selected + random photo = UNKNOWN/MISMATCH
def test_passport_selected_random_photo_mismatch(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_random_photo.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] in ["DOCUMENT_TYPE_MISMATCH", "UNKNOWN_DOCUMENT"]
    assert res["detected_document_type"] == "UNKNOWN"
    assert res["is_match"] is False

# 7. Passport selected + blank image = INVALID/UNKNOWN
def test_passport_selected_blank_image(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_blank.png")
    res = classifier.classify_document(path, selected_document_type="PASSPORT")
    assert res["validation_status"] in ["UNKNOWN_DOCUMENT", "INVALID_INPUT", "DOCUMENT_TYPE_MISMATCH"]
    assert res["detected_document_type"] == "UNKNOWN"
    assert res["is_match"] is False
    assert res["classification_confidence"] <= 20.0

# 8. Aadhaar selected + valid Aadhaar = PASS (DOCUMENT_TYPE_CONFIRMED)
def test_aadhaar_selected_valid_aadhaar(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_aadhaar.png")
    res = classifier.classify_document(path, selected_document_type="AADHAAR")
    assert res["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert res["detected_document_type"] == "AADHAAR"
    assert res["is_match"] is True
    assert res["classification_confidence"] >= 75.0

# 9. PAN selected + valid PAN = PASS (DOCUMENT_TYPE_CONFIRMED)
def test_pan_selected_valid_pan(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_pan_card.png")
    res = classifier.classify_document(path, selected_document_type="PAN_CARD")
    assert res["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert res["detected_document_type"] == "PAN_CARD"
    assert res["is_match"] is True
    assert res["classification_confidence"] >= 75.0

# 10. Driving Licence selected + valid Driving Licence = PASS (DOCUMENT_TYPE_CONFIRMED)
def test_dl_selected_valid_dl(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_license_expired.png")
    res = classifier.classify_document(path, selected_document_type="DRIVERS_LICENSE")
    assert res["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert res["detected_document_type"] == "DRIVERS_LICENSE"
    assert res["is_match"] is True

# 11. Voter ID selected + valid Voter ID = PASS (DOCUMENT_TYPE_CONFIRMED)
def test_voter_id_selected_valid_voter_id(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_voter_id.png")
    res = classifier.classify_document(path, selected_document_type="VOTER_ID")
    assert res["validation_status"] == "DOCUMENT_TYPE_CONFIRMED"
    assert res["detected_document_type"] == "VOTER_ID"
    assert res["is_match"] is True
    assert res["classification_confidence"] >= 75.0

# 12. Low-confidence document = MANUAL_REVIEW_REQUIRED
def test_low_confidence_manual_review(classifier, sample_files):
    path = str(SAMPLES_DIR / "sample_residence_blurry.png")
    # Partial or degraded OCR text below full threshold triggers manual review
    res = classifier.classify_document(
        path,
        selected_document_type="RESIDENCE_PERMIT",
        raw_ocr_text="EUROPEAN UNION RESIDENCE PERMIT\nNAME: HELENA SANTO\nRC-448219"
    )
    assert res["validation_status"] == "MANUAL_REVIEW_REQUIRED"
    assert res["detected_document_type"] == "RESIDENCE_PERMIT"
    assert res["classification_confidence"] < 75.0
    assert res["is_match"] is False
    assert "manual review" in res["warning_message"].lower()
