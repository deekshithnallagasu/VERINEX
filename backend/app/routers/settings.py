from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..models import SystemSetting, User
from ..services.audit_service import log_audit_event
from .auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

class UpdateSettingsRequest(BaseModel):
    settings: Dict[str, str]

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    items = db.query(SystemSetting).all()
    result = {}
    for item in items:
        result[item.key] = {
            "value": item.value,
            "description": item.description,
            "category": item.category
        }
    return result

@router.put("")
def update_settings(
    req: UpdateSettingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    for k, v in req.settings.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == k).first()
        if setting:
            setting.value = str(v)
        else:
            setting = SystemSetting(key=k, value=str(v), category="Custom")
            db.add(setting)

    db.commit()

    log_audit_event(
        db=db,
        username=current_user.full_name,
        action="SETTINGS_UPDATE",
        details=f"System parameters updated by {current_user.full_name}: {list(req.settings.keys())}",
        severity="WARNING"
    )

    return {"status": "success", "message": "Settings updated successfully."}
