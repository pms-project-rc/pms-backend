"""
Exportaciones del módulo de repositorios de usuarios.
"""
from .user_repository import (
    UserRepositoryInterface,
    GlobalAdminRepository,
    OperationalAdminRepository,
)

__all__ = [
    "UserRepositoryInterface",
    "GlobalAdminRepository",
    "OperationalAdminRepository",
]
