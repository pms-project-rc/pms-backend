from pydantic import BaseModel


class WasherResponse(BaseModel):
    id: int
    name: str
    bonus_percentage: float
    active: bool

    class Config:
        from_attributes = True
