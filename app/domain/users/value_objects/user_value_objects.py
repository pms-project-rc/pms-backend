"""
Value Objects para el módulo de usuarios.

Los Value Objects son objetos inmutables que representan conceptos
del dominio sin identidad propia.
"""
from dataclasses import dataclass
from typing import ClassVar
import re


@dataclass(frozen=True)
class Email:
    """
    Value Object para representar un email válido.
    
    Attributes:
        value: La dirección de email
    """
    value: str
    
    # Pattern de validación de email (simple)
    EMAIL_PATTERN: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __post_init__(self):
        """Valida el email al crear el objeto."""
        if not self.value:
            raise ValueError("El email no puede estar vacío")
        if not re.match(self.EMAIL_PATTERN, self.value):
            raise ValueError(f"Email inválido: {self.value}")
        # Normalizar a minúsculas
        object.__setattr__(self, 'value', self.value.lower())
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def domain(self) -> str:
        """Retorna el dominio del email (parte después del @)."""
        return self.value.split('@')[1]


@dataclass(frozen=True)
class Password:
    """
    Value Object para representar una contraseña hasheada.
    
    Note: Este VO solo almacena el hash, no la contraseña en texto plano.
    El hashing se debe hacer antes de crear el VO.
    
    Attributes:
        hashed_value: El hash de la contraseña
    """
    hashed_value: str
    
    def __post_init__(self):
        """Valida que el hash no esté vacío."""
        if not self.hashed_value:
            raise ValueError("El hash de la contraseña no puede estar vacío")
        if len(self.hashed_value) < 10:
            raise ValueError("El hash de la contraseña es demasiado corto, probablemente inválido")
    
    def __str__(self) -> str:
        """Retorna una representación segura (no muestra el hash)."""
        return "***hashed***"
    
    def __repr__(self) -> str:
        return "<Password(***hashed***)>"


@dataclass(frozen=True)
class PhoneNumber:
    """
    Value Object para representar un número de teléfono.
    
    Attributes:
        value: El número de teléfono
    """
    value: str
    
    def __post_init__(self):
        """Valida y normaliza el número de teléfono."""
        if not self.value:
            raise ValueError("El número de teléfono no puede estar vacío")
        
        # Eliminar caracteres no numéricos y espacios
        cleaned = re.sub(r'[^\d+]', '', self.value)
        
        if len(cleaned) < 7:
            raise ValueError(f"Número de teléfono demasiado corto: {self.value}")
        
        if len(cleaned) > 15:
            raise ValueError(f"Número de teléfono demasiado largo: {self.value}")
        
        # Normalizar
        object.__setattr__(self, 'value', cleaned)
    
    def __str__(self) -> str:
        return self.value
