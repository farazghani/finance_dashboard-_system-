from fastapi import APIRouter, Depends

from src.core.security import TokenData, require_any_role
from src.db.db import get_db
from src.models.dashboard import DashboardSummary
from src.models.user import Role
from src.services.dashboard_Services import get_dashboard_summary


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary_endpoint(
    db=Depends(get_db),
    current_user: TokenData = Depends(
        require_any_role(Role.viewer, Role.analyst, Role.admin)
    ),
):
    return get_dashboard_summary(db)
