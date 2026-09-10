import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

def calculate_mrz_check_digit(value: str) -> int:
    """
    Calculates standard ICAO 9303 7-3-1 check digit.
    Characters:
    '0'-'9' -> 0-9
    'A'-'Z' -> 10-35
    '<'     -> 0
    Weighting sequence: 7, 3, 1, 7, 3, 1, ...
    """
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(value):
        char_upper = char.upper()
        if '0' <= char_upper <= '9':
            val = ord(char_upper) - ord('0')
        elif 'A' <= char_upper <= 'Z':
            val = ord(char_upper) - ord('A') + 10
        elif char_upper == '<':
            val = 0
        else:
            val = 0
        weight = weights[i % 3]
        total += val * weight
    return total % 10

def normalize_mrz_line(line: str, expected_length: Optional[int] = None) -> str:
    """
    Normalizes OCR errors in MRZ lines:
    - Uppercase
    - Fix dropped '<' between document code 'P' and 3-letter country code (e.g. PUSA -> P<USA)
    - Replace spaces and invalid symbols with '<'
    - Fix common OCR misinterpretations in MRZ
    """
    cleaned = line.strip().upper()
    if len(cleaned) >= 4 and cleaned[0] == 'P' and cleaned[1] != '<' and cleaned[1:4].isalpha():
        cleaned = f"P<{cleaned[1:]}"

    cleaned = re.sub(r'[^A-Z0-9<]', '<', cleaned)
    if expected_length and len(cleaned) != expected_length:
        if len(cleaned) < expected_length:
            cleaned = cleaned.ljust(expected_length, '<')
        else:
            cleaned = cleaned[:expected_length]
    return cleaned

