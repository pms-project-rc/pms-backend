from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    role: str

    class Config:
        orm_mode = True
