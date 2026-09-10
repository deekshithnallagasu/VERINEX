import pytest
import numpy as np
import cv2
from backend.app.services.ocr_service import extract_document_text, parse_names, parse_document_number

def test_parse_structured_fields_helpers():
    raw_lines = [
        "PASSPORT",
        "UNITED STATES OF AMERICA",
        "Passport No. / No du passeport: E84920194",
        "Surname / Nom: ABERNATHY",
        "Given Names / Prenoms: CLARA ELEANOR"
    ]
    doc_num = parse_document_number(raw_lines)
    surname, given_names = parse_names(raw_lines)
    assert doc_num == "E84920194"
    assert surname == "ABERNATHY"
    assert given_names == "CLARA ELEANOR"

def test_ocr_runs_on_image(tmp_path):
    img = np.full((150, 400, 3), 255, dtype=np.uint8)
    cv2.putText(img, "PASSPORT E84920194", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    img_path = tmp_path / "ocr_test.png"
    cv2.imwrite(str(img_path), img)

    res = extract_document_text(str(img_path), "PASSPORT")
    assert "ocr_confidence" in res
    assert "raw_text" in res
    assert "extracted_data" in res
    assert "E84920194" in res["raw_text"] or res["extracted_data"].get("document_number") == "E84920194"
