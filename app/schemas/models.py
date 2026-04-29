from pydantic import BaseModel, Field, EmailStr



class User(BaseModel):
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    dni: str = Field(..., min_length=1, max_length=8, pattern=r'^\d+$')
    telefono: str = Field(..., min_length=1, max_length=9, pattern=r'^\d+$')
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    telefono: str

