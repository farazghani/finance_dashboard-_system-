import os
from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, ConfigDict, EmailStr

from src.core.exceptions import ForbiddenException, UnauthorizedException
from src.models.user import Role


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

ROLE_HIERARCHY: dict[Role, int] = {
    Role.viewer: 1,
    Role.analyst: 2,
    Role.admin: 3,
}


class TokenData(BaseModel):
    user_id: str
    email: EmailStr | None = None
    role: Role
    exp: int | None = None

    model_config = ConfigDict(use_enum_values=False)


def normalize_role(role: Role | str) -> Role:
    if isinstance(role, Role):
        return role

    try:
        return Role(role)
    except ValueError as exc:
        raise ForbiddenException("Invalid user role") from exc


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def has_required_role(
    user_role: Role | str,
    required_role: Role | str,
) -> bool:
    normalized_user_role = normalize_role(user_role)
    normalized_required_role = normalize_role(required_role)
    return ROLE_HIERARCHY[normalized_user_role] >= ROLE_HIERARCHY[normalized_required_role]


def enforce_role(
    user_role: Role | str,
    required_role: Role | str,
) -> Role:
    normalized_user_role = normalize_role(user_role)
    if not has_required_role(normalized_user_role, required_role):
        raise ForbiddenException("Insufficient permissions")
    return normalized_user_role


def enforce_any_role(
    user_role: Role | str,
    allowed_roles: Iterable[Role | str],
) -> Role:
    normalized_user_role = normalize_role(user_role)
    normalized_allowed_roles = {normalize_role(role) for role in allowed_roles}
    if normalized_user_role not in normalized_allowed_roles:
        raise ForbiddenException("Insufficient permissions")
    return normalized_user_role


def _build_token_payload(
    user_id: str,
    role: Role | str,
    email: str | None = None,
    expires_delta: timedelta | None = None,
) -> dict[str, Any]:
    expire_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": user_id,
        "role": normalize_role(role).value,
        "exp": expire_at,
    }
    if email is not None:
        payload["email"] = email
    return payload


def create_access_token(
    user_id: str,
    role: Role | str,
    email: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    payload = _build_token_payload(
        user_id=user_id,
        role=role,
        email=email,
        expires_delta=expires_delta,
    )
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedException("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedException("Invalid token") from exc

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or not role:
        raise UnauthorizedException("Invalid token payload")

    try:
        return TokenData(
            user_id=user_id,
            email=payload.get("email"),
            role=normalize_role(role),
            exp=payload.get("exp"),
        )
    except Exception as exc:
        raise UnauthorizedException("Invalid token payload") from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return decode_access_token(token)


def require_role(required_role: Role | str):
    def checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        enforce_role(current_user.role, required_role)
        return current_user

    return checker


def require_any_role(*allowed_roles: Role | str):
    if not allowed_roles:
        raise ValueError("At least one role must be provided")

    def checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        enforce_any_role(current_user.role, allowed_roles)
        return current_user

    return checker


role_checker = require_any_role
