from fastapi import APIRouter, Depends, status

from src.core.security import TokenData, require_role
from src.db.db import get_db
from src.models.common import IdResponse
from src.models.user import Role
from src.models.user import TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate
from src.services.user_services import create_user, login_user, update_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=TokenResponse)
def login_user_endpoint(
    credentials: UserLogin,
    db=Depends(get_db),
):
    return login_user(db, credentials)


@router.post("", response_model=IdResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    user: UserCreate,
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return create_user(db, user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user_endpoint(
    user_id: str,
    user: UserUpdate,
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return update_user(user_id, db, user)
