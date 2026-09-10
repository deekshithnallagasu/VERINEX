import re
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher

def clean_alphanumeric(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r'[^A-Z0-9]', '', str(text).upper())

def fuzzy_similarity(s1: str, s2: str) -> float:
    if not s1 or not s2:
        return 0.0
    return SequenceMatcher(None, s1.upper(), s2.upper()).ratio()

def compare_names(ocr_name: Optional[str], mrz_name: Optional[str]) -> TupleBoolReason:
    if not ocr_name or not mrz_name:
        return False, "One or both names missing"

    clean_ocr = clean_alphanumeric(ocr_name)
    clean_mrz = clean_alphanumeric(mrz_name)

    # 1. Exact alphanumeric match
    if clean_ocr == clean_mrz:
        return True, "Exact name match"

    # 2. Token subset match (e.g. "Clara Eleanor Abernathy" vs "Abernathy Clara")
    ocr_tokens = set(re.findall(r'[A-Z0-9]+', ocr_name.upper()))
    mrz_tokens = set(re.findall(r'[A-Z0-9]+', mrz_name.upper()))
    if ocr_tokens and mrz_tokens:
        overlap = len(ocr_tokens.intersection(mrz_tokens))
        if overlap >= min(len(ocr_tokens), len(mrz_tokens)):
            return True, f"Full token overlap ({overlap} tokens match)"

    # Check if sub-tokens of one name exist inside the other
    ocr_in_mrz = all(token in clean_mrz for token in ocr_tokens if len(token) >= 3)
    if ocr_tokens and ocr_in_mrz:
        return True, "All name components found in MRZ zone"

    # 3. Fuzzy similarity
    sim = fuzzy_similarity(clean_ocr, clean_mrz)
    if sim >= 0.70:
        return True, f"Fuzzy phonetic/string similarity {round(sim * 100, 1)}%"

    return False, f"Name mismatch: visual '{ocr_name}' vs MRZ '{mrz_name}' (similarity: {round(sim * 100, 1)}%)"

def compare_dates(ocr_date: Optional[str], mrz_date: Optional[str]) -> TupleBoolReason:
    if not ocr_date or not mrz_date:
        return False, "One or both dates missing"

    # Clean dates to digits
    d1 = re.sub(r'[^0-9]', '', str(ocr_date))
    d2 = re.sub(r'[^0-9]', '', str(mrz_date))

    # Exact digit match (e.g. 19890514 == 19890514)
    if d1 == d2:
        return True, "Exact match"

    # YYMMDD vs YYYYMMDD
    if len(d1) == 8 and len(d2) == 6 and d1[2:] == d2:
        return True, "Matching date (century aligned)"
    if len(d2) == 8 and len(d1) == 6 and d2[2:] == d1:
        return True, "Matching date (century aligned)"

    return False, f"Date mismatch: visual '{ocr_date}' vs MRZ '{mrz_date}'"

def compare_nationalities(ocr_nat: Optional[str], mrz_nat: Optional[str]) -> TupleBoolReason:
    if not ocr_nat or not mrz_nat:
        return True, "Nationality field omitted in visual zone"

    c_ocr = clean_alphanumeric(ocr_nat)
    c_mrz = clean_alphanumeric(mrz_nat)

    if c_ocr == c_mrz:
        return True, "Exact code match"

    # Common country aliases (e.g. USA vs United States of America)
    aliases = {
        "USA": ["UNITEDSTATES", "UNITEDSTATESOFAMERICA", "AMERICA", "US"],
        "GBR": ["UNITEDKINGDOM", "GREATBRITAIN", "BRITISH", "UK"],
        "CAN": ["CANADA", "CANADIAN"],
        "IND": ["INDIA", "INDIAN"],
        "DEU": ["GERMANY", "DEUTSCHLAND"],
        "FRA": ["FRANCE", "FRENCH"],
        "PRT": ["PORTUGAL", "PORTUGUESE"],
        "MET": ["METROPOLIS", "REPUBLICOFMETROPOLIS"]
    }

    if c_mrz in aliases:
        for alias in aliases[c_mrz]:
            if alias in c_ocr or c_ocr in alias:
                return True, f"Recognized country alias match ({c_mrz} - {ocr_nat})"

    sim = fuzzy_similarity(c_ocr, c_mrz)
    if sim >= 0.7:
        return True, f"Similarity {round(sim*100, 1)}%"

    return False, f"Nationality mismatch: visual '{ocr_nat}' vs MRZ '{mrz_nat}'"

