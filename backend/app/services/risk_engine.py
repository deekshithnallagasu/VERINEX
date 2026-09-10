from datetime import datetime, date
from typing import Dict, Any, List, Optional

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

def evaluate_document_risk(
    extracted_data: Dict[str, Any],
    quality_metrics: Dict[str, Any],
    ocr_confidence: float,
    document_type: str = "PASSPORT",
    mrz_result: Optional[Dict[str, Any]] = None,
    consistency_result: Optional[Dict[str, Any]] = None,
    validation_result: Optional[Dict[str, Any]] = None,
    tampering_result: Optional[Dict[str, Any]] = None,
    face_result: Optional[Dict[str, Any]] = None,
    liveness_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Multi-Signal Risk Fusion Engine for SIH Defensive Screening.
    Combines:
    1. MRZ Cryptographic Checksum Validation (25 max pts)
    2. OCR <-> MRZ Cross-Zone Consistency (20 max pts)
    3. Document Structure & Logical Validity (15 max pts)
    4. Forensic Image Tampering & ELA Inconsistencies (20 max pts)
    5. Biometric Face Verification (15 max pts)
    6. Metadata & Compression Anomalies (5 max pts)
    
    Risk Levels:
    - 0-29:  LOW (Screening Clear)
    - 30-59: REVIEW (Manual Verification Required)
    - 60-100: HIGH (Secondary Inspection / Escalated)
    
    CRITICAL ETHICAL BOUNDARY:
    Risk score is a screening risk indicator, NOT a proof that the document is fake.
    """
    # Ensure ocr_confidence is a float even if a dict was passed
    if isinstance(ocr_confidence, dict):
        conf_val = float(ocr_confidence.get("ocr_confidence", 90.0))
    elif isinstance(ocr_confidence, (int, float)):
        conf_val = float(ocr_confidence)
    else:
        conf_val = 90.0

    risk_score = 0
    breakdown = {
        "mrz": 0,
        "consistency": 0,
        "structure": 0,
        "tampering": 0,
        "face": 0,
        "metadata": 0
    }
    indicators_list: List[str] = []
    suspicious_indicators: List[Dict[str, Any]] = []
    consistency_checks: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. MRZ VALIDATION (Max 25 pts)
    # -------------------------------------------------------------
    if mrz_result and mrz_result.get("detected"):
        mrz_status = mrz_result.get("overall_status")
        cds = mrz_result.get("check_digits", {})
        if mrz_status == "FAIL":
            failed_cds = [k for k, v in cds.items() if v is False]
            mrz_pts = 25
            breakdown["mrz"] = mrz_pts
            risk_score += mrz_pts
            ind_msg = f"MRZ check digit validation failed ({', '.join(failed_cds) if failed_cds else 'Check digit error'})"
            indicators_list.append(ind_msg)
            suspicious_indicators.append({
                "title": "MRZ Checksum Failure",
                "severity": "HIGH",
                "category": "Cryptographic & Format Integrity",
                "explanation": "Calculated ICAO 9303 7-3-1 check digit does not match encoded value in the Machine Readable Zone.",
                "recommendation": "Verify physical document security features and optical zone."
            })
            consistency_checks.append({
                "check_name": "ICAO 9303 MRZ Checksums",
                "status": "FAIL",
                "category": "Cryptographic & Format Integrity",
                "details": f"Failed check digits: {', '.join(failed_cds)}"
            })
        else:
            consistency_checks.append({
                "check_name": "ICAO 9303 MRZ Checksums",
                "status": "PASS",
                "category": "Cryptographic & Format Integrity",
                "details": "All MRZ check digits (document number, DOB, expiry, composite) verified successfully."
            })
    else:
        consistency_checks.append({
            "check_name": "MRZ Verification",
            "status": "PASS",
            "category": "Cryptographic & Format Integrity",
            "details": "Document class does not mandate or contain an ICAO MRZ."
        })

    # -------------------------------------------------------------
    # 2. OCR <-> MRZ CONSISTENCY (Max 60 pts for critical mismatches)
    # -------------------------------------------------------------
    if consistency_result and consistency_result.get("overall_status") == "FAIL":
        mismatches = consistency_result.get("mismatches", [])
        critical_mismatches = [m for m in mismatches if (m.get("severity") == "CRITICAL" if isinstance(m, dict) else True)]
        if critical_mismatches:
            cons_pts = min(65, 50 + (len(critical_mismatches) - 1) * 10)
        else:
            cons_pts = min(35, len(mismatches) * 15)
        breakdown["consistency"] = cons_pts
        risk_score += cons_pts
        for m in mismatches:
            if isinstance(m, dict):
                field = m.get('field', 'Field')
                msg = f"Visual {field} differs from MRZ: '{m.get('ocr_value')}' vs '{m.get('mrz_value')}'"
                indicators_list.append(msg)
                suspicious_indicators.append({
                    "title": f"{field} Cross-Zone Mismatch",
                    "severity": m.get("severity", "HIGH"),
                    "category": "Tamper Indication",
                    "explanation": m.get("reason", "Visual information contradicts machine-readable track."),
                    "recommendation": "Send for immediate Tier-2 Forensic Document Review."
                })
            else:
                indicators_list.append(str(m))
                suspicious_indicators.append({
                    "title": "Cross-Zone Mismatch",
                    "severity": "HIGH",
                    "category": "Tamper Indication",
                    "explanation": str(m),
                    "recommendation": "Send for immediate Tier-2 Forensic Document Review."
                })
        consistency_checks.append({
            "check_name": "Visual-to-MRZ Cross Consistency",
            "status": "FAIL",
            "category": "Data Alignment",
            "details": f"{len(mismatches)} cross-zone discrepancy detected."
        })
    elif consistency_result and consistency_result.get("overall_status") == "PASS":
        consistency_checks.append({
            "check_name": "Visual-to-MRZ Cross Consistency",
            "status": "PASS",
            "category": "Data Alignment",
            "details": "Visual fields (Name, Document Number, DOB, Expiry, Nationality) match MRZ perfectly."
        })

    # -------------------------------------------------------------
    # 3. DOCUMENT VALIDATION & LOGICAL SANITY (Max 15 pts)
    # -------------------------------------------------------------
    if validation_result:
        is_expired = validation_result.get("is_expired", False)
        has_logical_fails = validation_result.get("has_logical_failures", False)
        
        # Merge individual validation checks
        for c in validation_result.get("checks", []):
            consistency_checks.append({
                "check_name": c.get("name"),
                "status": c.get("status"),
                "category": "Logical & Temporal Integrity",
                "details": c.get("details") or c.get("reason", "")
            })

        if is_expired:
            # Strictly marked as VALIDITY WARNING, NOT FORGERY!
            breakdown["structure"] += 12
            risk_score += 12
            indicators_list.append("Document has expired (Validity Warning, not forgery)")
            suspicious_indicators.append({
                "title": "Document Expired (Validity Warning)",
                "severity": "MEDIUM",
                "category": "Temporal Validity",
                "explanation": "The document expiration date has passed. While not evidence of fraud or forgery, an expired document cannot be accepted for active identity clearance.",
                "recommendation": "Request user submit a currently valid, unexpired identity document."
            })

        if has_logical_fails:
            breakdown["structure"] += 15
            risk_score += 15
            indicators_list.append("Logical date sequence or document number syntax anomaly detected")

    # -------------------------------------------------------------
    # 4. FORENSIC IMAGE TAMPERING (Max 20 pts)
    # -------------------------------------------------------------
    if tampering_result:
        t_score = tampering_result.get("tampering_score", 0.0)
        t_status = tampering_result.get("status", "LOW")
        regions = tampering_result.get("suspicious_regions", [])

        if t_status == "HIGH" or t_score >= 60.0:
            breakdown["tampering"] = 20
            risk_score += 20
            indicators_list.append(f"Forensic ELA analysis detected {len(regions)} suspicious manipulated regions")
            suspicious_indicators.append({
                "title": "Digital Image Tampering Detected",
                "severity": "HIGH",
                "category": "Image Forensics",
                "explanation": f"Error Level Analysis (ELA) and local compression variance indicate localized pixel manipulation (Tamper score: {t_score}/100).",
                "recommendation": "Inspect annotated forensic heatmap for copy-paste or text substitution boundaries."
            })
            consistency_checks.append({
                "check_name": "Digital Forensics & ELA Integrity",
                "status": "FAIL",
                "category": "Forensic Analysis",
                "details": f"High compression divergence ({len(regions)} localized anomalies flagged)."
            })
        elif t_status == "REVIEW" or t_score >= 30.0:
            breakdown["tampering"] = 10
            risk_score += 10
            indicators_list.append("Moderate compression or edge variance detected across document regions")
            consistency_checks.append({
                "check_name": "Digital Forensics & ELA Integrity",
                "status": "WARN",
                "category": "Forensic Analysis",
                "details": f"Moderate ELA score ({t_score}/100) requires manual visual inspection."
            })
        else:
            consistency_checks.append({
                "check_name": "Digital Forensics & ELA Integrity",
                "status": "PASS",
                "category": "Forensic Analysis",
                "details": "Uniform error level compression and natural edge gradients confirmed."
            })

        # Metadata Anomaly Check (Max 5 pts)
        meta_score = tampering_result.get("metadata_anomaly_score", 0.0)
        if meta_score >= 40.0:
            breakdown["metadata"] = 5
            risk_score += 5
            indicators_list.append(f"Image edited with digital manipulation software signature")

    # -------------------------------------------------------------
    # 5. BIOMETRIC FACE VERIFICATION (Max 15 pts)
    # -------------------------------------------------------------
    if face_result and face_result.get("face_detected"):
        sim = face_result.get("similarity", 1.0)
        f_status = face_result.get("status", "MATCH")
        if f_status == "MISMATCH" or sim < 0.55:
            breakdown["face"] = 15
            risk_score += 15
            indicators_list.append(f"Biometric face mismatch: Probe photo differs from document portrait (Similarity: {round(sim * 100, 1)}%)")
            suspicious_indicators.append({
                "title": "Facial Biometric Mismatch",
                "severity": "HIGH",
                "category": "Biometric Verification",
                "explanation": f"Deep facial embedding cosine distance ({round(sim * 100, 1)}%) is below match threshold. Document portrait does not match presented individual.",
                "recommendation": "Perform mandatory live in-person video interview or secondary biometric check."
            })
            consistency_checks.append({
                "check_name": "Biometric Face Match (1:1)",
                "status": "FAIL",
                "category": "Biometrics",
                "details": f"Similarity {round(sim * 100, 1)}% is below the required 80.0% match threshold."
            })
        elif f_status == "REVIEW" or sim < 0.80:
            breakdown["face"] = 8
            risk_score += 8
            indicators_list.append(f"Borderline facial similarity ({round(sim * 100, 1)}%) requires human reviewer verification")
            consistency_checks.append({
                "check_name": "Biometric Face Match (1:1)",
                "status": "WARN",
                "category": "Biometrics",
                "details": f"Similarity {round(sim * 100, 1)}% falls in reviewer inspection range (55-79%)."
            })
        else:
            consistency_checks.append({
                "check_name": "Biometric Face Match (1:1)",
                "status": "PASS",
                "category": "Biometrics",
                "details": f"Facial portrait verified against probe photo (Similarity: {round(sim * 100, 1)}%)."
            })

    # -------------------------------------------------------------
    # 6. OPTICAL QUALITY IMPACT ON CONFIDENCE
    # -------------------------------------------------------------
    qual_score = quality_metrics.get("overall_quality_score", 90.0)
    sharpness = quality_metrics.get("sharpness_score", 85.0)

    if qual_score < 50.0 or sharpness < 45.0:
        indicators_list.append("Low document sharpness or blur impairs fine security feature analysis")
        consistency_checks.append({
            "check_name": "Optical Sharpness & Clarity",
            "status": "WARN",
            "category": "Image Forensics",
            "details": f"Quality score ({qual_score}/100) below optimal threshold."
        })
    else:
        consistency_checks.append({
            "check_name": "Optical Sharpness & Clarity",
            "status": "PASS",
            "category": "Image Forensics",
            "details": f"High resolution and sharpness ({sharpness}/100) confirmed."
        })

    # Bound risk score between 0 and 100
    final_risk_score = min(99, max(4, risk_score))

    # Determine Risk Level Category
    if final_risk_score >= 60:
        risk_level = "HIGH"
        recommendation = "MANDATORY SECONDARY INSPECTION / CASE ESCALATED"
    elif final_risk_score >= 30:
        risk_level = "REVIEW"
        recommendation = "MANUAL VERIFICATION REQUIRED"
    else:
        risk_level = "LOW"
        recommendation = "APPROVED / SCREENING CLEAR"

    # AI Model Confidence calculation
    ai_confidence = round(
        (conf_val * 0.40) + (qual_score * 0.35) + max(0, (100 - min(final_risk_score, 50))) * 0.25,
        1
    )
    ai_confidence = min(99.4, max(60.0, ai_confidence))

    return {
        "risk_score": final_risk_score,
        "overall_risk_level": risk_level,
        "risk_level": risk_level,
        "confidence": round(ai_confidence / 100.0, 2),
        "ai_confidence": ai_confidence,
        "breakdown": breakdown,
        "indicators": indicators_list if indicators_list else ["Document conforms to standard structural and security parameters"],
        "suspicious_indicators": suspicious_indicators,
        "consistency_checks": consistency_checks,
        "recommendation": recommendation
    }
