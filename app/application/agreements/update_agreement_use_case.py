from typing import Optional
from datetime import date
from app.domain.agreements.repositories.agreement_repository import IAgreementRepository
from app.domain.agreements.entities.agreement import Agreement

class UpdateAgreementUseCase:
    def __init__(self, agreement_repo: IAgreementRepository):
        self.agreement_repo = agreement_repo

    async def execute(
        self,
        agreement_id: int,
        company_name: Optional[str] = None,
        contact_name: Optional[str] = None,
        start_date: Optional[date] = None,
        discount_percentage: Optional[int] = None,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        end_date: Optional[date] = None,
        special_rate: Optional[int] = None,
        notes: Optional[str] = None,
        is_active: Optional[str] = None
    ) -> Agreement:
        
        # Get existing agreement
        existing_agreement = await self.agreement_repo.get_by_id(agreement_id)
        if not existing_agreement:
            raise ValueError(f"Agreement with ID {agreement_id} not found")

        # Update fields if provided
        if company_name is not None:
            existing_agreement.company_name = company_name
        if contact_name is not None:
            existing_agreement.contact_name = contact_name
        if start_date is not None:
            existing_agreement.start_date = start_date
        if discount_percentage is not None:
            existing_agreement.discount_percentage = discount_percentage
        if contact_phone is not None:
            existing_agreement.contact_phone = contact_phone
        if contact_email is not None:
            existing_agreement.contact_email = contact_email
        if end_date is not None:
            existing_agreement.end_date = end_date
        if special_rate is not None:
            existing_agreement.special_rate = special_rate
        if notes is not None:
            existing_agreement.notes = notes
        if is_active is not None:
            existing_agreement.is_active = is_active

        # Save updates
        updated_agreement = await self.agreement_repo.update(agreement_id, existing_agreement)
        return updated_agreement
