"""
Eventos de dominio para el módulo de usuarios.

Los eventos de dominio representan hechos importantes que ocurren
en el ciclo de vida de las entidades.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class EventType(Enum):
    """Tipos de eventos de dominio."""
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    USER_LOGIN = "user_login"


@dataclass
class DomainEvent:
    """
    Clase base para eventos de dominio.
    
    Attributes:
        event_type: Tipo de evento
        occurred_at: Timestamp del evento
        user_id: ID del usuario relacionado
        user_role: Rol del usuario
        metadata: Información adicional del evento
    """
    event_type: EventType
    occurred_at: datetime
    user_id: int
    user_role: str
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.now())


@dataclass
class UserCreatedEvent(DomainEvent):
    """Evento emitido cuando se crea un nuevo usuario."""
    
    def __init__(self, user_id: int, user_role: str, email: str):
        super().__init__(
            event_type=EventType.USER_CREATED,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata={"email": email}
        )


@dataclass
class UserUpdatedEvent(DomainEvent):
    """Evento emitido cuando se actualiza un usuario."""
    
    def __init__(self, user_id: int, user_role: str, changes: dict):
        super().__init__(
            event_type=EventType.USER_UPDATED,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata={"changes": changes}
        )


@dataclass
class UserDeletedEvent(DomainEvent):
    """Evento emitido cuando se elimina un usuario."""
    
    def __init__(self, user_id: int, user_role: str):
        super().__init__(
            event_type=EventType.USER_DELETED,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata=None
        )


@dataclass
class UserActivatedEvent(DomainEvent):
    """Evento emitido cuando se activa un usuario."""
    
    def __init__(self, user_id: int, user_role: str):
        super().__init__(
            event_type=EventType.USER_ACTIVATED,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata=None
        )


@dataclass
class UserDeactivatedEvent(DomainEvent):
    """Evento emitido cuando se desactiva un usuario."""
    
    def __init__(self, user_id: int, user_role: str, reason: Optional[str] = None):
        super().__init__(
            event_type=EventType.USER_DEACTIVATED,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata={"reason": reason} if reason else None
        )


@dataclass
class UserLoginEvent(DomainEvent):
    """Evento emitido cuando un usuario inicia sesión."""
    
    def __init__(self, user_id: int, user_role: str, ip_address: Optional[str] = None):
        super().__init__(
            event_type=EventType.USER_LOGIN,
            occurred_at=datetime.now(),
            user_id=user_id,
            user_role=user_role,
            metadata={"ip_address": ip_address} if ip_address else None
        )
