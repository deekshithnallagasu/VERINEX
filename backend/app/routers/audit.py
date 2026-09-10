from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from ..database import get_db
from ..models import AuditLog
from ..schemas import AuditLogOut
from ..services.audit_service import log_audit_event
from .auth import get_current_user
from ..models import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

class ClientAuditRequest(BaseModel):
    action: str
    details: str
    case_id: Optional[str] = None
    severity: Optional[str] = "INFO"

@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    action: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action and action != "ALL":
        query = query.filter(AuditLog.action == action)
    if severity and severity != "ALL":
        query = query.filter(AuditLog.severity == severity)
    if search:
        query = query.filter(
            (AuditLog.username.ilike(f"%{search}%")) |
            (AuditLog.details.ilike(f"%{search}%")) |
            (AuditLog.case_id.ilike(f"%{search}%"))
        )

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs

@router.post("", response_model=AuditLogOut)
def record_client_audit_event(
    req: ClientAuditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = log_audit_event(
        db=db,
        username=current_user.full_name,
        action=req.action,
        case_id=req.case_id,
        details=req.details,
        severity=req.severity or "INFO"
    )
    return entry
