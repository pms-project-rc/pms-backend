from datetime import date
from typing import Optional
from app.domain.agreements.entities.agreement import Agreement
from app.domain.agreements.repositories.agreement_repository import IAgreementRepository

class CreateAgreementUseCase:
    """Use case for creating a new agreement"""
    
    def __init__(self, agreement_repo: IAgreementRepository):
        self.agreement_repo = agreement_repo
    
    async def execute(
        self,
        company_name: str,
        contact_name: str,
        start_date: date,
        discount_percentage: int,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        end_date: Optional[date] = None,
        special_rate: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Agreement:
        # Validate discount percentage
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        
        # Create agreement
        agreement = Agreement(
            id=None,
            company_name=company_name,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            start_date=start_date,
            end_date=end_date,
            discount_percentage=discount_percentage,
            special_rate=special_rate,
            is_active="active",
            notes=notes
        )
        
        return await self.agreement_repo.create(agreement)
