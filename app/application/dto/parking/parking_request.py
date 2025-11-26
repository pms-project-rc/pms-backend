"""
Request DTOs for parking operations.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ParkingEntryRequest(BaseModel):
    """Request DTO for parking entry registration."""
    
    plate: str = Field(
        ...,
        description="Vehicle license plate",
        min_length=6,
        max_length=10,
        examples=["ABC123", "ABC123D"]
    )
    
    helmet_count: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Number of helmets (only for motorcycles)"
    )
    
    owner_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Vehicle owner name"
    )
    
    owner_phone: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Vehicle owner phone number"
    )
    
    notes: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Additional notes"
    )
    
    @field_validator('plate')
    @classmethod
    def validate_plate(cls, v: str) -> str:
        """Validate and normalize plate format."""
        if not v:
            raise ValueError("La placa no puede estar vacía")
        
        # Remove spaces and convert to uppercase
        normalized = v.strip().upper().replace(" ", "").replace("-", "")
        
        if len(normalized) < 6:
            raise ValueError("La placa debe tener al menos 6 caracteres")
        
        return normalized
    
    class Config:
        json_schema_extra = {
            "example": {
                "plate": "ABC123D",
                "helmet_count": 2,
                "owner_name": "Juan Pérez",
                "owner_phone": "3001234567",
                "notes": "Cliente frecuente"
            }
        }
