from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(50), default="Compliance Analyst")  # Admin, Senior Reviewer, Compliance Analyst, Auditor
    avatar = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("CaseNote", back_populates="author")

class ScreeningCase(Base):
    __tablename__ = "screening_cases"

    id = Column(String(50), primary_key=True, index=True)  # VNX-2026-XXXX
    document_type = Column(String(50), nullable=False)     # PASSPORT, DRIVERS_LICENSE, NATIONAL_ID, RESIDENCE_PERMIT
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(255), nullable=False)
    
    status = Column(String(50), default="IN_REVIEW", index=True) # PENDING, IN_REVIEW, VERIFIED, FLAGGED, REJECTED
    overall_risk_level = Column(String(20), default="LOW", index=True) # LOW, MEDIUM, HIGH
    risk_score = Column(Integer, default=15)               # 0 - 100
    ai_confidence = Column(Float, default=94.5)            # 0 - 100%
    document_quality_score = Column(Float, default=92.0)   # 0 - 100%
    ocr_confidence = Column(Float, default=96.0)           # 0 - 100%

    # Serialized JSON structures
    extracted_data_json = Column(Text, default="{}")
    consistency_checks_json = Column(Text, default="[]")
    suspicious_indicators_json = Column(Text, default="[]")
    timeline_json = Column(Text, default="[]")
    mrz_result_json = Column(Text, default="{}")
    tampering_result_json = Column(Text, default="{}")
    face_result_json = Column(Text, default="{}")
    validation_result_json = Column(Text, default="{}")

    annotated_file_url = Column(String(255), nullable=True)
    face_file_url = Column(String(255), nullable=True)

    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewer_name = Column(String(100), nullable=True)
    reviewer_decision = Column(String(50), nullable=True)
    reviewer_decision_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")

    def get_extracted_data(self):
        try:
            return json.loads(self.extracted_data_json)
        except Exception:
            return {}

    def get_consistency_checks(self):
        try:
            return json.loads(self.consistency_checks_json)
        except Exception:
            return []

    def get_suspicious_indicators(self):
        try:
            return json.loads(self.suspicious_indicators_json)
        except Exception:
            return []

    def get_timeline(self):
        try:
            return json.loads(self.timeline_json)
        except Exception:
            return []

    def get_mrz_result(self):
        try:
            return json.loads(self.mrz_result_json) if self.mrz_result_json else {}
        except Exception:
            return {}

    def get_tampering_result(self):
        try:
            return json.loads(self.tampering_result_json) if self.tampering_result_json else {}
        except Exception:
            return {}

    def get_face_result(self):
        try:
            return json.loads(self.face_result_json) if self.face_result_json else {}
        except Exception:
            return {}

    def get_validation_result(self):
        try:
            return json.loads(self.validation_result_json) if self.validation_result_json else {}
        except Exception:
            return {}

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("screening_cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_name = Column(String(100), nullable=False)
    author_role = Column(String(50), default="Reviewer")
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("ScreeningCase", back_populates="notes")
    author = relationship("User", back_populates="notes")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, default="System")
    action = Column(String(100), nullable=False, index=True) # e.g. USER_LOGIN, SCREENING_RUN, STATUS_UPDATE, NOTE_ADDED, REPORT_EXPORTED
    case_id = Column(String(50), nullable=True, index=True)
    details = Column(Text, nullable=False)
    ip_address = Column(String(50), default="127.0.0.1")
    user_agent = Column(String(255), default="VERINEX-Client/1.0 (Secured)")
    severity = Column(String(20), default="INFO", index=True) # INFO, WARNING, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    category = Column(String(50), default="General")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
