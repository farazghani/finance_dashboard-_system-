from fastapi import APIRouter

from src.api.audit import router as audit_router
from src.api.dashboard import router as dashboard_router
from src.api.records import router as records_router
from src.api.users import router as users_router


api_router = APIRouter()
api_router.include_router(users_router)
api_router.include_router(records_router)
api_router.include_router(dashboard_router)
api_router.include_router(audit_router)
