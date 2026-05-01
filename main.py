from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.model.connection import get_connection
from app.schemas.models import User, UserResponse, LoginRequest, TokenResponse
from app.auth.jwt_handler import hash_password, verify_password, create_access_token, get_current_user
from loguru import logger


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users/", response_model=UserResponse)
async def create_user(user: User):
    connection = await get_connection()
    try:
        hashed_password = hash_password(user.password)
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


@app.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    connection = await get_connection()
    try:
        row = await connection.fetchrow(
            "SELECT id, password FROM Usuarios WHERE dni = $1",
            credentials.dni
        )
        if not row or not verify_password(credentials.password, row["password"]):
            raise HTTPException(status_code=401, detail="DNI o contraseña incorrectos")
        token = create_access_token(data={"sub": str(row["id"])})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        await connection.close()


@app.get("/users/information", response_model=list[UserResponse])
async def get_user_information(current_user: dict = Depends(get_current_user)):
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