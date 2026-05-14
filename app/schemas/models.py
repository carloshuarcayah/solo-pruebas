from pydantic import BaseModel, Field, EmailStr, model_validator
from datetime import datetime, date, time



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


class ReservaCreate(BaseModel):
    cancha_id: int = Field(..., gt=0)
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time

    @model_validator(mode='after')
    def validar_rango_horario(self) -> 'ReservaCreate':
        if self.hora_fin <= self.hora_inicio:
            raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return self


class ReservaResponse(BaseModel):
    id: int
    usuario_id: int
    cancha_id: int
    fecha_reserva: date
    hora_inicio: time
    hora_fin: time
    estado: str
    created_at: datetime

