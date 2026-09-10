import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import User, ScreeningCase, CaseNote, AuditLog, SystemSetting
from .sample_generator import generate_sample_documents
from .security import hash_password

def seed_database(db: Session):
    """
    Seeds the database with fictional demo users, cases, notes, audit logs, and settings.
    """
    # 1. Generate sample images on disk first
    generate_sample_documents()

    # 2. Seed Users
    if db.query(User).count() == 0:
        demo_users = [
            User(
                username="analyst",
                email="analyst@verinex.ai",
                full_name="Sarah Chen",
                hashed_password=hash_password("Verinex2026!"),
                role="Compliance Analyst",
                avatar="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
            ),
            User(
                username="reviewer",
                email="reviewer@verinex.ai",
                full_name="David Vance",
                hashed_password=hash_password("Verinex2026!"),
                role="Senior Reviewer",
                avatar="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
            ),
            User(
                username="admin",
                email="admin@verinex.ai",
                full_name="Alex Mercer",
                hashed_password=hash_password("Verinex2026!"),
                role="Risk Administrator",
                avatar="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
            )
        ]
        db.add_all(demo_users)
        db.commit()

    # 3. Seed Cases if empty
    if db.query(ScreeningCase).count() == 0:
        now = datetime.utcnow()
        cases = [
            ScreeningCase(
                id="VNX-2026-8801",
                document_type="PASSPORT",
                file_name="sample_passport_clean.png",
                file_url="/static/samples/sample_passport_clean.png",
                status="VERIFIED",
                overall_risk_level="LOW",
                risk_score=12,
                ai_confidence=97.8,
                document_quality_score=94.5,
                ocr_confidence=98.4,
                extracted_data_json=json.dumps({
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
                }),
                consistency_checks_json=json.dumps([
                    {"check_name": "Document Validity Period", "status": "PASS", "category": "Temporal Integrity", "details": "Valid until 2029-06-11."},
                    {"check_name": "MRZ Checksum & Cryptography", "status": "PASS", "category": "ICAO 9303 Compliance", "details": "Check digits 7, 4, 7 match."},
                    {"check_name": "Visual vs MRZ Consistency", "status": "PASS", "category": "Format Integrity", "details": "Name and document number coincide perfectly."},
                    {"check_name": "Optical Quality & Legibility", "status": "PASS", "category": "Image Forensics", "details": "Sharpness 94%, no glare, guilloche visible."}
                ]),
                suspicious_indicators_json=json.dumps([]),
                timeline_json=json.dumps([
                    {"step": "Uploaded", "timestamp": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Document uploaded by system ingest."},
                    {"step": "Quality & OCR", "timestamp": (now - timedelta(hours=2, minutes=58)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "High fidelity capture (98.4% OCR confidence)."},
                    {"step": "AI Risk Engine", "timestamp": (now - timedelta(hours=2, minutes=57)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Low risk evaluated (12/100)."},
                    {"step": "Human Verification", "timestamp": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Verified by David Vance (Senior Reviewer)."}
                ]),
                reviewer_name="David Vance",
                reviewer_decision="VERIFIED",
                reviewer_decision_at=now - timedelta(hours=1),
                created_at=now - timedelta(hours=3),
                updated_at=now - timedelta(hours=1)
            ),
            ScreeningCase(
                id="VNX-2026-8802",
                document_type="DRIVERS_LICENSE",
                file_name="sample_license_expired.png",
                file_url="/static/samples/sample_license_expired.png",
                status="IN_REVIEW",
                overall_risk_level="MEDIUM",
                risk_score=58,
                ai_confidence=91.2,
                document_quality_score=89.0,
                ocr_confidence=94.2,
                extracted_data_json=json.dumps({
                    "full_name": "Arthur Liam Vance",
                    "document_number": "WDL82947102",
                    "date_of_birth": "1982-11-23",
                    "issue_date": "2017-04-19",
                    "expiry_date": "2023-04-18",
                    "nationality": "USA",
                    "issuing_authority": "Washington Dept of Licensing",
                    "address": "1042 Northwest Pine St, Seattle, WA 98101",
                    "gender": "Male"
                }),
                consistency_checks_json=json.dumps([
                    {"check_name": "Document Validity Period", "status": "FAIL", "category": "Temporal Integrity", "details": "Document expired on 2023-04-18."},
                    {"check_name": "DOB & Age Realism", "status": "PASS", "category": "Biographical Consistency", "details": "Subject age 43 years is valid."},
                    {"check_name": "Format & Layout Syntax", "status": "PASS", "category": "Jurisdiction Syntax", "details": "Washington standard DL syntax matches."},
                    {"check_name": "Optical Quality & Legibility", "status": "PASS", "category": "Image Forensics", "details": "Resolution 860x540 clear."}
                ]),
                suspicious_indicators_json=json.dumps([
                    {
                        "title": "Expired Identity Credential",
                        "severity": "MEDIUM",
                        "category": "Temporal Validity",
                        "explanation": "Document expiration date (2023-04-18) is past. Government jurisdictions consider expired credentials invalid for authoritative identity verification.",
                        "recommendation": "Request customer upload valid current driver's license or passport."
                    }
                ]),
                timeline_json=json.dumps([
                    {"step": "Uploaded", "timestamp": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Document uploaded via customer verification portal."},
                    {"step": "Quality & OCR", "timestamp": (now - timedelta(hours=4, minutes=58)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "OCR extracted 8 fields with 94.2% confidence."},
                    {"step": "AI Risk Engine", "timestamp": (now - timedelta(hours=4, minutes=57)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Medium risk flag generated due to expired status."},
                    {"step": "Queued for Review", "timestamp": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M"), "status": "IN_PROGRESS", "description": "Awaiting tier-1 reviewer adjudication."}
                ]),
                reviewer_name=None,
                reviewer_decision=None,
                reviewer_decision_at=None,
                created_at=now - timedelta(hours=5),
                updated_at=now - timedelta(hours=5)
            ),
            ScreeningCase(
                id="VNX-2026-8803",
                document_type="NATIONAL_ID",
                file_name="sample_national_id_tampered.png",
                file_url="/static/samples/sample_national_id_tampered.png",
                status="FLAGGED",
                overall_risk_level="HIGH",
                risk_score=88,
                ai_confidence=93.4,
                document_quality_score=87.5,
                ocr_confidence=91.8,
                extracted_data_json=json.dumps({
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
                }),
                consistency_checks_json=json.dumps([
                    {"check_name": "Visual vs MRZ Name Match", "status": "FAIL", "category": "Cryptographic & Format Integrity", "details": "Printed name 'Marcus Reid' differs from MRZ encoded name 'Devon Jones'."},
                    {"check_name": "MRZ Checksum Algorithm", "status": "WARN", "category": "ICAO 9303 Compliance", "details": "Check digit anomaly detected in line 2."},
                    {"check_name": "Document Validity Period", "status": "PASS", "category": "Temporal Integrity", "details": "Document unexpired (valid until 2028-08-14)."},
                    {"check_name": "Optical Quality & Legibility", "status": "PASS", "category": "Image Forensics", "details": "No physical blur detected."}
                ]),
                suspicious_indicators_json=json.dumps([
                    {
                        "title": "Visual-to-MRZ Cross-Check Discrepancy",
                        "severity": "HIGH",
                        "category": "Identity Tampering Signal",
                        "explanation": "Critical mismatch detected between the human-readable Visual Inspection Zone (VIZ) name 'Marcus Reid' and the machine-readable optical track 'JONES DEVON'. This pattern frequently signals digital surface manipulation or composite overlay.",
                        "recommendation": "Escalate to Fraud Intelligence & Security Team for forensic document inspection."
                    }
                ]),
                timeline_json=json.dumps([
                    {"step": "Uploaded", "timestamp": (now - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "High-risk trigger from automated onboarding."},
                    {"step": "Quality & OCR", "timestamp": (now - timedelta(hours=7, minutes=58)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "OCR extracted text and parsed dual-line MRZ zone."},
                    {"step": "AI Risk Engine", "timestamp": (now - timedelta(hours=7, minutes=57)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "High risk calculated (88/100) due to name-MRZ discrepancy."},
                    {"step": "Escalation", "timestamp": (now - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Flagged for fraud team investigation."}
                ]),
                reviewer_name="Sarah Chen",
                reviewer_decision="FLAGGED",
                reviewer_decision_at=now - timedelta(hours=6),
                created_at=now - timedelta(hours=8),
                updated_at=now - timedelta(hours=6)
            ),
            ScreeningCase(
                id="VNX-2026-8804",
                document_type="RESIDENCE_PERMIT",
                file_name="sample_residence_blurry.png",
                file_url="/static/samples/sample_residence_blurry.png",
                status="IN_REVIEW",
                overall_risk_level="MEDIUM",
                risk_score=48,
                ai_confidence=74.5,
                document_quality_score=42.0,
                ocr_confidence=72.1,
                extracted_data_json=json.dumps({
                    "full_name": "Helena Santo",
                    "document_number": "RC-448219",
                    "date_of_birth": "1991-03-20",
                    "issue_date": "2022-10-15",
                    "expiry_date": "2027-10-15",
                    "nationality": "PRT",
                    "issuing_authority": "Immigration & Border Service",
                    "address": "Optical Glare / Low Resolution",
                    "gender": "Female",
                    "mrz_line1": "CR<PRT448219<<<<<<<<<<<<<<<<<<",
                    "mrz_line2": "9103208F2710153PRT<<<<<<<<<<<0"
                }),
                consistency_checks_json=json.dumps([
                    {"check_name": "Optical Quality & Sharpness", "status": "FAIL", "category": "Image Forensics", "details": "Sharpness score 42% falls below threshold of 70%."},
                    {"check_name": "Glare & Flash Reflection", "status": "WARN", "category": "Image Forensics", "details": "Central specular glare obscuring sub-text."},
                    {"check_name": "Document Validity Period", "status": "PASS", "category": "Temporal Integrity", "details": "Expiry date 2027-10-15 valid."}
                ]),
                suspicious_indicators_json=json.dumps([
                    {
                        "title": "Sub-Threshold Image Sharpness & Glare",
                        "severity": "MEDIUM",
                        "category": "Image Forensics",
                        "explanation": "Image sharpness (42/100) and optical glare obscure micro-print security features, reducing automated screening confidence.",
                        "recommendation": "Request high-resolution re-scan or photo taken in diffuse ambient lighting."
                    }
                ]),
                timeline_json=json.dumps([
                    {"step": "Uploaded", "timestamp": (now - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Mobile camera upload submitted."},
                    {"step": "Quality Analysis", "timestamp": (now - timedelta(hours=9, minutes=58)).strftime("%Y-%m-%d %H:%M"), "status": "COMPLETED", "description": "Image quality test flagged severe blur/glare."},
                    {"step": "Queued for Review", "timestamp": (now - timedelta(hours=9)).strftime("%Y-%m-%d %H:%M"), "status": "IN_PROGRESS", "description": "Assigned to document review queue."}
                ]),
                reviewer_name=None,
                reviewer_decision=None,
                reviewer_decision_at=None,
                created_at=now - timedelta(hours=10),
                updated_at=now - timedelta(hours=10)
            )
        ]
        db.add_all(cases)
        db.commit()

        # Add notes to some cases
        note1 = CaseNote(
            case_id="VNX-2026-8801",
            author_name="David Vance",
            author_role="Senior Reviewer",
            note_text="Clean specimen. Visual security fibers and MRZ check digits match all standards. Standard verification granted.",
            created_at=now - timedelta(hours=1)
        )
        note2 = CaseNote(
            case_id="VNX-2026-8803",
            author_name="Sarah Chen",
            author_role="Compliance Analyst",
            note_text="Elevated to High Risk. Visual name Marcus Reid does not align with MRZ track DEVON JONES. Flagged for secondary fraud verification.",
            created_at=now - timedelta(hours=6)
        )
        db.add_all([note1, note2])
        db.commit()

    # 4. Seed Audit Logs
    if db.query(AuditLog).count() == 0:
        now = datetime.utcnow()
        logs = [
            AuditLog(
                username="David Vance",
                action="USER_LOGIN",
                case_id=None,
                details="Successful multi-factor enterprise authentication from trusted IP subnet.",
                ip_address="192.168.1.45",
                severity="INFO",
                created_at=now - timedelta(hours=4)
            ),
            AuditLog(
                username="System Ingest",
                action="DOCUMENT_UPLOAD",
                case_id="VNX-2026-8801",
                details="Document 'sample_passport_clean.png' successfully parsed and secured in encrypted storage.",
                ip_address="10.0.4.12",
                severity="INFO",
                created_at=now - timedelta(hours=3)
            ),
            AuditLog(
                username="AI Risk Engine",
                action="RISK_EVALUATION",
                case_id="VNX-2026-8803",
                details="High risk score (88/100) triggered: Discrepancy between printed visual zone and machine-readable zone.",
                ip_address="127.0.0.1",
                severity="WARNING",
                created_at=now - timedelta(hours=7)
            ),
            AuditLog(
                username="Sarah Chen",
                action="CASE_DECISION",
                case_id="VNX-2026-8803",
                details="Case status updated to FLAGGED. Reason: Escalated for fraud forensics.",
                ip_address="192.168.1.82",
                severity="CRITICAL",
                created_at=now - timedelta(hours=6)
            ),
            AuditLog(
                username="David Vance",
                action="CASE_DECISION",
                case_id="VNX-2026-8801",
                details="Case status updated to VERIFIED. Decision: Approved standard onboarding.",
                ip_address="192.168.1.45",
                severity="INFO",
                created_at=now - timedelta(hours=1)
            )
        ]
        db.add_all(logs)
        db.commit()

    # 5. Seed System Settings
    if db.query(SystemSetting).count() == 0:
        settings = [
            SystemSetting(key="risk_low_threshold", value="29", description="Maximum score threshold for Low Risk classification", category="Risk Thresholds"),
            SystemSetting(key="risk_med_threshold", value="69", description="Maximum score threshold for Medium Risk classification", category="Risk Thresholds"),
            SystemSetting(key="auto_escalate_high_risk", value="true", description="Automatically queue High Risk cases for human review", category="Workflow"),
            SystemSetting(key="session_timeout_minutes", value="30", description="Inactivity timeout for compliance sessions", category="Security"),
            SystemSetting(key="data_retention_days", value="90", description="Days before PII is automatically redacted", category="Privacy"),
            SystemSetting(key="ocr_engine_mode", value="Hybrid (Heuristic + LayoutLM)", description="Active document parser mode", category="AI Configuration")
        ]
        db.add_all(settings)
        db.commit()
