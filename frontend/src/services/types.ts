export type UserRole = 'Compliance Analyst' | 'Senior Reviewer' | 'Risk Administrator' | 'Auditor';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  avatar?: string;
  created_at: string;
}

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type CaseStatus = 'PENDING' | 'IN_REVIEW' | 'VERIFIED' | 'FLAGGED' | 'REJECTED';
export type DocumentType = 'PASSPORT' | 'DRIVERS_LICENSE' | 'NATIONAL_ID' | 'RESIDENCE_PERMIT';

export interface ExtractedData {
  full_name?: string;
  document_number?: string;
  date_of_birth?: string;
  issue_date?: string;
  expiry_date?: string;
  nationality?: string;
  issuing_authority?: string;
  address?: string;
  gender?: string;
  mrz_line1?: string;
  mrz_line2?: string;
}

export interface ConsistencyCheck {
  check_name: string;
  status: 'PASS' | 'WARN' | 'FAIL';
  details: string;
  category?: string;
}

export interface SuspiciousIndicator {
  title: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  category: string;
  explanation: string;
  recommendation?: string;
}

export interface TimelineEvent {
  step: string;
  timestamp: string;
  status: string;
  description: string;
}

export interface CaseNote {
  id: number;
  case_id: string;
  author_name: string;
  author_role: string;
  note_text: string;
  created_at: string;
}

export interface ScreeningCase {
  id: string;
  document_type: DocumentType;
  file_name: string;
  file_url: string;
  status: CaseStatus;
  overall_risk_level: RiskLevel;
  risk_score: number;
  ai_confidence: number;
  document_quality_score: number;
  ocr_confidence: number;
  extracted_data: ExtractedData;
  consistency_checks: ConsistencyCheck[];
  suspicious_indicators: SuspiciousIndicator[];
  timeline: TimelineEvent[];
  mrz_result?: any;
  tampering_result?: any;
  face_result?: any;
  validation_result?: any;
  annotated_file_url?: string | null;
  face_file_url?: string | null;
  recommendation?: string | null;
  reviewer_name?: string | null;
  reviewer_decision?: string | null;
  reviewer_decision_at?: string | null;
  created_at: string;
  updated_at: string;
  notes?: CaseNote[];
}

export interface SampleDocumentItem {
  id: string;
  title: string;
  description: string;
  document_type: DocumentType;
  expected_risk: RiskLevel;
  image_url: string;
  badge_label: string;
}

export interface AuditLog {
  id: number;
  username: string;
  action: string;
  case_id?: string | null;
  details: string;
  ip_address: string;
  user_agent: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  created_at: string;
}

export interface DashboardStats {
  metrics: {
    total_screenings: number;
    verified_documents: number;
    suspicious_documents: number;
    pending_reviews: number;
    verification_rate: number;
    avg_processing_time_sec: number;
  };
  risk_distribution: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
  };
  document_type_distribution: Record<string, number>;
  activity_chart: Array<{
    day: string;
    verified: number;
    suspicious: number;
    pending: number;
  }>;
  recent_screenings: ScreeningCase[];
}
