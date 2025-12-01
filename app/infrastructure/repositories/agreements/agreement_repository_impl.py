from typing import List, Optional
from datetime import date
from sqlalchemy import select, update, delete as sql_delete
from app.domain.agreements.entities.agreement import Agreement
from app.domain.agreements.repositories.agreement_repository import IAgreementRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.subscriptions import Agreement as AgreementModel, AgreementVehicle

class AgreementRepositoryImpl(IAgreementRepository):
    
    def _to_entity(self, model: AgreementModel) -> Optional[Agreement]:
        if not model:
            return None
        return Agreement(
            id=model.id,
            company_name=model.company_name,
            contact_name=model.contact_name,
            contact_phone=model.contact_phone,
            contact_email=model.contact_email,
            start_date=model.start_date,
            end_date=model.end_date,
            discount_percentage=model.discount_percentage,
            special_rate=model.special_rate,
            is_active=model.is_active,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: Agreement) -> AgreementModel:
        return AgreementModel(
            id=entity.id,
            company_name=entity.company_name,
            contact_name=entity.contact_name,
            contact_phone=entity.contact_phone,
            contact_email=entity.contact_email,
            start_date=entity.start_date,
            end_date=entity.end_date,
            discount_percentage=entity.discount_percentage,
            special_rate=entity.special_rate,
            is_active=entity.is_active,
            notes=entity.notes
        )

    async def create(self, agreement: Agreement) -> Agreement:
        async with SessionLocal() as session:
            model = self._to_model(agreement)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, agreement_id: int) -> Optional[Agreement]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(AgreementModel).where(AgreementModel.id == agreement_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update(self, agreement_id: int, agreement: Agreement) -> Agreement:
        async with SessionLocal() as session:
            stmt = (
                update(AgreementModel)
                .where(AgreementModel.id == agreement_id)
                .values(
                    company_name=agreement.company_name,
                    contact_name=agreement.contact_name,
                    contact_phone=agreement.contact_phone,
                    contact_email=agreement.contact_email,
                    start_date=agreement.start_date,
                    end_date=agreement.end_date,
                    discount_percentage=agreement.discount_percentage,
                    special_rate=agreement.special_rate,
                    is_active=agreement.is_active,
                    notes=agreement.notes
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(AgreementModel).where(AgreementModel.id == agreement_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, agreement_id: int):
        async with SessionLocal() as session:
            await session.execute(
                sql_delete(AgreementModel).where(AgreementModel.id == agreement_id)
            )
            await session.commit()

    async def list_active(self) -> List[Agreement]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(AgreementModel).where(AgreementModel.is_active == 'active')
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def list_all(self) -> List[Agreement]:
        async with SessionLocal() as session:
            result = await session.execute(select(AgreementModel))
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def add_vehicle_to_agreement(self, agreement_id: int, vehicle_id: int):
        async with SessionLocal() as session:
            # Check if already exists
            result = await session.execute(
                select(AgreementVehicle)
                .where(AgreementVehicle.agreement_id == agreement_id)
                .where(AgreementVehicle.vehicle_id == vehicle_id)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                agreement_vehicle = AgreementVehicle(
                    agreement_id=agreement_id,
                    vehicle_id=vehicle_id
                )
                session.add(agreement_vehicle)
                await session.commit()

    async def remove_vehicle_from_agreement(self, agreement_id: int, vehicle_id: int):
        async with SessionLocal() as session:
            await session.execute(
                sql_delete(AgreementVehicle)
                .where(AgreementVehicle.agreement_id == agreement_id)
                .where(AgreementVehicle.vehicle_id == vehicle_id)
            )
            await session.commit()

    async def get_agreement_by_vehicle_id(self, vehicle_id: int) -> Optional[Agreement]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(AgreementModel)
                .join(AgreementVehicle, AgreementModel.id == AgreementVehicle.agreement_id)
                .where(AgreementVehicle.vehicle_id == vehicle_id)
                .where(AgreementModel.is_active == 'active')
            )
            model = result.scalars().first()
            return self._to_entity(model)
