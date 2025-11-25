from dataclasses import dataclass


@dataclass
class Washer:
    id: int | None
    name: str
    bonus_percentage: float
    active: bool
