from pydantic import BaseModel
from typing import List


class CategorySummary(BaseModel):
    category: str
    total: float


class DashboardSummary(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    category_breakdown: List[CategorySummary]