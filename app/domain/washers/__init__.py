"""
Bounded Context: Washers (Lavadores)

Este módulo contiene el dominio de los lavadores del sistema.
"""
from .entities import Washer
from .repositories import WasherRepository

__all__ = [
    "Washer",
    "WasherRepository",
]
