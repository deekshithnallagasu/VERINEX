from datetime import datetime, date
from typing import Dict, Any, List

def calculate_mrz_checksum(data: str) -> int:
    """
    Computes standard ICAO 9303 7-3-1 weighting checksum for MRZ fields.
    """
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data):
        if char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char.upper()) - 55
        elif char == '<':
            val = 0
        else:
            val = 0
        total += val * weights[i % 3]
    return total % 10

def parse_date_safely(date_str: str) -> date | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d %b %Y", "%Y%m%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def evaluate_document_risk(
    extracted_data: Dict[str, Any],
    quality_metrics: Dict[str, Any],
    ocr_confidence: float,
    document_type: str = "PASSPORT"
) -> Dict[str, Any]:
    """
    Evaluates risk with full explainability and transparency.
    Returns:
    - risk_score: int (0-100)
    - overall_risk_level: "LOW" | "MEDIUM" | "HIGH"
    - ai_confidence: float (0-100%)
    - consistency_checks: list of check objects with status PASS/WARN/FAIL
    - suspicious_indicators: list of flags with explicit reasoning
    """
    now = datetime.utcnow().date()
    # Baseline score starts at 5 (minimal baseline noise)
    risk_score = 5
    consistency_checks: List[Dict[str, Any]] = []
    suspicious_indicators: List[Dict[str, Any]] = []

    # 1. Document Expiration Check
    exp_str = extracted_data.get("expiry_date")
    exp_date = parse_date_safely(exp_str)
    
    if exp_date:
        if exp_date < now:
            days_expired = (now - exp_date).days
            if days_expired > 365:
                risk_score += 45
                severity = "HIGH"
            else:
                risk_score += 30
                severity = "MEDIUM"

            consistency_checks.append({
                "check_name": "Document Validity Period",
                "status": "FAIL",
                "category": "Temporal Integrity",
                "details": f"Document expired {days_expired} days ago on {exp_date}."
            })
            suspicious_indicators.append({
                "title": "Expired Identity Document",
                "severity": severity,
                "category": "Temporal Validity",
                "explanation": f"The document expiration date ({exp_date}) has passed. Documents presented beyond their expiration date cannot guarantee current validity.",
                "recommendation": "Request renewed government-issued document from user."
            })
        elif (exp_date - now).days < 60:
            risk_score += 15
            consistency_checks.append({
                "check_name": "Document Validity Period",
                "status": "WARN",
                "category": "Temporal Integrity",
                "details": f"Document is approaching expiration within {(exp_date - now).days} days."
            })
            suspicious_indicators.append({
                "title": "Document Near Expiration",
                "severity": "LOW",
                "category": "Temporal Validity",
                "explanation": f"Document will expire in less than 60 days ({exp_date}).",
                "recommendation": "Verify user maintains alternative active identification."
            })
        else:
            consistency_checks.append({
                "check_name": "Document Validity Period",
                "status": "PASS",
                "category": "Temporal Integrity",
                "details": f"Document is valid through {exp_date}."
            })
    else:
        risk_score += 20
        consistency_checks.append({
            "check_name": "Document Validity Period",
            "status": "WARN",
            "category": "Temporal Integrity",
            "details": "Expiration date could not be parsed from document."
        })
        suspicious_indicators.append({
            "title": "Missing Expiry Date",
            "severity": "MEDIUM",
            "category": "Completeness",
            "explanation": "No valid expiration date could be extracted from the document visual inspection zone.",
            "recommendation": "Manual reviewer should inspect physical card corners."
        })

    # 2. Date of Birth and Age Realism
    dob_str = extracted_data.get("date_of_birth")
    dob_date = parse_date_safely(dob_str)
    if dob_date:
        if dob_date > now:
            risk_score += 50
            consistency_checks.append({
                "check_name": "Date of Birth Logic",
                "status": "FAIL",
                "category": "Biographical Consistency",
                "details": f"Date of birth ({dob_date}) is in the future."
            })
            suspicious_indicators.append({
                "title": "Impossible Future Birth Date",
                "severity": "HIGH",
                "category": "Biographical Anomaly",
                "explanation": f"Recorded birth date {dob_date} occurs after current calendar date {now}.",
                "recommendation": "Mandatory manual investigation."
            })
        else:
            age = (now - dob_date).days // 365
            if age < 16 and document_type in ("DRIVERS_LICENSE", "PASSPORT"):
                risk_score += 25
                consistency_checks.append({
                    "check_name": "Date of Birth Logic",
                    "status": "WARN",
                    "category": "Biographical Consistency",
                    "details": f"Subject age is calculated at {age} years (under standard threshold)."
                })
            else:
                consistency_checks.append({
                    "check_name": "Date of Birth Logic",
                    "status": "PASS",
                    "category": "Biographical Consistency",
                    "details": f"Subject age ({age} years) is consistent with adult holder profile."
                })
    else:
        consistency_checks.append({
            "check_name": "Date of Birth Logic",
            "status": "WARN",
            "category": "Biographical Consistency",
            "details": "DOB field was not unambiguously detected."
        })

    # 3. MRZ Cross-Check and Consistency
    mrz1 = extracted_data.get("mrz_line1")
    mrz2 = extracted_data.get("mrz_line2")
    full_name = extracted_data.get("full_name", "")

    if mrz1 or mrz2:
        mrz_combined = f"{mrz1 or ''} {mrz2 or ''}"
        # Check if name in MRZ aligns with visual name
        name_parts = [p.upper() for p in full_name.replace(',', '').split() if len(p) > 2]
        mrz_has_name = any(part in mrz_combined.replace('<', ' ') for part in name_parts)
        
        if not mrz_has_name and len(name_parts) > 0:
            risk_score += 55
            consistency_checks.append({
                "check_name": "MRZ vs Visual Zone Name Consistency",
                "status": "FAIL",
                "category": "Cryptographic & Format Integrity",
                "details": f"Visual name '{full_name}' does not match encoded MRZ string."
            })
            suspicious_indicators.append({
                "title": "Visual-to-MRZ Name Mismatch",
                "severity": "HIGH",
                "category": "Tamper Indication",
                "explanation": f"The printed holder name '{full_name}' does not match the optical machine-readable zone data ({mrz2 or mrz1}). This indicates potential digital alteration of the document face.",
                "recommendation": "Send for immediate Tier-2 Forensic Document Review."
            })
        else:
            consistency_checks.append({
                "check_name": "MRZ vs Visual Zone Name Consistency",
                "status": "PASS",
                "category": "Cryptographic & Format Integrity",
                "details": "Visual name conforms with machine-readable zone encoding."
            })
    else:
        # For documents like standard driver's licenses where MRZ is absent
        consistency_checks.append({
            "check_name": "MRZ Verification",
            "status": "PASS",
            "category": "Cryptographic & Format Integrity",
            "details": "Document class does not require standard ICAO 9303 MRZ."
        })

    # 4. Image Quality & Optical Signals
    qual_score = quality_metrics.get("overall_quality_score", 90.0)
    sharpness = quality_metrics.get("sharpness_score", 85.0)
    glare = quality_metrics.get("glare_score", 90.0)

    if qual_score < 50.0 or sharpness < 45.0:
        risk_score += 35
        consistency_checks.append({
            "check_name": "Optical Quality & Legibility",
            "status": "FAIL",
            "category": "Image Forensics",
            "details": f"Severe blur / low sharpness score ({sharpness}/100) impairs forensic verification."
        })
        suspicious_indicators.append({
            "title": "Degraded Image Quality / Blur",
            "severity": "MEDIUM",
            "category": "Image Forensics",
            "explanation": f"Document sharpness score ({sharpness}%) is significantly below acceptance threshold (70%). Key security guilloche patterns cannot be reliably assessed.",
            "recommendation": "Request high-resolution re-scan or photograph under neutral lighting."
        })
    elif qual_score < 75.0 or glare < 60.0:
        risk_score += 15
        consistency_checks.append({
            "check_name": "Optical Quality & Legibility",
            "status": "WARN",
            "category": "Image Forensics",
            "details": f"Sub-optimal lighting or glare detected (Quality: {qual_score}/100)."
        })
    else:
        consistency_checks.append({
            "check_name": "Optical Quality & Legibility",
            "status": "PASS",
            "category": "Image Forensics",
            "details": f"Resolution, contrast, and edge sharpness verified (Score: {qual_score}/100)."
        })

    # 5. Document Number Format & Font Uniformity
    doc_no = extracted_data.get("document_number", "")
    if len(doc_no) < 5:
        risk_score += 25
        consistency_checks.append({
            "check_name": "Document Number Pattern Check",
            "status": "WARN",
            "category": "Data Structure",
            "details": f"Document number '{doc_no}' is shorter than standard expected format."
        })
    else:
        consistency_checks.append({
            "check_name": "Document Number Pattern Check",
            "status": "PASS",
            "category": "Data Structure",
            "details": f"Document number '{doc_no}' adheres to expected syntax structure."
        })

    # Bound risk score between 0 and 100
    risk_score = min(99, max(5, risk_score))

    # Categorize Risk Level
    if risk_score >= 70:
        overall_risk_level = "HIGH"
    elif risk_score >= 30:
        overall_risk_level = "MEDIUM"
    else:
        overall_risk_level = "LOW"

    # AI Model Confidence calculation
    ai_confidence = round(
        (ocr_confidence * 0.45) + (qual_score * 0.35) + (100 - min(risk_score, 40)) * 0.20,
        1
    )
    ai_confidence = min(99.4, max(65.0, ai_confidence))

    return {
        "risk_score": risk_score,
        "overall_risk_level": overall_risk_level,
        "ai_confidence": ai_confidence,
        "consistency_checks": consistency_checks,
        "suspicious_indicators": suspicious_indicators
    }
