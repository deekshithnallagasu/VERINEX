import os
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from rapidocr_onnxruntime import RapidOCR
from .image_preprocessing import preprocess_document_image

# Global lazy-loaded OCR engine to avoid re-initialization overhead
_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        try:
            _ocr_engine = RapidOCR()
        except Exception:
            _ocr_engine = None
    return _ocr_engine

def parse_dates_from_text(lines: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Scans lines for DOB, Issue Date, and Expiry Date using contextual regex patterns.
    """
    dob = None
    issue_date = None
    expiry_date = None

    date_regex = r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{4}|\d{1,2}\s+(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[a-z]*\s+\d{4})'

    for line in lines:
        u_line = line.upper()
        # Look for DOB
        if any(k in u_line for k in ["DOB", "DATE OF BIRTH", "NAISSANCE", "BIRTH"]):
            match = re.search(date_regex, u_line)
            if match and not dob:
                dob = match.group(1).replace('/', '-').replace('.', '-')
        
        # Look for Issue Date
        if any(k in u_line for k in ["ISSUE", "DELIVRANCE", "ISS", "ISSUED", "DATE OF ISSUE"]):
            match = re.search(date_regex, u_line)
            if match and not issue_date:
                issue_date = match.group(1).replace('/', '-').replace('.', '-')
        
        # Look for Expiry Date
        if any(k in u_line for k in ["EXPIRY", "EXPIRATION", "EXP", "VALID UNTIL", "EXPIRES"]):
            match = re.search(date_regex, u_line)
            if match and not expiry_date:
                expiry_date = match.group(1).replace('/', '-').replace('.', '-')

    return dob, issue_date, expiry_date

def parse_document_number(lines: List[str]) -> Optional[str]:
    """
    Extracts document identification number.
    """
    for line in lines:
        u_line = line.upper()
        # Look for explicit labels
        if any(k in u_line for k in ["PASSPORT NO", "DOC NO", "DL NO", "ID NO", "DOCUMENT NO", "LICENCE NO", "NO DE PASSEPORT"]):
            # Split by colon or label
            parts = re.split(r'[:#]|\bNO\b', u_line)
            if len(parts) > 1:
                candidate = parts[-1].strip()
                # Clean candidate
                clean = re.sub(r'[^A-Z0-9]', '', candidate)
                if 5 <= len(clean) <= 15:
                    return clean

    # Heuristic search for typical passport / ID format (e.g. 1 letter + 8 digits, or 9 digits)
    for line in lines:
        matches = re.findall(r'\b[A-Z0-9]{8,10}\b', line.upper())
        for m in matches:
            if any(char.isdigit() for char in m) and not m.startswith("20"):
                return m

    return None

def parse_names(lines: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts surname and given names from label headers.
    """
    surname = None
    given_names = None
    full_name = None

    for i, line in enumerate(lines):
        u_line = line.upper()
        LABEL_KEYWORDS = {"SURNAME", "NOM", "LN", "LAST NAME", "GIVEN NAMES", "GIVEN NAME", "PRENOMS", "PRENOM", "FN", "FIRST NAME", "NAME", "NAME/PRENOM", "NAME/NOM"}
        
        # Check for Surname / Nom (use word boundary so 'NOM' does not match 'PRENOMS')
        if re.search(r'\b(SURNAME|LAST\s*NAME|LN|NOM)\b', u_line) and not re.search(r'\b(PRENOM|PRENOMS|GIVEN)\b', u_line):
            parts = re.split(r'[:/]', u_line)
            candidate = parts[-1].strip() if len(parts) > 1 else ""
            if candidate and candidate not in LABEL_KEYWORDS:
                surname = candidate
            elif i + 1 < len(lines) and lines[i + 1].strip().upper() not in LABEL_KEYWORDS:
                surname = lines[i + 1].strip()

        # Check for Given Names / Prenoms
        if re.search(r'\b(GIVEN\s*NAMES?|PRENOMS?|FN|FIRST\s*NAME)\b', u_line):
            parts = re.split(r'[:/]', u_line)
            candidate = parts[-1].strip() if len(parts) > 1 else ""
            if candidate and candidate not in LABEL_KEYWORDS:
                given_names = candidate
            elif i + 1 < len(lines) and lines[i + 1].strip().upper() not in LABEL_KEYWORDS:
                given_names = lines[i + 1].strip()

        # Generic Name
        if "NAME:" in u_line or "NAME /" in u_line:
            parts = u_line.split("NAME")
            if len(parts) > 1:
                val = parts[1].replace(":", "").replace("/", "").strip()
                if val:
                    full_name = val

    if surname and given_names:
        # Clean words
        clean_s = re.sub(r'[^A-Z\s]', '', surname.upper()).strip()
        clean_g = re.sub(r'[^A-Z\s]', '', given_names.upper()).strip()
        return clean_s, clean_g
    elif full_name:
        clean_f = re.sub(r'[^A-Z\s]', '', full_name.upper()).strip()
        parts = clean_f.split()
        if len(parts) > 1:
            return parts[-1], " ".join(parts[:-1])
        return clean_f, ""

    return None, None

def extract_document_text(
    file_path: str,
    document_type: str = "PASSPORT",
    mock_profile: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extracts real structured identity information from document image.
    Uses RapidOCR (PaddleOCR onnx engine) running locally.
    
    CRITICAL REQUIREMENT:
    - For real uploaded files (mock_profile is None), runs genuine OCR on the uploaded image.
    - Does NOT use filename-based fallback.
    - If OCR detects nothing or fails, returns proper warning/failure rather than fake data.
    - Existing fictional sample profiles remain ONLY when mock_profile is explicitly passed by demo gallery.
    """
    # 1. DEDICATED DEMO GALLERY PROFILES (Allowed only if mock_profile is explicitly specified)
    if mock_profile == "CLEAN_PASSPORT":
        return {
            "ocr_confidence": 98.4,
            "raw_text": "PASSPORT / PASSEPORT\nUNITED STATES OF AMERICA / ETATS-UNIS D'AMERIQUE\nSURNAME: ABERNATHY\nGIVEN NAMES: CLARA ELEANOR\nNATIONALITY: USA\nDATE OF BIRTH: 14 MAY 1989\nSEX: F\nPLACE OF BIRTH: CALIFORNIA, USA\nDATE OF ISSUE: 12 JUN 2019\nDATE OF EXPIRATION: 11 JUN 2029\nAUTHORITY: UNITED STATES DEPARTMENT OF STATE\nPASSPORT NO: E84920194\nP<USAABERNATHY<<CLARA<ELEANOR<<<<<<<<<<<<<<<\nE849201947USA8905144F2906117<<<<<<<<<<<<<<<4",
            "extracted_data": {
                "full_name": "Clara Eleanor Abernathy",
                "document_number": "E84920194",
                "date_of_birth": "1989-05-14",
                "issue_date": "2019-06-12",
                "expiry_date": "2029-06-11",
                "nationality": "USA",
                "issuing_authority": "U.S. Department of State",
                "address": "742 Evergreen Terrace, Springfield, OR 97477",
                "gender": "Female",
                "mrz_line1": "P<USAABERNATHY<<CLARA<ELEANOR<<<<<<<<<<<<<<<",
                "mrz_line2": "E849201947USA8905144F2906117<<<<<<<<<<<<<<<4"
            }
        }
    elif mock_profile == "EXPIRED_LICENSE":
        return {
            "ocr_confidence": 94.2,
            "raw_text": "DRIVER LICENSE / PERMIS DE CONDUIRE\nSTATE OF WASHINGTON\nDL NO: WDL82947102\nEXP: 2023-04-18\nLN: VANCE\nFN: ARTHUR LIAM\nDOB: 1982-11-23\nSEX: M\nISS: 2017-04-19\nADDR: 1042 NORTHWEST PINE ST, SEATTLE, WA 98101\nCLASS: D - REGULAR VEHICLES",
            "extracted_data": {
                "full_name": "Arthur Liam Vance",
                "document_number": "WDL82947102",
                "date_of_birth": "1982-11-23",
                "issue_date": "2017-04-19",
                "expiry_date": "2023-04-18",
                "nationality": "USA",
                "issuing_authority": "Washington Dept of Licensing",
                "address": "1042 Northwest Pine St, Seattle, WA 98101",
                "gender": "Male",
                "mrz_line1": None,
                "mrz_line2": None
            }
        }
    elif mock_profile == "TAMPERED_MRZ_ID":
        return {
            "ocr_confidence": 91.8,
            "raw_text": "NATIONAL IDENTITY CARD / CARTE NATIONALE D'IDENTITE\nREPUBLIC OF METROPOLIS\nNAME: MARCUS REID\nDOB: 1994-08-15\nSEX: M\nDOC NO: ID-90184712\nEXP: 2028-08-14\nI<MET90184712<<9<<<<<<<<<<<<<<\n9408155M2808143METJONES<<DEVON<8",
            "extracted_data": {
                "full_name": "Marcus Reid",
                "document_number": "ID-90184712",
                "date_of_birth": "1994-08-15",
                "issue_date": "2018-08-15",
                "expiry_date": "2028-08-14",
                "nationality": "MET",
                "issuing_authority": "Metropolis National Registration Office",
                "address": "402 Skyline Boulevard, Apt 9B, Metropolis",
                "gender": "Male",
                "mrz_line1": "I<MET90184712<<9<<<<<<<<<<<<<<",
                "mrz_line2": "9408155M2808143METJONES<<DEVON<8"
            }
        }
    elif mock_profile == "BLURRY_CARD":
        return {
            "ocr_confidence": 72.1,
            "raw_text": "RESIDENCE CARD / TITRE DE SEJOUR\nNAME: HELENA SANTO\nDOB: 1991-03-20\nDOC NO: RC-448219\nEXP: 2027-10-15\nADDR: LOW RESOLUTION / SPECULAR GLARE DETECTED",
            "extracted_data": {
                "full_name": "Helena Santo",
                "document_number": "RC-448219",
                "date_of_birth": "1991-03-20",
                "issue_date": "2022-10-15",
                "expiry_date": "2027-10-15",
                "nationality": "PRT",
                "issuing_authority": "Immigration & Border Service",
                "address": "Low OCR Resolution / Optical Glare detected",
                "gender": "Female",
                "mrz_line1": "CR<PRT448219<<<<<<<<<<<<<<<<<<",
                "mrz_line2": "9103208F2710153PRT<<<<<<<<<<<0"
            }
        }

    # 2. GENUINE OCR PIPELINE FOR REAL UPLOADS
    if not os.path.exists(file_path):
        return {
            "ocr_confidence": 0.0,
            "raw_text": "",
            "extracted_data": {},
            "error": "Uploaded document file not found on disk"
        }

    # Apply image preprocessing to maximize OCR accuracy
    prep_result = preprocess_document_image(file_path)
    ocr_target_image = prep_result.get("best_image_path", file_path)

    engine = get_ocr_engine()
    if engine is None:
        return {
            "ocr_confidence": 0.0,
            "raw_text": "",
            "extracted_data": {},
            "error": "RapidOCR engine failed to initialize"
        }

    try:
        ocr_result, elapse = engine(ocr_target_image)
    except Exception as e:
        # Fallback to original image if preprocessed image failed
        try:
            ocr_result, elapse = engine(file_path)
        except Exception as e2:
            return {
                "ocr_confidence": 0.0,
                "raw_text": "",
                "extracted_data": {},
                "error": f"OCR processing failed: {str(e2)}"
            }

    if not ocr_result or len(ocr_result) == 0:
        return {
            "ocr_confidence": 0.0,
            "raw_text": "",
            "extracted_data": {
                "full_name": None,
                "document_number": None,
                "date_of_birth": None,
                "issue_date": None,
                "expiry_date": None,
                "nationality": None,
                "gender": None,
                "issuing_authority": None,
                "mrz_line1": None,
                "mrz_line2": None
            },
            "warning": "No readable text detected in uploaded document. Check document resolution, lighting, or orientation."
        }

    # Collect extracted lines and confidence
    lines = []
    confidences = []
    mrz_candidates = []

    for item in ocr_result:
        # item is [box_points, text, confidence_str_or_float]
        text = str(item[1]).strip()
        try:
            conf = float(item[2])
        except Exception:
            conf = 0.85
        if text:
            lines.append(text)
            confidences.append(conf)
            if '<' in text:
                mrz_candidates.append(text.replace(' ', '').upper())

    avg_conf = round(float(sum(confidences) / max(1, len(confidences))) * 100.0, 1)
    raw_text = "\n".join(lines)

    # 3. STRUCTURED FIELD PARSING
    surname, given_names = parse_names(lines)
    full_name = f"{given_names} {surname}".strip() if (surname or given_names) else None
    
    doc_number = parse_document_number(lines)
    dob, issue_date, expiry_date = parse_dates_from_text(lines)

    # Nationality heuristic
    nationality = None
    for line in lines:
        u = line.upper()
        if "NATIONALITY" in u or "NATIONALITE" in u:
            parts = re.split(r'[:/]', u)
            if len(parts) > 1:
                nationality = parts[-1].strip()
        elif any(c in u for c in ["UNITED STATES", "USA", "CANADA", "INDIA", "UNITED KINGDOM", "GERMANY", "FRANCE", "METROPOLIS"]):
            for c in ["UNITED STATES", "USA", "CANADA", "INDIA", "UNITED KINGDOM", "GERMANY", "FRANCE", "METROPOLIS"]:
                if c in u:
                    nationality = c
                    break

    # Gender heuristic
    gender = "Unspecified"
    for line in lines:
        u = line.upper()
        if "SEX" in u or "GENDER" in u:
            if " F " in f" {u} " or "FEMALE" in u:
                gender = "Female"
            elif " M " in f" {u} " or "MALE" in u:
                gender = "Male"

    # Authority heuristic
    authority = None
    for line in lines:
        u = line.upper()
        if any(a in u for a in ["AUTHORITY", "DEPARTMENT OF STATE", "DEPT OF LICENSING", "MINISTRY", "GOVERNMENT", "REGISTRATION OFFICE"]):
            authority = line.strip()

    # MRZ lines
    mrz_l1 = mrz_candidates[0] if len(mrz_candidates) > 0 else None
    mrz_l2 = mrz_candidates[1] if len(mrz_candidates) > 1 else None

    return {
        "ocr_confidence": avg_conf,
        "raw_text": raw_text,
        "extracted_data": {
            "full_name": full_name,
            "surname": surname,
            "given_names": given_names,
            "document_number": doc_number,
            "date_of_birth": dob,
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "nationality": nationality,
            "gender": gender,
            "issuing_authority": authority,
            "mrz_line1": mrz_l1,
            "mrz_line2": mrz_l2
        },
        "lines_detected": len(lines)
    }
