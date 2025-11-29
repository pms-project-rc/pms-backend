from typing import List, Dict, Any
from app.domain.financial.repositories.bonus_repository import BonusRepository
from app.domain.washers.repositories.washer_repository import IWasherRepository

class GetMonthlyBonuses:
    def __init__(self, bonus_repository: BonusRepository, washer_repository: IWasherRepository):
        self.bonus_repository = bonus_repository
        self.washer_repository = washer_repository

    async def execute(self, month: int, year: int) -> List[Dict[str, Any]]:
        # Get summary from bonus repo
        summary_data = await self.bonus_repository.get_monthly_summary(month, year)
        
        results = []
        for item in summary_data:
            washer_id = item["washer_id"]
            total_amount = item["total_amount"]
            
            # Get washer details
            washer = await self.washer_repository.get(washer_id)
            washer_name = washer.full_name if washer else "Unknown"
            
            results.append({
                "washer_id": washer_id,
                "washer_name": washer_name,
                "month": month,
                "year": year,
                "total_bonus": total_amount
            })
            
        return results
