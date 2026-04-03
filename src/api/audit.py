from fastapi import APIRouter, Depends

from src.core.security import TokenData, require_role
from src.db.db import get_db
from src.models.audit import AuditLogResponse
from src.models.user import Role
from src.services.audit_service import get_audit_logs


router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def get_audit_logs_endpoint(
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return get_audit_logs(db)
