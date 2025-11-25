from pydantic import BaseModel, Field


class WasherCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    bonus_percentage: float = Field(..., ge=0)

class WasherUpdateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    bonus_percentage: float = Field(..., ge=0)
    active: bool
