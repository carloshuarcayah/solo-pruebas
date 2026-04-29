from fastapi import FastAPI, HTTPException
from app.model.connection import get_connection
from app.schemas.models import User, UserResponse
from loguru import logger
import hashlib


app = FastAPI()


@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    connection = await get_connection()
    try:
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        row = await connection.fetchrow(
            """
            INSERT INTO Usuarios (nombre, apellido, dni, telefono, password)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, nombre, apellido, dni, telefono
            """,
            user.nombre, user.apellido, str(user.dni), str(user.telefono), hashed_password
        )
        return dict(row)
    except Exception as e:
        logger.error(f"Error al crear el usuario: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {e}")
    finally:
        await connection.close()


@app.get("/users/information", response_model=list[UserResponse])
async def get_user_information():
    connection = await get_connection()
    try:
        rows = await connection.fetch(
            """
            SELECT id, nombre, apellido, dni, telefono
            FROM Usuarios
            """
        )
        return [dict(row) for row in rows]
    finally:
        await connection.close()