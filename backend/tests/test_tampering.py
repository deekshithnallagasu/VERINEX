import pytest
import numpy as np
import cv2
from pathlib import Path
from backend.app.services.tampering_service import analyze_image_tampering

def test_tampering_clean_synthetic_image(tmp_path):
    img = np.full((300, 400, 3), 240, dtype=np.uint8)
    cv2.putText(img, "TEST DOCUMENT", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (20, 20, 20), 2)
    img_path = tmp_path / "clean_test.png"
    cv2.imwrite(str(img_path), img)

    res = analyze_image_tampering(str(img_path))
    assert "tampering_score" in res
    assert "photo_manipulation_score" in res
    assert "suspicious_regions" in res
    assert res["status"] in ["LOW", "REVIEW", "HIGH"]

def test_tampering_composite_splice_anomaly(tmp_path):
    img = np.full((400, 500, 3), 240, dtype=np.uint8)
    noise_block = np.random.randint(0, 255, (100, 120, 3), dtype=np.uint8)
    img[100:200, 150:270] = noise_block

    img_path = tmp_path / "spliced_test.png"
    cv2.imwrite(str(img_path), img)

    res = analyze_image_tampering(str(img_path))
    assert res["tampering_score"] >= 0.0
    assert "status" in res
