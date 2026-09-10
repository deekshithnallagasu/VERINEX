import re
from datetime import datetime, date
from typing import Dict, Any, List, Optional

def parse_flexible_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    
    clean_str = re.sub(r'[^A-Za-z0-9]', ' ', str(date_str)).strip()
    
    # Common formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, DD MMM YYYY, etc.
    formats = [
        "%Y %m %d",
        "%d %m %Y",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%Y %b %d",
        "%Y%m%d",
        "%d%m%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(clean_str, fmt).date()
        except ValueError:
            pass
    return None

def validate_document_logic(
    extracted_data: Dict[str, Any],
    document_template: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs logical sanity checks on identity fields:
    - DOB validity, future date check, age plausibility
    - Issue date validity & future date check
    - Expiry date validity
    - Expiry >= Issue date
    - Expiration check (classified strictly as VALIDITY WARNING, NOT FORGERY)
    - Document number length & format
    - Required field completeness
    """
    today = date.today()
    checks = []
    validity_warnings = []
    is_expired = False

    dob_val = extracted_data.get("date_of_birth")
    issue_val = extracted_data.get("issue_date")
    exp_val = extracted_data.get("expiry_date")
    doc_num = extracted_data.get("document_number")

    dob_dt = parse_flexible_date(dob_val)
    issue_dt = parse_flexible_date(issue_val)
    exp_dt = parse_flexible_date(exp_val)

    # 1. Date of Birth Check
    if dob_dt:
        if dob_dt > today:
            checks.append({
                "name": "Date of Birth Plausibility",
                "status": "FAIL",
                "reason": f"Date of birth ({dob_dt}) is in the future"
            })
        else:
            age = today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
            if age > 125:
                checks.append({
                    "name": "Date of Birth Plausibility",
                    "status": "WARNING",
                    "reason": f"Calculated age ({age} years) is unusually high"
                })
            else:
                checks.append({
                    "name": "Date of Birth Plausibility",
                    "status": "PASS",
                    "details": f"Valid date of birth (Holder age: {age} years)"
                })
    else:
        checks.append({
            "name": "Date of Birth Plausibility",
            "status": "WARNING" if dob_val else "PASS",
            "reason": "Date of birth could not be formatted into standard calendar date" if dob_val else "Not provided"
        })

    # 2. Issue Date Check
    if issue_dt:
        if issue_dt > today:
            checks.append({
                "name": "Issue Date Validity",
                "status": "WARNING",
                "reason": f"Document issue date ({issue_dt}) is recorded in the future"
            })
        else:
            checks.append({
                "name": "Issue Date Validity",
                "status": "PASS",
                "details": f"Document issued on {issue_dt}"
            })

    # 3. Expiry Date & Expiration Status Check
    if exp_dt:
        if exp_dt < today:
            is_expired = True
            validity_warnings.append(f"Document expired on {exp_dt}")
            checks.append({
                "name": "Document Expiry Status",
                "status": "WARNING",
                "reason": f"Document expired on {exp_dt}. Document validity lapsed; this is a compliance warning, NOT evidence of forgery."
            })
        else:
            checks.append({
                "name": "Document Expiry Status",
                "status": "PASS",
                "details": f"Document is currently valid until {exp_dt}"
            })
    elif exp_val:
        checks.append({
            "name": "Document Expiry Status",
            "status": "WARNING",
            "reason": f"Unrecognized expiry format '{exp_val}'"
        })
    else:
        checks.append({
            "name": "Document Expiry Status",
            "status": "PASS",
            "details": "Expiry date not applicable or not provided"
        })

    # 4. Date Chronology Check (Expiry >= Issue)
    if issue_dt and exp_dt:
        if exp_dt < issue_dt:
            checks.append({
                "name": "Chronological Consistency",
                "status": "FAIL",
                "reason": f"Expiration date ({exp_dt}) precedes issue date ({issue_dt})"
            })
        else:
            validity_duration_years = round((exp_dt - issue_dt).days / 365.25, 1)
            checks.append({
                "name": "Chronological Consistency",
                "status": "PASS",
                "details": f"Logical date sequence confirmed ({validity_duration_years} year validity span)"
            })

    # 5. Document Number Format Check
    if doc_num:
        clean_num = re.sub(r'[^A-Z0-9]', '', str(doc_num).upper())
        if len(clean_num) >= 5:
            checks.append({
                "name": "Document Number Syntax",
                "status": "PASS",
                "details": f"Valid syntax ({len(clean_num)} alphanumeric characters)"
            })
        else:
            checks.append({
                "name": "Document Number Syntax",
                "status": "WARNING",
                "reason": f"Document number '{doc_num}' is unusually short"
            })
    else:
        checks.append({
            "name": "Document Number Syntax",
            "status": "FAIL",
            "reason": "Document identifier missing or unreadable"
        })

    # 6. Required Fields Completeness Check
    if isinstance(document_template, dict):
        req_fields = document_template.get("required_fields") or ["document_number", "full_name"]
    else:
        req_fields = ["document_number", "full_name"]
    missing_req = []
    for f in req_fields:
        val = extracted_data.get(f)
        if not val or val == "None" or val == "Unspecified":
            missing_req.append(f)

    if missing_req:
        checks.append({
            "name": "Required Field Presence",
            "status": "WARNING",
            "reason": f"Missing expected fields: {', '.join(missing_req)}"
        })
    else:
        checks.append({
            "name": "Required Field Presence",
            "status": "PASS",
            "details": f"All {len(req_fields)} required fields successfully identified"
        })

    has_failures = any(c["status"] == "FAIL" for c in checks)
    if has_failures:
        overall_status = "FAIL"
    elif is_expired or validity_warnings:
        overall_status = "VALIDITY_WARNING"
    else:
        overall_status = "VALID"

    return {
        "status": overall_status,
        "checks": checks,
        "is_expired": is_expired,
        "validity_warnings": validity_warnings,
        "has_logical_failures": has_failures
    }