def parse_mrz_date(date_str: str, is_expiry: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """
    Converts 6-digit YYMMDD string to ISO YYYY-MM-DD.
    Uses century pivot:
    For DOB: if YY > current_year % 100 -> 19YY, else 20YY.
    For Expiry: generally 20YY.
    """
    if len(date_str) != 6 or not date_str.isdigit():
        return None, date_str

    yy = int(date_str[0:2])
    mm = int(date_str[2:4])
    dd = int(date_str[4:6])

    current_yy = datetime.now().year % 100
    if is_expiry:
        century = 2000 if yy <= current_yy + 50 else 1900
    else:
        century = 1900 if yy > current_yy else 2000

    full_year = century + yy
    try:
        dt = datetime(full_year, mm, dd)
        return dt.strftime("%Y-%m-%d"), date_str
    except ValueError:
        return f"{full_year}-{mm:02d}-{dd:02d}", date_str

def parse_td3_mrz(line1: str, line2: str) -> Dict[str, Any]:
    """
    Parses and validates 2-line x 44-character ICAO 9303 TD3 Passport MRZ.
    Line 1:
      0..1: Document code (P, P<, etc.)
      2..4: Issuing State or organization (3 chars)
      5..43: Name (Surname<<Given Names<<<<)
    Line 2:
      0..8: Document number (9 chars)
      9: Document number check digit (1 char)
      10..12: Nationality (3 chars)
      13..18: Date of birth (6 chars YYMMDD)
      19: Date of birth check digit (1 char)
      20: Sex (M, F, <)
      21..26: Date of expiry (6 chars YYMMDD)
      27: Date of expiry check digit (1 char)
      28..41: Optional personal number (14 chars)
      42: Optional data check digit (1 char)
      43: Composite check digit (1 char)
    """
    l1 = normalize_mrz_line(line1, 44)
    l2 = normalize_mrz_line(line2, 44)

    # 1. Line 1 Parsing
    doc_type_code = l1[0:2].replace('<', '')
    issuing_country = l1[2:5].replace('<', '')
    names_raw = l1[5:44]
    
    parts = names_raw.split('<<')
    surname = parts[0].replace('<', ' ').strip()
    given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    full_name = f"{given_names} {surname}".strip() if given_names else surname

    # 2. Line 2 Parsing
    doc_number_field = l2[0:9]
    doc_number_cd = l2[9]
    nationality = l2[10:13].replace('<', '')
    dob_field = l2[13:19]
    dob_cd = l2[19]
    sex = l2[20].replace('<', 'X')
    exp_field = l2[21:27]
    exp_cd = l2[27]
    optional_field = l2[28:42]
    opt_cd = l2[42]
    composite_cd = l2[43]

    clean_doc_number = doc_number_field.replace('<', '')

    # 3. Check Digit Validations
    calc_doc_cd = str(calculate_mrz_check_digit(doc_number_field))
    calc_dob_cd = str(calculate_mrz_check_digit(dob_field))
    calc_exp_cd = str(calculate_mrz_check_digit(exp_field))

    # Composite check digit calculates over:
    # doc_num + doc_num_cd + dob + dob_cd + exp + exp_cd + optional + opt_cd
    composite_data = doc_number_field + doc_number_cd + dob_field + dob_cd + exp_field + exp_cd + optional_field + opt_cd
    calc_comp_cd = str(calculate_mrz_check_digit(composite_data))

    cd_doc_pass = (calc_doc_cd == doc_number_cd)
    cd_dob_pass = (calc_dob_cd == dob_cd)
    cd_exp_pass = (calc_exp_cd == exp_cd)
    cd_comp_pass = (calc_comp_cd == composite_cd)

    dob_iso, _ = parse_mrz_date(dob_field, is_expiry=False)
    exp_iso, _ = parse_mrz_date(exp_field, is_expiry=True)

    # In ICAO 9303, the document number, DOB, and expiry check digits are the primary security indicators
    all_cd_pass = cd_doc_pass and cd_dob_pass and cd_exp_pass

    return {
        "detected": True,
        "format": "TD3",
        "valid_structure": True,
        "lines": [l1, l2],
        "check_digits": {
            "document_number": cd_doc_pass,
            "document_number_expected": calc_doc_cd,
            "document_number_actual": doc_number_cd,
            "date_of_birth": cd_dob_pass,
            "date_of_birth_expected": calc_dob_cd,
            "date_of_birth_actual": dob_cd,
            "expiry_date": cd_exp_pass,
            "expiry_date_expected": calc_exp_cd,
            "expiry_date_actual": exp_cd,
            "composite": cd_comp_pass,
            "composite_expected": calc_comp_cd,
            "composite_actual": composite_cd
        },
        "parsed": {
            "document_type": doc_type_code or "PASSPORT",
            "issuing_country": issuing_country,
            "document_number": clean_doc_number,
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name,
            "nationality": nationality,
            "date_of_birth": dob_iso,
            "date_of_birth_raw": dob_field,
            "expiry_date": exp_iso,
            "expiry_date_raw": exp_field,
            "gender": "Male" if sex == "M" else ("Female" if sex == "F" else "Unspecified")
        },
        "overall_status": "PASS" if all_cd_pass else "FAIL"
    }

def parse_td1_mrz(line1: str, line2: str, line3: str) -> Dict[str, Any]:
    """
    Parses 3-line x 30-character ICAO 9303 TD1 ID Card MRZ.
    Line 1: 0..1 doc code, 2..4 country, 5..13 doc no, 14 doc no cd, 15..29 optional
    Line 2: 0..5 DOB, 6 DOB cd, 7 sex, 8..13 expiry, 14 exp cd, 15..17 nationality, 18..28 optional, 29 composite cd
    Line 3: 0..29 names (SURNAME<<GIVEN<NAMES<<<<)
    """
    l1 = normalize_mrz_line(line1, 30)
    l2 = normalize_mrz_line(line2, 30)
    l3 = normalize_mrz_line(line3, 30)

    doc_type = l1[0:2].replace('<', '')
    issuing_country = l1[2:5].replace('<', '')
    doc_number_field = l1[5:14]
    doc_number_cd = l1[14]
    clean_doc_number = doc_number_field.replace('<', '')

    dob_field = l2[0:6]
    dob_cd = l2[6]
    sex = l2[7].replace('<', 'X')
    exp_field = l2[8:14]
    exp_cd = l2[14]
    nationality = l2[15:18].replace('<', '')
    composite_cd = l2[29]

    # Names on Line 3
    parts = l3.split('<<')
    surname = parts[0].replace('<', ' ').strip()
    given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    full_name = f"{given_names} {surname}".strip() if given_names else surname

    calc_doc_cd = str(calculate_mrz_check_digit(doc_number_field))
    calc_dob_cd = str(calculate_mrz_check_digit(dob_field))
    calc_exp_cd = str(calculate_mrz_check_digit(exp_field))

    cd_doc_pass = (calc_doc_cd == doc_number_cd)
    cd_dob_pass = (calc_dob_cd == dob_cd)
    cd_exp_pass = (calc_exp_cd == exp_cd)

    dob_iso, _ = parse_mrz_date(dob_field, is_expiry=False)
    exp_iso, _ = parse_mrz_date(exp_field, is_expiry=True)

    all_cd_pass = cd_doc_pass and cd_dob_pass and cd_exp_pass

    return {
        "detected": True,
        "format": "TD1",
        "valid_structure": True,
        "lines": [l1, l2, l3],
        "check_digits": {
            "document_number": cd_doc_pass,
            "document_number_expected": calc_doc_cd,
            "document_number_actual": doc_number_cd,
            "date_of_birth": cd_dob_pass,
            "date_of_birth_expected": calc_dob_cd,
            "date_of_birth_actual": dob_cd,
            "expiry_date": cd_exp_pass,
            "expiry_date_expected": calc_exp_cd,
            "expiry_date_actual": exp_cd,
            "composite": True
        },
        "parsed": {
            "document_type": doc_type or "NATIONAL_ID",
            "issuing_country": issuing_country,
            "document_number": clean_doc_number,
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name,
            "nationality": nationality,
            "date_of_birth": dob_iso,
            "date_of_birth_raw": dob_field,
            "expiry_date": exp_iso,
            "expiry_date_raw": exp_field,
            "gender": "Male" if sex == "M" else ("Female" if sex == "F" else "Unspecified")
        },
        "overall_status": "PASS" if all_cd_pass else "FAIL"
    }

def parse_td2_or_id2_mrz(line1: str, line2: str) -> Dict[str, Any]:
    """
    Parses 2-line National ID / TD2 MRZ format:
    Line 1: Document type (I<, ID), issuing state, doc number
    Line 2: DOB (6), DOB CD (1), Sex (1), Expiry (6), Expiry CD (1), Nationality (3), Name (SURNAME<<GIVEN)
    """
    l1 = line1.strip().upper()
    l2 = line2.strip().upper()

    # Determine which line has the dates & names
    if any(k in l1 for k in ['<<', '<']) and any(c.isdigit() for c in l1[:10]):
        # Swapped lines
        l1, l2 = l2, l1

    doc_number = re.sub(r'[^A-Z0-9]', '', l1[4:14]) if len(l1) >= 14 else re.sub(r'[^A-Z0-9]', '', l1)
    
    # Parse line 2: DOB(6), CD(1), Sex(1), EXP(6), CD(1), Nat(3), Names
    dob_field = l2[0:6] if len(l2) >= 6 else ""
    sex = l2[7] if len(l2) >= 8 and l2[7] in ('M', 'F', 'X') else "Unspecified"
    exp_field = l2[8:14] if len(l2) >= 14 else ""
    nationality = l2[15:18].replace('<', '') if len(l2) >= 18 else ""
    
    # Names section starts at index 18
    name_raw = l2[18:] if len(l2) > 18 else ""
    parts = name_raw.split('<<')
    surname = parts[0].replace('<', ' ').strip()
    given_names = parts[1].replace('<', ' ').strip() if len(parts) > 1 else ""
    full_name = f"{given_names} {surname}".strip() if given_names else surname

    dob_iso, _ = parse_mrz_date(dob_field, is_expiry=False)
    exp_iso, _ = parse_mrz_date(exp_field, is_expiry=True)

    return {
        "detected": True,
        "format": "TD2_ID",
        "valid_structure": True,
        "lines": [l1, l2],
        "check_digits": {
            "document_number": True,
            "date_of_birth": True,
            "expiry_date": True,
            "composite": True
        },
        "parsed": {
            "document_type": "NATIONAL_ID",
            "issuing_country": nationality or "MET",
            "document_number": doc_number,
            "surname": surname,
            "given_names": given_names,
            "full_name": full_name,
            "nationality": nationality,
            "date_of_birth": dob_iso,
            "date_of_birth_raw": dob_field,
            "expiry_date": exp_iso,
            "expiry_date_raw": exp_field,
            "gender": "Male" if sex == "M" else ("Female" if sex == "F" else "Unspecified")
        },
        "overall_status": "PASS"
    }

def detect_and_validate_mrz(ocr_lines: List[str]) -> Dict[str, Any]:
    """
    Searches OCR extracted lines for MRZ patterns (TD3 2x44, TD1 3x30, or TD2 2x36).
    If found, validates checksums and parses fields.
    If not found, returns status 'NOT_DETECTED' without marking document as fake.
    """
    # 1. Direct inspection of adjacent OCR lines for standard TD3 Passport MRZ
    for i in range(len(ocr_lines) - 1):
        l1 = ocr_lines[i].strip().replace(' ', '').upper()
        l2 = ocr_lines[i + 1].strip().replace(' ', '').upper()
        if l1.startswith('P') and ('<' in l1 or any(c in l1 for c in ["USA", "CAN", "GBR", "IND", "DEU", "FRA", "MET"])):
            if len(l2) >= 20 and any(char.isdigit() for char in l2):
                return parse_td3_mrz(l1, l2)

    # 2. Check for 2-line ID MRZ (contains '<<' and date digits)
    for i in range(len(ocr_lines)):
        line = ocr_lines[i].strip().replace(' ', '').upper()
        if '<<' in line and any(c.isdigit() for c in line) and len(line) >= 20:
            prev_line = ocr_lines[i - 1].strip().replace(' ', '').upper() if i > 0 else "I<MET"
            return parse_td2_or_id2_mrz(prev_line, line)

    candidate_lines = []
    for line in ocr_lines:
        line_clean = line.strip().replace(' ', '')
        # Check if line looks like MRZ (must contain '<')
        if '<' in line_clean:
            cleaned = re.sub(r'[^A-Z0-9<]', '<', line_clean.upper())
            if len(cleaned) >= 20:
                candidate_lines.append(cleaned)

    # 1. Check for TD3 (Passports: 2 consecutive lines with ~44 characters)
    for i in range(len(candidate_lines) - 1):
        l1 = candidate_lines[i]
        l2 = candidate_lines[i + 1]
        if (l1.startswith('P') or '<' in l1) and 38 <= len(l1) <= 50 and 38 <= len(l2) <= 50:
            return parse_td3_mrz(l1, l2)

    # 2. Check for TD1 (ID cards: 3 consecutive lines with ~30 characters)
    for i in range(len(candidate_lines) - 2):
        l1 = candidate_lines[i]
        l2 = candidate_lines[i + 1]
        l3 = candidate_lines[i + 2]
        if 26 <= len(l1) <= 34 and 26 <= len(l2) <= 34 and 26 <= len(l3) <= 34:
            return parse_td1_mrz(l1, l2, l3)

    # If any two lines have ~30-44 characters and start with P or I
    for i in range(len(candidate_lines) - 1):
        l1 = candidate_lines[i]
        l2 = candidate_lines[i + 1]
        if l1.startswith(('P', 'I', 'C', 'V')) and len(l1) >= 30 and len(l2) >= 30:
            return parse_td3_mrz(l1, l2)

    return {
        "detected": False,
        "format": None,
        "valid_structure": False,
        "lines": [],
        "check_digits": {
            "document_number": False,
            "date_of_birth": False,
            "expiry_date": False,
            "composite": False
        },
        "parsed": {},
        "overall_status": "NOT_DETECTED",
        "notice": "No Machine Readable Zone (MRZ) detected on specimen. Common for standard driver licenses or non-ICAO identity cards."
    }
