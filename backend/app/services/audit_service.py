from sqlalchemy.orm import Session
from datetime import datetime
from ..models import AuditLog

def log_audit_event(
    db: Session,
    action: str,
    details: str,
    username: str = "System",
    case_id: str | None = None,
    ip_address: str = "127.0.0.1",
    user_agent: str = "VERINEX-Browser/2026.1",
    severity: str = "INFO"
) -> AuditLog:
    """
    Creates an immutable audit log entry.
    """
    entry = AuditLog(
        username=username,
        action=action,
        case_id=case_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        severity=severity,
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
