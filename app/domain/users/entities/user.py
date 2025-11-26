from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """
    Entidad de dominio User.
    Este objeto representa al usuario dentro de la lógica de negocio (dominio).
    """
    id: Optional[int]
    full_name: str
    email: str
    phone: Optional[str]
    status: str = "active"
    created_at: Optional[datetime] = None
