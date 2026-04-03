from uuid import uuid4
from datetime import datetime

from src.models.audit import AuditLogCreate, AuditLogResponse


def create_audit_log(db, data: AuditLogCreate):
    cursor = db.cursor()
    audit_id = str(uuid4())
    created_at = datetime.utcnow()
    cursor.execute(
        """
        INSERT INTO audit_logs (id, user_id, action, target_id, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            audit_id,
            data.user_id,
            data.action,
            data.target_id,
            data.details,
            created_at.isoformat(),
        ),
    )
    db.commit()
    return AuditLogResponse(
        id=audit_id,
        user_id=data.user_id,
        action=data.action,
        target_id=data.target_id,
        details=data.details,
        created_at=created_at,
    )


def get_audit_logs(db) -> list[AuditLogResponse]:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, user_id, action, target_id, details, created_at
        FROM audit_logs
        ORDER BY created_at DESC
        """
    )
    rows = cursor.fetchall()

    return [
        AuditLogResponse(
            id=row["id"],
            user_id=row["user_id"],
            action=row["action"],
            target_id=row["target_id"],
            details=row["details"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
