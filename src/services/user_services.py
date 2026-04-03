from uuid import uuid4
from datetime import datetime

from src.models.user import UserCreate, UserResponse, UserUpdate
from src.core.exceptions import BadRequestException, NotFoundException

def create_user(db, user: UserCreate):
    try:
        cursor = db.cursor()

        user_id = str(uuid4())

        cursor.execute(
            """
            INSERT INTO users (id, name, email, password, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user.name,
                user.email,
                user.password,
                user.role.value if hasattr(user.role, "value") else user.role,
                datetime.utcnow().isoformat(),
            ),
        )

        db.commit()

        return {"id": user_id}

    except Exception as e:
        raise BadRequestException(f"Failed to create user: {str(e)}")



def update_user(user_id: str, db, user: UserUpdate) -> UserResponse:
    try:
        cursor = db.cursor()

        update_fields = []
        values = []

        # dynamically build query
        if user.name is not None:
            update_fields.append("name = ?")
            values.append(user.name)

        if user.email is not None:
            update_fields.append("email = ?")
            values.append(user.email)

        if user.role is not None:
            update_fields.append("role = ?")
            values.append(
                user.role.value if hasattr(user.role, "value") else user.role
            )

        # ❌ nothing to update
        if not update_fields:
            raise BadRequestException("No fields provided for update")

        # build final query
        query = f"""
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = ?
        """

        values.append(user_id)

        cursor.execute(query, tuple(values))
        db.commit()

        # check if user exists
        if cursor.rowcount == 0:
            raise NotFoundException("User not found")

        # fetch updated user
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        return UserResponse(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            role=row["role"],
            created_at=row["created_at"],
        )

    except (BadRequestException, NotFoundException):
        raise

    except Exception as e:
        raise BadRequestException(f"Failed to update user: {str(e)}")
    

