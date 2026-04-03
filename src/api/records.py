from datetime import date as dt_date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status

from src.core.security import TokenData, require_any_role, require_role
from src.db.db import get_db
from src.models.common import IdResponse, MessageResponse
from src.models.transaction import RecordCreate, RecordResponse, RecordUpdate
from src.models.user import Role
from src.services.finance_Services import (
    create_record,
    delete_record,
    get_records,
    update_record,
)


router = APIRouter(tags=["records"])


@router.get("/records", response_model=list[RecordResponse])
def get_records_endpoint(
    type: Literal["debit", "credit"] | None = Query(default=None),
    category: str | None = Query(default=None),
    date: dt_date | None = Query(default=None),
    db=Depends(get_db),
    current_user: TokenData = Depends(
        require_any_role(Role.viewer, Role.analyst, Role.admin)
    ),
):
    return get_records(
        db,
        record_type=type,
        category=category,
        record_date=date,
    )


@router.post(
    "/users/{user_id}/records",
    response_model=IdResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_record_endpoint(
    user_id: str,
    data: RecordCreate,
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return create_record(db, user_id, data)


@router.patch("/records/{record_id}", response_model=RecordResponse)
def update_record_endpoint(
    record_id: str,
    data: RecordUpdate,
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return update_record(db, record_id, data, current_user.user_id)


@router.delete("/records/{record_id}", response_model=MessageResponse)
def delete_record_endpoint(
    record_id: str,
    db=Depends(get_db),
    current_user: TokenData = Depends(require_role(Role.admin)),
):
    return delete_record(db, record_id, current_user.user_id)
