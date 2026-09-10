import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import ScreeningCase, CaseNote, User
from ..schemas import ScreeningCaseOut, CaseNoteOut, AddNoteRequest, UpdateCaseStatusRequest
from ..services.audit_service import log_audit_event
from .auth import get_current_user
from .screenings import _format_case_out

router = APIRouter(prefix="/cases", tags=["Case Review & Management"])

@router.get("", response_model=List[ScreeningCaseOut])
def list_cases(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ScreeningCase)
    if status and status != "ALL":
        query = query.filter(ScreeningCase.status == status)
    if risk_level and risk_level != "ALL":
        query = query.filter(ScreeningCase.overall_risk_level == risk_level)
    if doc_type and doc_type != "ALL":
        query = query.filter(ScreeningCase.document_type == doc_type)
    if search:
        query = query.filter(
            (ScreeningCase.id.ilike(f"%{search}%")) |
            (ScreeningCase.extracted_data_json.ilike(f"%{search}%"))
        )

    cases = query.order_by(ScreeningCase.created_at.desc()).all()
    return [_format_case_out(c) for c in cases]

@router.get("/{case_id}", response_model=ScreeningCaseOut)
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return _format_case_out(case)

@router.patch("/{case_id}/status", response_model=ScreeningCaseOut)
def update_case_status(
    case_id: str,
    req: UpdateCaseStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    old_status = case.status
    case.status = req.status
    case.reviewer_id = current_user.id
    case.reviewer_name = current_user.full_name
    case.reviewer_decision = req.status
    case.reviewer_decision_at = datetime.utcnow()
    case.updated_at = datetime.utcnow()

    # Append to timeline
    timeline = case.get_timeline()
    timeline.append({
        "step": f"Adjudication: {req.status}",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "COMPLETED",
        "description": f"Status updated from '{old_status}' to '{req.status}' by {current_user.full_name}. Reason: {req.decision_reason or 'Standard review'}"
    })
    case.timeline_json = json.dumps(timeline)

    # Optional internal note if decision reason was given
    if req.decision_reason:
        note = CaseNote(
            case_id=case.id,
            user_id=current_user.id,
            author_name=current_user.full_name,
            author_role=current_user.role,
            note_text=f"Decision: {req.status} – {req.decision_reason}",
            created_at=datetime.utcnow()
        )
        db.add(note)

    db.commit()
    db.refresh(case)

    # Audit log
    severity = "CRITICAL" if req.status in ["REJECTED", "FLAGGED"] else "INFO"
    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="CASE_STATUS_UPDATE",
        case_id=case.id,
        details=f"Case {case.id} status changed to {req.status}. Reason: {req.decision_reason or 'None'}",
        severity=severity
    )

    return _format_case_out(case)

@router.post("/{case_id}/notes", response_model=CaseNoteOut)
def add_case_note(
    case_id: str,
    req: AddNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(ScreeningCase).filter(ScreeningCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    author = req.author_name or current_user.full_name
    note = CaseNote(
        case_id=case.id,
        user_id=current_user.id,
        author_name=author,
        author_role=current_user.role,
        note_text=req.note_text,
        created_at=datetime.utcnow()
    )
    db.add(note)

    # Append to timeline
    timeline = case.get_timeline()
    timeline.append({
        "step": "Reviewer Note Added",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "COMPLETED",
        "description": f"Note recorded by {author}: \"{req.note_text[:45]}...\""
    })
    case.timeline_json = json.dumps(timeline)

    db.commit()
    db.refresh(note)

    log_audit_event(
        db=db,
        username=author,
        action="NOTE_ADDED",
        case_id=case.id,
        details=f"Investigator note added to case {case.id}",
        severity="INFO"
    )

    return note
