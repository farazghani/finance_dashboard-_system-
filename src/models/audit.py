from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class AuditLogBase(BaseModel):
    user_id: str
    action: str
    target_id: Optional[str] = None
    details: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogResponse(AuditLogBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)