import pytest
from datetime import datetime

from src.core.security import verify_password, get_password_hash
from src.db.db import get_test_db
from src.services.user_services import create_user, login_user, update_user
from src.models.user import UserCreate, UserLogin, UserUpdate, Role
from src.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException


# 🔹 helper to insert user directly
def seed_user(db, user_id="u1"):
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO users (id, name, email, password, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            "Test User",
            "test@example.com",
            get_password_hash("password"),
            "admin",
            datetime.utcnow().isoformat(),
        ),
    )
    db.commit()
    return user_id


# ✅ 1. create_user success
def test_create_user_success():
    db = get_test_db()

    user = UserCreate(
        name="Faraz",
        email="faraz@test.com",
        role=Role.admin,
        password="secret",
    )

    result = create_user(db, user)

    assert "id" in result

    # verify DB insert
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (result["id"],))
    row = cursor.fetchone()

    assert row["email"] == "faraz@test.com"
    assert row["is_active"] == 1
    assert row["password"] != "secret"
    assert verify_password("secret", row["password"]) is True


# ❌ 2. create_user duplicate email → BadRequest
def test_create_user_duplicate_email():
    db = get_test_db()

    user = UserCreate(
        name="Faraz",
        email="same@test.com",
        role=Role.admin,
        password="secret",
    )

    create_user(db, user)

    with pytest.raises(BadRequestException):
        create_user(db, user)  # duplicate email


# ✅ 3. update_user success
def test_update_user_success():
    db = get_test_db()
    user_id = seed_user(db)

    update_data = UserUpdate(name="Updated Name")

    result = update_user(user_id, db, update_data)

    assert result.name == "Updated Name"

    # verify DB updated
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    assert row["name"] == "Updated Name"


def test_update_user_is_active_success():
    db = get_test_db()
    user_id = seed_user(db)

    result = update_user(user_id, db, UserUpdate(is_active=False))

    assert result.is_active is False

    cursor = db.cursor()
    cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    assert row["is_active"] == 0


# ❌ 4. update_user no fields → BadRequest
def test_update_user_no_fields():
    db = get_test_db()
    user_id = seed_user(db)

    with pytest.raises(BadRequestException):
        update_user(user_id, db, UserUpdate())


# ❌ 5. update_user user not found → NotFound
def test_update_user_not_found():
    db = get_test_db()

    update_data = UserUpdate(name="New Name")

    with pytest.raises(NotFoundException):
        update_user("non-existent-id", db, update_data)


def test_login_user_rejects_inactive_user():
    db = get_test_db()
    user_id = seed_user(db)
    update_user(user_id, db, UserUpdate(is_active=False))

    with pytest.raises(UnauthorizedException):
        login_user(
            db,
            UserLogin(email="test@example.com", password="password"),
        )
