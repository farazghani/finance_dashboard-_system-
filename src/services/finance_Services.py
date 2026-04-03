from uuid import uuid4
from datetime import datetime
from src.models.transaction import RecordCreate , RecordResponse , RecordUpdate
from src.core.exceptions import NotFoundException, BadRequestException


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
        db.commit()
        return {"id": record_id}

    except Exception as e:
        raise BadRequestException(f"Failed to create record: {str(e)}")
    


def update_record(db, record_id: str, data: RecordUpdate) -> RecordResponse:
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

        return RecordResponse(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            type=row["type"],
            category=row["category"],
            date=row["date"],
            notes=row.get("notes"),
        )

    except (BadRequestException, NotFoundException):
        raise

    except Exception as e:
        raise BadRequestException(f"Failed to update record: {str(e)}")

def get_records(db):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    except Exception as e:
        raise BadRequestException(f"Failed to fetch records: {str(e)}")




def delete_record(db, record_id: str):
    try:
        cursor = db.cursor()

        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        db.commit()

        if cursor.rowcount == 0:
            raise NotFoundException("Record not found")

        return {"message": "deleted"}
    
    except Exception as e:
        raise BadRequestException(f"Failed to fetch records: {str(e)}")

