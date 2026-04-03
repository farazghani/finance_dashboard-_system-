from pydantic import BaseModel
from typing import List


class CategorySummary(BaseModel):
    category: str
    total: float


class RecentActivity(BaseModel):
    id: str
    user_id: str
    amount: float
    type: str
    category: str
    date: str
    notes: str | None = None


class MonthlyTrend(BaseModel):
    month: str
    total_income: float
    total_expense: float
    net_balance: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    category_breakdown: List[CategorySummary]
    recent_activity: List[RecentActivity]
    monthly_trends: List[MonthlyTrend]