class TupleBoolReason:
    def __init__(self, match: bool, reason: str):
        self.match = match
        self.reason = reason
    def __iter__(self):
        yield self.match
        yield self.reason

def verify_ocr_mrz_consistency(
    extracted_ocr: Dict[str, Any],
    mrz_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs cross-zone cross-validation between visual OCR fields and parsed MRZ.
    Checks:
    - Document Number
    - Full Name (using fuzzy & token set matching)
    - Date of Birth
    - Expiry Date
    - Nationality
    """
    if not mrz_result or not mrz_result.get("detected"):
        return {
            "name_match": True,
            "document_number_match": True,
            "dob_match": True,
            "expiry_match": True,
            "nationality_match": True,
            "overall_status": "NOT_APPLICABLE",
            "mismatches": [],
            "notice": "Document does not have a detectable MRZ zone; cross-zone comparison skipped."
        }

    mrz_data = mrz_result.get("parsed", {})
    mismatches = []

    # 1. Document Number Check
    ocr_doc_num = clean_alphanumeric(extracted_ocr.get("document_number"))
    mrz_doc_num = clean_alphanumeric(mrz_data.get("document_number"))
    doc_num_match = False
    doc_num_reason = ""

    if ocr_doc_num and mrz_doc_num:
        if ocr_doc_num == mrz_doc_num:
            doc_num_match = True
            doc_num_reason = "Exact match"
        elif ocr_doc_num in mrz_doc_num or mrz_doc_num in ocr_doc_num:
            doc_num_match = True
            doc_num_reason = "Prefix/substring match"
        else:
            doc_num_match = False
            doc_num_reason = f"Mismatch: visual '{ocr_doc_num}' vs MRZ '{mrz_doc_num}'"
            mismatches.append({
                "field": "Document Number",
                "ocr_value": extracted_ocr.get("document_number"),
                "mrz_value": mrz_data.get("document_number"),
                "severity": "CRITICAL",
                "reason": doc_num_reason
            })
    else:
        doc_num_match = True
        doc_num_reason = "Document number omitted in one zone"

    # 2. Name Check
    name_match, name_reason = compare_names(
        extracted_ocr.get("full_name"),
        mrz_data.get("full_name") or f"{mrz_data.get('surname', '')} {mrz_data.get('given_names', '')}".strip()
    )
    if not name_match:
        mismatches.append({
            "field": "Full Name",
            "ocr_value": extracted_ocr.get("full_name"),
            "mrz_value": mrz_data.get("full_name"),
            "severity": "CRITICAL",
            "reason": name_reason
        })

    # 3. DOB Check
    dob_match, dob_reason = compare_dates(
        extracted_ocr.get("date_of_birth"),
        mrz_data.get("date_of_birth") or mrz_data.get("date_of_birth_raw")
    )
    if not dob_match and extracted_ocr.get("date_of_birth"):
        mismatches.append({
            "field": "Date of Birth",
            "ocr_value": extracted_ocr.get("date_of_birth"),
            "mrz_value": mrz_data.get("date_of_birth"),
            "severity": "HIGH",
            "reason": dob_reason
        })

    # 4. Expiry Date Check
    exp_match, exp_reason = compare_dates(
        extracted_ocr.get("expiry_date"),
        mrz_data.get("expiry_date") or mrz_data.get("expiry_date_raw")
    )
    if not exp_match and extracted_ocr.get("expiry_date"):
        mismatches.append({
            "field": "Expiry Date",
            "ocr_value": extracted_ocr.get("expiry_date"),
            "mrz_value": mrz_data.get("expiry_date"),
            "severity": "HIGH",
            "reason": exp_reason
        })

    # 5. Nationality Check
    nat_match, nat_reason = compare_nationalities(
        extracted_ocr.get("nationality"),
        mrz_data.get("nationality")
    )
    if not nat_match:
        mismatches.append({
            "field": "Nationality",
            "ocr_value": extracted_ocr.get("nationality"),
            "mrz_value": mrz_data.get("nationality"),
            "severity": "MEDIUM",
            "reason": nat_reason
        })

    all_passed = (len(mismatches) == 0)

    return {
        "name_match": name_match,
        "name_details": name_reason,
        "document_number_match": doc_num_match,
        "document_number_details": doc_num_reason,
        "dob_match": dob_match,
        "dob_details": dob_reason,
        "expiry_match": exp_match,
        "expiry_details": exp_reason,
        "nationality_match": nat_match,
        "nationality_details": nat_reason,
        "overall_status": "PASS" if all_passed else "FAIL",
        "mismatches": mismatches
    }
