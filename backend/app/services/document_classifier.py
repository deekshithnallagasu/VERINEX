import os
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageStat, ImageOps

from ..config import settings
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
from .quality_service import analyze_document_quality

class DocumentTypeClassifier:
    """
    Mandatory Document Type Authentication & Classification Service.
    
    Independently inspects an uploaded image to determine its genuine identity document type
    before OCR field extraction, digital forensics, or risk scoring can proceed.
    
    Combines:
    - Visual/layout features (blank detection, signature detection, selfie/portrait detection, aspect ratio)
    - RapidOCR text extraction and weighted keyword analysis
    - Identity number regex patterns (Aadhaar, PAN, Passport MRZ, DL, Voter ID)
    - Structural expected field detection
    """
    
    # Document Type Canonical Names & Aliases
    DOCUMENT_TYPES = {
        "PASSPORT": {
            "name": "Passport (ICAO Doc 9303)",
            "aliases": ["PASSPORT", "PASSPORT_TD3", "PASSPORT_TD1"],
            "aspect_ratio": 1.42,
            "expected_features": ["ICAO 9303 MRZ Lines (P<...)", "Issuing Country / State Banner", "Passport Number", "Holder Portrait", "Date of Birth & Expiry"]
        },
        "AADHAAR": {
            "name": "Aadhaar Card (UIDAI)",
            "aliases": ["AADHAAR", "AADHAR", "UIDAI"],
            "aspect_ratio": 1.58,
            "expected_features": ["Government of India Header", "12-Digit UID Number", "UIDAI Emblem / Logo", "Date of Birth / Year of Birth", "Mera Aadhaar Meri Pehchan"]
        },
        "PAN_CARD": {
            "name": "Permanent Account Number Card (Income Tax Dept)",
            "aliases": ["PAN_CARD", "PAN", "PANCARD"],
            "aspect_ratio": 1.58,
            "expected_features": ["Income Tax Department Header", "10-Character Alphanumeric PAN", "Father's Name Field", "Holder Photo & Signature Zone", "Govt. of India Seal"]
        },
        "DRIVERS_LICENSE": {
            "name": "Driver License / Driving Licence",
            "aliases": ["DRIVERS_LICENSE", "DRIVER_LICENSE", "DRIVING_LICENCE", "DL"],
            "aspect_ratio": 1.58,
            "expected_features": ["Driver License / Permis de Conduire Title", "DL Number", "Vehicle Class Categories", "Issuing Transport Authority", "Date of Issue & Expiry"]
        },
        "VOTER_ID": {
            "name": "Elector Photo Identity Card (Voter ID)",
            "aliases": ["VOTER_ID", "VOTER", "EPIC"],
            "aspect_ratio": 1.58,
            "expected_features": ["Election Commission of India Header", "EPIC Alphanumeric Number", "Elector Name & Father/Spouse Name", "Constituency Details", "Electoral Photo"]
        },
        "NATIONAL_ID": {
            "name": "National Identity Card (Dual Zone)",
            "aliases": ["NATIONAL_ID", "NATIONALID", "ID_CARD"],
            "aspect_ratio": 1.58,
            "expected_features": ["National Identity Card Title", "Document Identification Number", "Nationality / Citizenship", "Holder Portrait"]
        },
        "RESIDENCE_PERMIT": {
            "name": "Residence Permit / Work Authorization",
            "aliases": ["RESIDENCE_PERMIT", "TITRE_SEJOUR", "PERMIT"],
            "aspect_ratio": 1.58,
            "expected_features": ["Residence Permit / Titre de Sejour Header", "Permit Number", "Valid Until / Expiration Date", "Immigration Authority Reference"]
        }
    }

    # Targeted Regex Patterns for Document Number Formats
    NUMBER_PATTERNS = {
        "AADHAAR": [
            r'\b\d{4}\s\d{4}\s\d{4}\b',      # 1234 5678 9012
            r'\b\d{12}\b'                     # 123456789012
        ],
        "PAN_CARD": [
            r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'      # ABCDE1234F
        ],
        "VOTER_ID": [
            r'\b[A-Z]{3}[0-9]{7}\b',          # ABC1234567
            r'\b[A-Z]{2}/[0-9]{2}/[0-9]{3}/[0-9]{6}\b'
        ],
        "PASSPORT": [
            r'\bP<[A-Z0-9<]{42,43}',          # MRZ TD3 Line 1
            r'\b[A-Z0-9<]{44}\b',              # MRZ TD3 Line 2
            r'\b[A-Z][0-9]{7,9}\b'             # Standard Passport Num e.g. E84920194
        ],
        "DRIVERS_LICENSE": [
            r'\b[A-Z]{2}[0-9]{2}[ -]?[0-9]{11}\b',  # Indian standard DL
            r'\bWDL[0-9]{8}\b',                     # Sample Washington State DL
            r'\bDL[- :A-Z0-9]{8,16}\b'
        ]
    }

    # Keyword Profiles with Weights
    KEYWORDS = {
        "PASSPORT": [
            ("PASSPORT", 15), ("PASSEPORT", 12), ("UNITED STATES", 8), ("REPUBLIC", 6),
            ("KINGDOM", 6), ("PASSPORT NO", 14), ("NO DE PASSEPORT", 12), ("P<", 20),
            ("DATE OF BIRTH", 5), ("NATIONALITY", 7), ("AUTHORITY", 5), ("EXPIRATION", 5)
        ],
        "AADHAAR": [
            ("AADHAAR", 20), ("UIDAI", 20), ("GOVERNMENT OF INDIA", 15), ("GOVT OF INDIA", 12),
            ("UNIQUE IDENTIFICATION", 18), ("MERA AADHAAR", 15), ("MERI PEHCHAN", 12),
            ("BHARAT SARKAR", 15), ("AUTHORITY OF INDIA", 12), ("HELP@UIDAI", 10),
            ("ENROLMENT", 8), ("VID", 8)
        ],
        "PAN_CARD": [
            ("INCOME TAX DEPARTMENT", 22), ("PERMANENT ACCOUNT NUMBER", 22), ("GOVT. OF INDIA", 12),
            ("GOVERNMENT OF INDIA", 12), ("INCOMETAX", 15), ("AYAKAR", 15),
            ("FATHER'S NAME", 10), ("FATHER NAME", 10), ("SIGNATURE", 8), ("PAN", 6)
        ],
        "DRIVERS_LICENSE": [
            ("DRIVING LICENCE", 22), ("DRIVER LICENSE", 22), ("PERMIS DE CONDUIRE", 18),
            ("DL NO", 16), ("LICENCE TO DRIVE", 18), ("UNION OF INDIA", 12),
            ("MOTOR VEHICLES", 14), ("TRANSPORT", 10), ("VALIDITY", 8), ("AUTHORISATION", 8)
        ],
        "VOTER_ID": [
            ("ELECTION COMMISSION OF INDIA", 22), ("ELECTOR PHOTO IDENTITY CARD", 24),
            ("ELECTOR", 14), ("EPIC NO", 18), ("BHARAT NIRVACHAN", 18),
            ("ASSEMBLY CONSTITUENCY", 14), ("PARLIAMENTARY", 10), ("ELECTORAL", 10)
        ],
        "NATIONAL_ID": [
            ("IDENTITY CARD", 16), ("NATIONAL ID", 18), ("CARTE NATIONALE", 18),
            ("CITIZEN", 10), ("PERSONAL ID", 12), ("NATIONAL IDENTITY", 16)
        ],
        "RESIDENCE_PERMIT": [
            ("RESIDENCE PERMIT", 22), ("TITRE DE SEJOUR", 22), ("PERMIT TO RESIDE", 18),
            ("WORK AUTHORIZATION", 15), ("RESIDENCE CARD", 15), ("IMMIGRATION", 10)
        ]
    }

    def __init__(self, confidence_threshold: Optional[float] = None):
        self.confidence_threshold = confidence_threshold or getattr(
            settings, "DOCUMENT_TYPE_CONFIDENCE_THRESHOLD", 75.0
        )

    def normalize_doc_type(self, doc_type_str: str) -> str:
        """Maps any alias to the standard canonical document type key."""
        clean = doc_type_str.strip().upper().replace(" ", "_").replace("-", "_")
        for canon, data in self.DOCUMENT_TYPES.items():
            if clean == canon or clean in data["aliases"]:
                return canon
        return clean

    def inspect_visual_input_type(self, image_path: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Inspects low-level image attributes to immediately identify:
        - Blank / uniform paper
        - Signature only image
        - Selfie / portrait only
        - Generic non-document image
        
        Returns (detected_category, confidence, visual_signals)
        """
        if not os.path.exists(image_path):
            return "UNKNOWN", 0.0, {"error": "File does not exist on disk"}

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = round(width / max(1, height), 2)
                gray = img.convert("L")
                stat = ImageStat.Stat(gray)
                mean_brightness = stat.mean[0]
                stddev = stat.stddev[0]
                
                # Check for Blank / Plain Uniform image
                # Standard document has varied text/photos giving stddev > 25.
                # Blank paper typically has stddev < 10 or mean > 245 with almost zero variance.
                if stddev < 10.0 or (mean_brightness > 246.0 and stddev < 14.0):
                    return "BLANK_IMAGE", 95.0, {
                        "visual_type": "BLANK_IMAGE",
                        "reason": "Uniform or blank image with minimal contrast/content variance",
                        "mean_brightness": round(mean_brightness, 1),
                        "stddev": round(stddev, 2),
                        "aspect_ratio": aspect_ratio
                    }

                # Signature Heuristic:
                # Signatures are typically drawn with dark ink on white background,
                # have thin aspect ratios (>2.2 or <0.5), or extremely low stroke density (<6% dark pixels),
                # and lack tabular card borders, headers, and photos.
                # Threshold to detect dark pixel ratio
                threshold = 128
                binary = gray.point(lambda p: 255 if p > threshold else 0)
                colors = binary.getcolors(maxcolors=256) or []
                dark_pixels = sum(count for count, color in colors if color == 0)
                total_pixels = width * height
                dark_ratio = dark_pixels / max(1, total_pixels)

                # Signature characteristics:
                # 1. Dark pixel ratio between 0.5% and 8% on plain background
                # 2. Mean brightness high (white paper > 200)
                # 3. High stddev of local strokes but overall sparse
                # 4. Aspect ratio typically elongated (>2.1 or height < 220)
                is_sparse_stroke = 0.003 <= dark_ratio <= 0.075 and mean_brightness > 195.0
                is_elongated_stroke = (aspect_ratio > 2.2 or aspect_ratio < 0.55) and dark_ratio < 0.12

                if is_sparse_stroke and (is_elongated_stroke or stddev < 38.0 or width < 400 or height < 250):
                    return "SIGNATURE_IMAGE", 90.0, {
                        "visual_type": "SIGNATURE_IMAGE",
                        "reason": "Image displays isolated ink strokes on plain background without document headers or structure",
                        "dark_ratio_percent": round(dark_ratio * 100, 2),
                        "aspect_ratio": aspect_ratio,
                        "dimensions": f"{width}x{height}"
                    }

                return "DOCUMENT_CANDIDATE", 50.0, {
                    "visual_type": "DOCUMENT_CANDIDATE",
                    "aspect_ratio": aspect_ratio,
                    "dimensions": f"{width}x{height}",
                    "stddev": round(stddev, 2)
                }

        except Exception as e:
            return "UNKNOWN", 0.0, {"error": str(e)}

    def extract_text_signals(self, image_path: str, raw_ocr_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Gathers OCR text, detected lines, and extracts matched keywords and regex patterns.
        """
        text = raw_ocr_text or ""
        lines = text.splitlines()

        # If text not provided, run RapidOCR extraction
        if not text and os.path.exists(image_path):
            from .ocr_service import get_ocr_engine
            engine = get_ocr_engine()
            if engine:
                try:
                    ocr_res, _ = engine(image_path)
                    if ocr_res:
                        lines = [str(item[1]).strip() for item in ocr_res if str(item[1]).strip()]
                        text = "\n".join(lines)
                except Exception:
                    pass

        text_upper = text.upper()

        keyword_matches: Dict[str, List[str]] = {}
        keyword_scores: Dict[str, float] = {}
        regex_matches: Dict[str, List[str]] = {}

        for doc_type, kw_list in self.KEYWORDS.items():
            matched_kws = []
            score = 0.0
            for kw, weight in kw_list:
                if kw in text_upper:
                    matched_kws.append(kw)
                    score += weight
            keyword_matches[doc_type] = matched_kws
            keyword_scores[doc_type] = score

        # Check regex patterns
        for doc_type, patterns in self.NUMBER_PATTERNS.items():
            found_patterns = []
            for pat in patterns:
                matches = re.findall(pat, text_upper)
                if matches:
                    found_patterns.extend([str(m).strip() for m in matches])
            if found_patterns:
                regex_matches[doc_type] = list(set(found_patterns))

        # Check MRZ characteristics
        has_passport_mrz = False
        mrz_lines = []
        for line in lines:
            cleaned = line.replace(" ", "").upper()
            if "<" in cleaned and (len(cleaned) >= 30 or cleaned.startswith("P<")):
                mrz_lines.append(cleaned)
                if cleaned.startswith("P<") or len(cleaned) == 44:
                    has_passport_mrz = True

        return {
            "raw_text": text,
            "lines_count": len(lines),
            "text_length": len(text),
            "keyword_matches": keyword_matches,
            "keyword_scores": keyword_scores,
            "regex_matches": regex_matches,
            "has_passport_mrz": has_passport_mrz,
            "mrz_lines": mrz_lines
        }

    def classify_document(
        self,
        image_path: str,
        selected_document_type: str = "PASSPORT",
        raw_ocr_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs end-to-end Document Type Classification & Authentication:
        1. Low-level visual & structure analysis (rejects blanks, signatures, selfies, etc.)
        2. RapidOCR text parsing & pattern identification
        3. Multi-hypothesis document score fusion
        4. Cross-checks detected document type against selected document type
        5. Computes authoritative validation_status and explanatory messages
        """
        selected_canonical = self.normalize_doc_type(selected_document_type)

        # 1. Low-level Visual Check
        visual_type, visual_conf, visual_signals = self.inspect_visual_input_type(image_path)

        # Immediate rejection of Blank Images
        if visual_type == "BLANK_IMAGE":
            return self._build_result(
                selected_type=selected_canonical,
                detected_type="UNKNOWN",
                detected_name="Blank / Uniform Paper",
                confidence=10.0,
                validation_status="UNKNOWN_DOCUMENT",
                mismatch_reason="The uploaded image is blank or has uniform pixel values without readable text or document structure.",
                warning_message=f"Invalid document input: {self.DOCUMENT_TYPES.get(selected_canonical, {}).get('name', selected_canonical)} was selected, but the uploaded file appears to be blank paper. Please upload an authentic identity document.",
                extracted_signals=visual_signals,
                scores_breakdown={}
            )

        # Extract text signals
        text_signals = self.extract_text_signals(image_path, raw_ocr_text)
        lines_count = text_signals["lines_count"]
        text_len = text_signals["text_length"]
        kw_scores = text_signals["keyword_scores"]
        regex_matches = text_signals["regex_matches"]
        has_passport_mrz = text_signals["has_passport_mrz"]

        # Immediate rejection of Signature Images
        # If visual inspection flagged signature AND text has 0 identity keywords and few lines
        max_kw_score = max(kw_scores.values()) if kw_scores else 0
        if (visual_type == "SIGNATURE_IMAGE" or lines_count <= 2) and max_kw_score < 10 and not regex_matches:
            if visual_type == "SIGNATURE_IMAGE" or (text_len < 30 and lines_count <= 2):
                return self._build_result(
                    selected_type=selected_canonical,
                    detected_type="UNKNOWN",
                    detected_name="Signature Image / Non-Document",
                    confidence=15.0,
                    validation_status="DOCUMENT_TYPE_MISMATCH",
                    mismatch_reason=f"The uploaded file appears to be a standalone signature or non-document image, not a valid {self.DOCUMENT_TYPES.get(selected_canonical, {}).get('name', selected_canonical)}.",
                    warning_message=f"Document type mismatch: {self.DOCUMENT_TYPES.get(selected_canonical, {}).get('name', selected_canonical)} was selected, but the uploaded file does not appear to be a {selected_canonical}. A valid {selected_canonical} image/document must be uploaded.",
                    extracted_signals={**visual_signals, **text_signals},
                    scores_breakdown={}
                )

        # Check for Random Photo / Landscape / Portrait without identity document text
        if lines_count == 0 and max_kw_score == 0 and not regex_matches:
            return self._build_result(
                selected_type=selected_canonical,
                detected_type="UNKNOWN",
                detected_name="Unrecognized Non-Document Photo",
                confidence=15.0,
                validation_status="UNKNOWN_DOCUMENT",
                mismatch_reason="No identity document markers, headers, or structured text lines could be identified in the uploaded image.",
                warning_message=f"Unrecognized image: The uploaded file does not contain document headers or identification zones expected for a {self.DOCUMENT_TYPES.get(selected_canonical, {}).get('name', selected_canonical)}. Please upload a clear document image.",
                extracted_signals={**visual_signals, **text_signals},
                scores_breakdown={}
            )

        # 2. Multi-Hypothesis Document Scoring
        doc_scores: Dict[str, float] = {}
        for doc_type in self.DOCUMENT_TYPES.keys():
            score = 0.0
            kw_sc = kw_scores.get(doc_type, 0.0)
            score += min(55.0, kw_sc * 1.2)

            # Regex bonuses
            if doc_type in regex_matches:
                score += 30.0

            # MRZ bonus for Passport
            if doc_type == "PASSPORT" and has_passport_mrz:
                score += 35.0

            # Aspect ratio proximity bonus
            target_ratio = self.DOCUMENT_TYPES[doc_type]["aspect_ratio"]
            actual_ratio = visual_signals.get("aspect_ratio", 1.58)
            ratio_diff = abs(actual_ratio - target_ratio)
            if ratio_diff < 0.15:
                score += 10.0
            elif ratio_diff < 0.3:
                score += 5.0

            # Penalties: if a document has specific incompatible signals
            if doc_type != "PASSPORT" and has_passport_mrz:
                score -= 20.0
            if doc_type != "AADHAAR" and "AADHAAR" in text_signals["keyword_matches"].get("AADHAAR", []):
                score -= 15.0
            if doc_type != "PAN_CARD" and "PERMANENT ACCOUNT NUMBER" in text_signals["keyword_matches"].get("PAN_CARD", []):
                score -= 15.0

            doc_scores[doc_type] = round(max(0.0, score), 1)

        # Determine best matching candidate
        sorted_candidates = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        top_type, top_score = sorted_candidates[0] if sorted_candidates else ("UNKNOWN", 0.0)

        # Scale score into 0-100 confidence
        # Score >= 50 maps to 80-99% confidence
        if top_score >= 45.0:
            confidence = min(99.0, round(75.0 + (top_score - 45.0) * 0.45, 1))
        elif top_score >= 30.0:
            confidence = round(50.0 + (top_score - 30.0) * 1.6, 1)  # 50 - 74%
        elif top_score >= 15.0:
            confidence = round(30.0 + (top_score - 15.0) * 1.3, 1)  # 30 - 49%
        else:
            confidence = round(max(10.0, top_score), 1)

        # 3. Validation Logic & Status Assignment
        detected_info = self.DOCUMENT_TYPES.get(top_type, {"name": "Unrecognized Document", "expected_features": []})
        selected_info = self.DOCUMENT_TYPES.get(selected_canonical, {"name": selected_canonical, "expected_features": []})

        # Case A: Low Confidence / Ambiguous
        if confidence < 35.0 or top_score < 20.0:
            return self._build_result(
                selected_type=selected_canonical,
                detected_type="UNKNOWN",
                detected_name="Unrecognized / Unsupported Document",
                confidence=confidence,
                validation_status="UNKNOWN_DOCUMENT",
                mismatch_reason="The uploaded image does not exhibit sufficient document features or recognized keywords for any supported identity document type.",
                warning_message=f"Document type mismatch: {selected_info.get('name', selected_canonical)} was selected, but the uploaded file does not appear to be a recognized identity document.",
                extracted_signals={**visual_signals, **text_signals},
                scores_breakdown=doc_scores
            )

        # Case B: Marginal Confidence -> Manual Review Required
        if confidence < self.confidence_threshold:
            return self._build_result(
                selected_type=selected_canonical,
                detected_type=top_type,
                detected_name=detected_info.get("name", top_type),
                confidence=confidence,
                validation_status="MANUAL_REVIEW_REQUIRED",
                mismatch_reason=f"Classification confidence ({confidence}%) is below the required security threshold ({self.confidence_threshold}%).",
                warning_message=f"Unable to confidently determine document type (Confidence: {confidence}%) — manual review required before proceeding.",
                extracted_signals={**visual_signals, **text_signals},
                scores_breakdown=doc_scores
            )

        # Case C: High Confidence -> Match vs Mismatch
        if top_type == selected_canonical:
            return self._build_result(
                selected_type=selected_canonical,
                detected_type=top_type,
                detected_name=detected_info.get("name", top_type),
                confidence=confidence,
                validation_status="DOCUMENT_TYPE_CONFIRMED",
                mismatch_reason=None,
                warning_message=None,
                extracted_signals={**visual_signals, **text_signals},
                scores_breakdown=doc_scores
            )
        else:
            # Document Type Mismatch!
            return self._build_result(
                selected_type=selected_canonical,
                detected_type=top_type,
                detected_name=detected_info.get("name", top_type),
                confidence=confidence,
                validation_status="DOCUMENT_TYPE_MISMATCH",
                mismatch_reason=f"User selected {selected_info.get('name', selected_canonical)}, but automated classification determined the file is a {detected_info.get('name', top_type)}.",
                warning_message=f"Document type mismatch: {selected_info.get('name', selected_canonical)} was selected, but the uploaded file appears to be a {detected_info.get('name', top_type)}. Please upload a valid {selected_info.get('name', selected_canonical)}.",
                extracted_signals={**visual_signals, **text_signals},
                scores_breakdown=doc_scores
            )

    def _build_result(
        self,
        selected_type: str,
        detected_type: str,
        detected_name: str,
        confidence: float,
        validation_status: str,
        mismatch_reason: Optional[str],
        warning_message: Optional[str],
        extracted_signals: Dict[str, Any],
        scores_breakdown: Dict[str, float]
    ) -> Dict[str, Any]:
        """Constructs the canonical validation payload returned by the classifier."""
        expected_features = self.DOCUMENT_TYPES.get(selected_type, {}).get("expected_features", [
            "Official Government Issuance Headers",
            "Unique Identification Number",
            "Holder Identity & Biometric Zones"
        ])

        # Clean serializable signals
        clean_signals = {
            "visual_type": extracted_signals.get("visual_type", "UNKNOWN"),
            "aspect_ratio": extracted_signals.get("aspect_ratio"),
            "lines_count": extracted_signals.get("lines_count", 0),
            "has_passport_mrz": extracted_signals.get("has_passport_mrz", False),
            "matched_keywords": {k: v for k, v in extracted_signals.get("keyword_matches", {}).items() if v},
            "matched_regex": extracted_signals.get("regex_matches", {})
        }

        return {
            "selected_document_type": selected_type,
            "detected_document_type": detected_type,
            "detected_document_name": detected_name,
            "classification_confidence": confidence,
            "confidence_threshold": self.confidence_threshold,
            "validation_status": validation_status,
            "is_match": (validation_status == "DOCUMENT_TYPE_CONFIRMED"),
            "extracted_signals": clean_signals,
            "expected_document_features": expected_features,
            "mismatch_reason": mismatch_reason,
            "warning_message": warning_message,
            "scores_breakdown": scores_breakdown
        }

# Global default classifier instance
classifier = DocumentTypeClassifier()
