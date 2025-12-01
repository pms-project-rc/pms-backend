from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.agreements.entities.agreement import Agreement

class IAgreementRepository(ABC):
    @abstractmethod
    async def create(self, agreement: Agreement) -> Agreement:
        pass

    @abstractmethod
    async def get_by_id(self, agreement_id: int) -> Optional[Agreement]:
        pass

    @abstractmethod
    async def update(self, agreement_id: int, agreement: Agreement) -> Agreement:
        pass

    @abstractmethod
    async def delete(self, agreement_id: int):
        pass

    @abstractmethod
    async def list_active(self) -> List[Agreement]:
        pass

    @abstractmethod
    async def list_all(self) -> List[Agreement]:
        pass

    @abstractmethod
    async def add_vehicle_to_agreement(self, agreement_id: int, vehicle_id: int):
        """Asocia un vehículo a un convenio."""
        pass

    @abstractmethod
    async def remove_vehicle_from_agreement(self, agreement_id: int, vehicle_id: int):
        """Desasocia un vehículo de un convenio."""
        pass

    @abstractmethod
    async def get_agreement_by_vehicle_id(self, vehicle_id: int) -> Optional[Agreement]:
        """Obtiene el convenio activo de un vehículo."""
        pass
