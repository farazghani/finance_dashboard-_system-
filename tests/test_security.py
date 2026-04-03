from datetime import timedelta

import pytest

from src.core.exceptions import ForbiddenException, UnauthorizedException
from src.core.security import (
    TokenData,
    create_access_token,
    decode_access_token,
    enforce_any_role,
    enforce_role,
    get_current_user,
    has_required_role,
    normalize_role,
    require_any_role,
    require_role,
)
from src.models.user import Role


def test_normalize_role_from_string():
    assert normalize_role("admin") == Role.admin


def test_has_required_role_uses_hierarchy():
    assert has_required_role(Role.admin, Role.analyst) is True
    assert has_required_role(Role.viewer, Role.admin) is False


def test_enforce_role_returns_normalized_role():
    assert enforce_role("admin", Role.viewer) == Role.admin


def test_enforce_role_raises_for_insufficient_permissions():
    with pytest.raises(ForbiddenException):
        enforce_role(Role.viewer, Role.analyst)


def test_enforce_any_role_accepts_allowed_role():
    assert enforce_any_role("analyst", [Role.viewer, Role.analyst]) == Role.analyst


def test_create_and_decode_access_token():
    token = create_access_token(
        user_id="user-1",
        email="user@example.com",
        role=Role.admin,
        expires_delta=timedelta(minutes=5),
    )

    payload = decode_access_token(token)

    assert payload.user_id == "user-1"
    assert payload.email == "user@example.com"
    assert payload.role == Role.admin


def test_decode_access_token_rejects_invalid_token():
    with pytest.raises(UnauthorizedException):
        decode_access_token("not-a-valid-token")


def test_decode_access_token_rejects_missing_claims():
    token = create_access_token(
        user_id="user-1",
        email="user@example.com",
        role=Role.admin,
    )
    broken_token = token.rsplit(".", 1)[0] + ".broken"

    with pytest.raises(UnauthorizedException):
        decode_access_token(broken_token)


def test_get_current_user_returns_token_data():
    token = create_access_token(
        user_id="user-2",
        email="viewer@example.com",
        role=Role.viewer,
    )

    current_user = get_current_user(token)

    assert isinstance(current_user, TokenData)
    assert current_user.user_id == "user-2"
    assert current_user.role == Role.viewer


def test_require_role_checker_accepts_allowed_role():
    checker = require_role(Role.analyst)
    current_user = TokenData(
        user_id="user-3",
        email="admin@example.com",
        role=Role.admin,
    )

    assert checker(current_user) == current_user


def test_require_role_checker_raises_for_insufficient_permissions():
    checker = require_role(Role.admin)
    current_user = TokenData(
        user_id="user-4",
        email="viewer@example.com",
        role=Role.viewer,
    )

    with pytest.raises(ForbiddenException):
        checker(current_user)


def test_require_any_role_checker_accepts_matching_role():
    checker = require_any_role(Role.viewer, Role.admin)
    current_user = TokenData(
        user_id="user-5",
        email="analyst@example.com",
        role=Role.admin,
    )

    assert checker(current_user) == current_user


def test_require_any_role_checker_raises_for_disallowed_role():
    checker = require_any_role(Role.admin)
    current_user = TokenData(
        user_id="user-6",
        email="analyst@example.com",
        role=Role.analyst,
    )

    with pytest.raises(ForbiddenException):
        checker(current_user)
