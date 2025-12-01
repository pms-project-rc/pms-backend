from typing import Optional
from sqlalchemy import select, update
from app.domain.parking.entities.vehicle import Vehicle
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.vehicles import Vehicle as VehicleModel

class VehicleRepositoryImpl(IVehicleRepository):
    
    def _to_entity(self, model: VehicleModel) -> Optional[Vehicle]:
        if not model:
            return None
        return Vehicle(
            id=model.id,
            plate=model.plate,
            vehicle_type=model.vehicle_type,
            owner_name=model.owner_name,
            owner_phone=model.owner_phone,
            brand=model.brand,
            model=model.model,
            color=model.color,
            is_frequent=model.is_frequent,
            notes=model.notes
        )

    def _to_model(self, entity: Vehicle) -> VehicleModel:
        return VehicleModel(
            id=entity.id,
            plate=entity.plate,
            vehicle_type=entity.vehicle_type,
            owner_name=entity.owner_name,
            owner_phone=entity.owner_phone,
            brand=entity.brand,
            model=entity.model,
            color=entity.color,
            is_frequent=entity.is_frequent,
            notes=entity.notes
        )

    async def get_by_plate(self, plate: str) -> Optional[Vehicle]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(VehicleModel).where(VehicleModel.plate == plate)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(VehicleModel).where(VehicleModel.id == vehicle_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def create(self, vehicle: Vehicle) -> Vehicle:
        async with SessionLocal() as session:
            model = self._to_model(vehicle)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update(self, vehicle_id: int, vehicle: Vehicle) -> Vehicle:
        async with SessionLocal() as session:
            stmt = (
                update(VehicleModel)
                .where(VehicleModel.id == vehicle_id)
                .values(
                    plate=vehicle.plate,
                    vehicle_type=vehicle.vehicle_type,
                    owner_name=vehicle.owner_name,
                    owner_phone=vehicle.owner_phone,
                    brand=vehicle.brand,
                    model=vehicle.model,
                    color=vehicle.color,
                    is_frequent=vehicle.is_frequent,
                    notes=vehicle.notes
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(VehicleModel).where(VehicleModel.id == vehicle_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)
