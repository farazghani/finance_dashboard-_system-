import pytest
from src.models.user import UserCreate
from src.models.user import Role


def test_user_create_valid():
    user = UserCreate(
        name="Faraz",
        email="faraz@test.com",
        role=Role.admin,
        password="secret"
    )

    assert user.email == "faraz@test.com"


def test_user_invalid_email():
    with pytest.raises(Exception):
        UserCreate(
            name="Faraz",
            email="invalid-email",
            role= Role.admin,
            password="secret"
        )

