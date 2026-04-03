from uuid import uuid4
from datetime import datetime

from src.core.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from src.core.security import create_access_token, get_password_hash, verify_password
from src.models.user import TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate
from src.services.audit_service import create_audit_log
from src.models.audit import AuditLogCreate

def create_user(db, user: UserCreate):
    try:
        cursor = db.cursor()

        user_id = str(uuid4())

        cursor.execute(
            """
            INSERT INTO users (id, name, email, password, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user.name,
                user.email,
                get_password_hash(user.password),
                user.role.value if hasattr(user.role, "value") else user.role,
                int(user.is_active),
                datetime.utcnow().isoformat(),
            ),
        )

        db.commit()
        create_audit_log(
            db,
            AuditLogCreate(
                user_id=user_id,
                action="CREATE_USER",
                target_id=user_id,
                details=f"User {user.email} created"
            )
         )
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

        if user.is_active is not None:
            update_fields.append("is_active = ?")
            values.append(int(user.is_active))

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
        create_audit_log(
            db,
            AuditLogCreate(
                user_id=user_id,
                action="UPDATE_USER",
                target_id=user_id,
                details="User updated"
            )
        )

        return UserResponse(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
        )

    except (BadRequestException, NotFoundException):
        raise

    except Exception as e:
        raise BadRequestException(f"Failed to update user: {str(e)}")


def login_user(db, credentials: UserLogin) -> TokenResponse:
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT id, email, password, role, is_active
        FROM users
        WHERE email = ?
        """,
        (credentials.email,),
    )
    row = cursor.fetchone()

    if row is None or not verify_password(credentials.password, row["password"]):
        raise UnauthorizedException("Invalid email or password")
    if not bool(row["is_active"]):
        raise UnauthorizedException("User account is inactive")

    access_token = create_access_token(
        user_id=row["id"],
        email=row["email"],
        role=row["role"],
    )
    return TokenResponse(access_token=access_token)
