import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

def load_document_templates() -> List[Dict[str, Any]]:
    templates = []
    if TEMPLATES_DIR.exists():
        for file in TEMPLATES_DIR.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["template_id"] = file.stem
                    templates.append(data)
            except Exception:
                pass
    return templates

def detect_document_type(
    raw_text: str,
    aspect_ratio: float = 1.42,
    has_mrz: bool = False,
    mrz_lines_count: int = 0
) -> Dict[str, Any]:
    """
    Detects prototype document type based on:
    - Extracted OCR keyword clues
    - Aspect ratio matching
    - Machine Readable Zone (MRZ) presence & line count
    - Template schema evaluation
    
    Returns identified document template and confidence.
    Clearly marks unsupported documents.
    """
    text_upper = raw_text.upper()
    templates = load_document_templates()

    best_match = None
    best_score = 0.0
    scores_breakdown = {}

    for tmpl in templates:
        score = 0.0
        doc_type = tmpl.get("document_type", "")
        keywords = tmpl.get("keywords", [])
        
        # 1. Keyword matching
        matched_keywords = [kw for kw in keywords if kw in text_upper]
        if matched_keywords:
            score += min(60.0, len(matched_keywords) * 20.0)

        # 2. MRZ presence alignment
        mrz_required = tmpl.get("mrz_required", False)
        tmpl_mrz_lines = tmpl.get("mrz_lines", 0)
        if mrz_required and has_mrz:
            score += 25.0
            if mrz_lines_count == tmpl_mrz_lines:
                score += 15.0
        elif not mrz_required and not has_mrz:
            score += 15.0

        # 3. Aspect ratio proximity
        tmpl_ratio = tmpl.get("aspect_ratio", 1.42)
        ratio_diff = abs(aspect_ratio - tmpl_ratio)
        if ratio_diff < 0.15:
            score += 10.0
        elif ratio_diff < 0.3:
            score += 5.0

        scores_breakdown[doc_type] = round(score, 1)
        if score > best_score:
            best_score = score
            best_match = tmpl

    if best_match and best_score >= 35.0:
        return {
            "document_type": best_match["document_type"],
            "document_name": best_match["name"],
            "confidence": min(98.0, round(best_score + 10.0, 1)),
            "is_supported": True,
            "required_fields": best_match.get("required_fields", []),
            "optional_fields": best_match.get("optional_fields", []),
            "mrz_expected": best_match.get("mrz_required", False),
            "template_id": best_match.get("template_id"),
            "scores_breakdown": scores_breakdown
        }
    else:
        # Unsupported or ambiguous document
        return {
            "document_type": "UNKNOWN_OR_UNSUPPORTED",
            "document_name": "Unsupported / Unrecognized Identity Specimen",
            "confidence": 30.0,
            "is_supported": False,
            "required_fields": ["document_number", "full_name"],
            "optional_fields": [],
            "mrz_expected": False,
            "template_id": None,
            "scores_breakdown": scores_breakdown,
            "notice": "Document does not match supported prototype templates (Passport TD3/TD1, National ID, Driver License, Residence Permit, Visa)."
        }
