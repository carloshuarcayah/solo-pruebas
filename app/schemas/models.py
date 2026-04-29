from pydantic import BaseModel, Field, EmailStr



class User(BaseModel):
    name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr = Field(..., min_length=1)
    dni: int = Field(..., max_digits=8, gt=0)
    telefono: int = Field(..., max_digits=9, gt=0)


class UserResponse(User):
    id: int

