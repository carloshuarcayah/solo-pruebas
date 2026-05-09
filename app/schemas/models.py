from pydantic import BaseModel, Field, EmailStr
from datetime import datetime



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


class LoginRequest(BaseModel):
    dni: str = Field(..., min_length=1, max_length=8, pattern=r'^\d+$')
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Court(BaseModel):
    id: int
    nombre: str
    ubicacion: str
    disponible: bool
    cantidad_jugadores: int
    precio: float
    fecha: datetime


class PaginatedCourts(BaseModel):
    items: list[Court]
    total: int
    page: int
    page_size: int

