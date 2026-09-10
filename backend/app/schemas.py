from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: Optional[str] = "Compliance Analyst"

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Extracted Data & Checks ---
class ExtractedData(BaseModel):
    full_name: Optional[str] = None
    document_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    nationality: Optional[str] = None
    issuing_authority: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    mrz_line1: Optional[str] = None
    mrz_line2: Optional[str] = None

class ConsistencyCheckItem(BaseModel):
    check_name: str
    status: str  # PASS, WARN, FAIL
    details: str
    category: Optional[str] = "Integrity"

class SuspiciousIndicatorItem(BaseModel):
    title: str
    severity: str  # LOW, MEDIUM, HIGH
    category: str
    explanation: str
    recommendation: Optional[str] = None

class TimelineEvent(BaseModel):
    step: str
    timestamp: str
    status: str
    description: str

# --- Screening Case Schemas ---
class CaseNoteOut(BaseModel):
    id: int
    case_id: str
    author_name: str
    author_role: str
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class AddNoteRequest(BaseModel):
    note_text: str
    author_name: Optional[str] = None

class UpdateCaseStatusRequest(BaseModel):
    status: str  # VERIFIED, FLAGGED, REJECTED, IN_REVIEW
    decision_reason: Optional[str] = None

class ScreeningCaseOut(BaseModel):
    id: str
    document_type: str
    file_name: str
    file_url: str
    status: str
    overall_risk_level: str
    risk_score: int
    ai_confidence: float
    document_quality_score: float
    ocr_confidence: float
    extracted_data: Dict[str, Any]
    consistency_checks: List[Dict[str, Any]]
    suspicious_indicators: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]
    reviewer_name: Optional[str] = None
    reviewer_decision: Optional[str] = None
    reviewer_decision_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    notes: Optional[List[CaseNoteOut]] = []

    class Config:
        from_attributes = True

# --- Sample Document Info ---
class SampleDocumentItem(BaseModel):
    id: str
    title: str
    description: str
    document_type: str
    expected_risk: str
    image_url: str
    badge_label: str

# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    id: int
    username: str
    action: str
    case_id: Optional[str] = None
    details: str
    ip_address: str
    user_agent: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard Stats Schemas ---
class DashboardStats(BaseModel):
    total_screenings: int
    verified_documents: int
    suspicious_documents: int
    pending_reviews: int
    verification_rate: float
    avg_processing_time_sec: float
    risk_distribution: Dict[str, int] # {"LOW": 45, "MEDIUM": 22, "HIGH": 11}
    document_type_distribution: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
