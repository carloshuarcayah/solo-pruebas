from pydantic import BaseModel, Field, EmailStr



class User(BaseModel):
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    dni: int = Field(..., gt=0, lt=100000000)
    telefono: int = Field(..., gt=0, lt=1000000000)
    contraseña: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    dni: str
    telefono: str

