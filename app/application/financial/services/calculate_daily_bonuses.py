from datetime import date
from typing import List, Dict, Any
from app.domain.financial.repositories.bonus_repository import BonusRepository
from app.domain.washing.repositories.washing_service_repository import WashingServiceRepository
from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.application.financial.services.apply_advance_deduction import ApplyAdvanceDeduction
from app.infrastructure.database.models.financial import Bonus

class CalculateDailyBonuses:
    def __init__(
        self,
        bonus_repository: BonusRepository,
        washing_repository: WashingServiceRepository,
        washer_repository: IWasherRepository,
        apply_deduction_use_case: ApplyAdvanceDeduction
    ):
        self.bonus_repository = bonus_repository
        self.washing_repository = washing_repository
        self.washer_repository = washer_repository
        self.apply_deduction_use_case = apply_deduction_use_case

    async def execute(self, calculation_date: date) -> List[Dict[str, Any]]:
        results = []
        washers = await self.washer_repository.list()

        for washer in washers:
            if not washer.is_active:
                continue

            # Check if bonus already exists
            existing_bonus = await self.bonus_repository.get_by_washer_and_date(washer.id, calculation_date)
            if existing_bonus:
                results.append({
                    "washer_id": washer.id,
                    "washer_name": washer.full_name,
                    "status": "skipped",
                    "reason": "Bonus already calculated"
                })
                continue

            # Calculate sales
            total_sales = await self.washing_repository.get_total_sales_by_washer_and_date(washer.id, calculation_date)
            
            if total_sales == 0:
                 results.append({
                    "washer_id": washer.id,
                    "washer_name": washer.full_name,
                    "status": "skipped",
                    "reason": "No sales"
                })
                 continue

            # Calculate gross bonus
            commission_rate = washer.commission_percentage / 100.0
            gross_bonus = int(total_sales * commission_rate)

            # Apply deductions
            deduction = await self.apply_deduction_use_case.execute(washer.id, gross_bonus)
            
            net_bonus = gross_bonus - deduction

            # Create Bonus
            bonus = Bonus(
                washer_id=washer.id,
                amount=net_bonus,
                bonus_date=calculation_date,
                reason=f"Sales: {total_sales}, Gross: {gross_bonus}, Ded: {deduction}"
            )
            
            await self.bonus_repository.create(bonus)
            
            results.append({
                "washer_id": washer.id,
                "washer_name": washer.full_name,
                "status": "calculated",
                "total_sales": total_sales,
                "gross_bonus": gross_bonus,
                "deduction": deduction,
                "net_bonus": net_bonus
            })

        return results
