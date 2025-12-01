from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.subscriptions.entities.monthly_subscription import MonthlySubscription

class ISubscriptionRepository(ABC):
    @abstractmethod
    async def create(self, subscription: MonthlySubscription) -> MonthlySubscription:
        pass

    @abstractmethod
    async def get_by_id(self, subscription_id: int) -> Optional[MonthlySubscription]:
        pass

    @abstractmethod
    async def get_active_by_vehicle_id(self, vehicle_id: int, current_date: date) -> Optional[MonthlySubscription]:
        """Obtiene la suscripción activa para un vehículo en la fecha dada."""
        pass

    @abstractmethod
    async def update(self, subscription_id: int, subscription: MonthlySubscription) -> MonthlySubscription:
        pass

    @abstractmethod
    async def list_active(self, current_date: date) -> List[MonthlySubscription]:
        pass

    @abstractmethod
    async def list_expiring(self, current_date: date, days_threshold: int) -> List[MonthlySubscription]:
        """Lista suscripciones que vencen en los próximos X días."""
        pass
