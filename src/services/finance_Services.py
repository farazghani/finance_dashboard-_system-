from uuid import uuid4
from datetime import date as dt_date, datetime
from src.models.transaction import RecordCreate , RecordResponse , RecordUpdate
from src.core.exceptions import NotFoundException, BadRequestException
from src.services.audit_service import create_audit_log
from src.models.audit import AuditLogCreate

def create_record(db, user_id: str, data: RecordCreate):
    try:
        cursor = db.cursor()
        record_id = str(uuid4())
        cursor.execute(
            """
            INSERT INTO records (id, user_id, amount, type, category, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                user_id,
                data.amount,
                data.type,
                data.category,
                str(data.date),
                datetime.utcnow().isoformat(),
            ),
        )

        create_audit_log(
            db,
            AuditLogCreate(
                user_id=user_id,
                action="CREATE_RECORD",
                target_id=record_id,
                details=f"{data.type} of {data.amount}"
            )
        )   

        return {"id": record_id}

    except Exception as e:
        raise BadRequestException(f"Failed to create record: {str(e)}")
    


def update_record(db, record_id: str, data: RecordUpdate , admin_user_id) -> RecordResponse:
    try:
        cursor = db.cursor()

        update_fields = []
        values = []

        if data.amount is not None:
            update_fields.append("amount = ?")
            values.append(data.amount)

        if data.type is not None:
            update_fields.append("type = ?")
            values.append(data.type)

        if data.category is not None:
            update_fields.append("category = ?")
            values.append(data.category)

        if data.date is not None:
            update_fields.append("date = ?")
            values.append(str(data.date))

        if data.notes is not None:
            update_fields.append("notes = ?")
            values.append(data.notes)

        # ❌ nothing to update
        if not update_fields:
            raise BadRequestException("No fields provided for update")

        query = f"""
            UPDATE records
            SET {', '.join(update_fields)}
            WHERE id = ?
        """

        values.append(record_id)

        cursor.execute(query, tuple(values))
        db.commit()

        if cursor.rowcount == 0:
            raise NotFoundException("Record not found")

        # fetch updated record
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = cursor.fetchone()

        create_audit_log(
            db,
            AuditLogCreate(
                user_id=admin_user_id,
                action="UPDATE_RECORD",
                target_id=record_id,
                details=f"{data.type} of {data.amount}"
            )
        )  
        return RecordResponse(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            type=row["type"],
            category=row["category"],
            date=row["date"],
            notes=row["notes"],
        )

    except (BadRequestException, NotFoundException):
        raise

    except Exception as e:
        raise BadRequestException(f"Failed to update record: {str(e)}")

def get_records(
    db,
    record_type: str | None = None,
    category: str | None = None,
    record_date: dt_date | None = None,
):
    try:
        cursor = db.cursor()
        query = "SELECT * FROM records"
        filters = []
        values = []

        if record_type is not None:
            filters.append("type = ?")
            values.append(record_type)

        if category is not None:
            filters.append("category = ?")
            values.append(category)

        if record_date is not None:
            filters.append("date = ?")
            values.append(str(record_date))

        if filters:
            query += " WHERE " + " AND ".join(filters)

        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    except Exception as e:
        raise BadRequestException(f"Failed to fetch records: {str(e)}")




def delete_record(db, record_id: str , admin_user_id : str):
    try:
        cursor = db.cursor()

        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        db.commit()

        if cursor.rowcount == 0:
            raise NotFoundException("Record not found")
        create_audit_log(
                db,
                AuditLogCreate(
                    user_id=admin_user_id,
                    action="DELETE_RECORD",
                    target_id=record_id,
                    details="Record deleted"
                )
        )
        return {"message": "deleted"}

    except Exception as e:
        raise BadRequestException(f"Failed to fetch records: {str(e)}")
