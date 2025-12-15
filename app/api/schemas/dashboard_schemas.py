from pydantic import BaseModel

class DashboardStats(BaseModel):
    active_vehicles: int
    total_washes: int
    today_income: float
    today_expenses: float
