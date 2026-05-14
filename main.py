from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from app.model.connection import get_connection
from app.schemas.models import User, UserResponse, LoginRequest, TokenResponse, Court, PaginatedCourts, ReservaCreate, ReservaResponse
from app.auth.jwt_handler import hash_password, verify_password, create_access_token, get_current_user
from loguru import logger


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4200",
        "https://red-deportiva-360-front.vercel.app",
    ],
    allow_origin_regex=r"https://red-deportiva-360-front-.*\.vercel\.app",
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


@app.get("/courts/", response_model=PaginatedCourts)
async def get_courts(
    search: str | None = Query(None, description="Buscar por nombre"),
    precio_max: float | None = Query(None, ge=0),
    capacidad_min: int | None = Query(None, ge=0),
    disponible: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    where = []
    params: list = []

    if search:
        params.append(f"%{search}%")
        where.append(f"nombre ILIKE ${len(params)}")
    if precio_max is not None:
        params.append(precio_max)
        where.append(f"precio <= ${len(params)}")
    if capacidad_min is not None:
        params.append(capacidad_min)
        where.append(f"cantidad_jugadores >= ${len(params)}")
    if disponible is not None:
        params.append(disponible)
        where.append(f"disponible = ${len(params)}")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    connection = await get_connection()
    try:
        total = await connection.fetchval(
            f"SELECT COUNT(*) FROM Canchas {where_sql}",
            *params,
        )
        offset = (page - 1) * page_size
        limit_idx = len(params) + 1
        offset_idx = len(params) + 2
        rows = await connection.fetch(
            f"""
            SELECT id, nombre, ubicacion, disponible, cantidad_jugadores, precio, fecha
            FROM Canchas
            {where_sql}
            ORDER BY precio ASC
            LIMIT ${limit_idx} OFFSET ${offset_idx}
            """,
            *params, page_size, offset,
        )
        return {
            "items": [dict(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Error al obtener las canchas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las canchas: {e}")
    finally:
        await connection.close()


@app.get("/courts/available/{hour}", response_model=list[Court])
async def get_available_courts_by_hour(hour: int):
    if hour < 0 or hour > 23:
        raise HTTPException(status_code=400, detail="La hora debe estar entre 0 y 23")
    connection = await get_connection()
    try:
        rows = await connection.fetch(
            """
            SELECT id, nombre, ubicacion, disponible, cantidad_jugadores, precio, fecha
            FROM Canchas
            WHERE EXTRACT(HOUR FROM fecha) = $1 AND disponible = true
            """,
            hour
        )
        if not rows:
            raise HTTPException(status_code=404, detail=f"No hay canchas disponibles a las {hour}:00")
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener canchas disponibles: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener canchas disponibles: {e}")
    finally:
        await connection.close()


@app.get("/courts/{court_name}", response_model=Court)
async def get_court_information(court_name: str):
    connection = await get_connection()
    try:
        row = await connection.fetchrow(
            """
            SELECT id, nombre, ubicacion, disponible, cantidad_jugadores, precio, fecha
            FROM Canchas
            WHERE LOWER(nombre) = LOWER($1)
            """,
            court_name
        )
        if not row:
            logger.warning(f"No se encontró la cancha con el nombre: {court_name}")
            raise HTTPException(status_code=404, detail=f"No se encontró la cancha con el nombre: {court_name}")
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener la información de la cancha: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener la información de la cancha: {e}")
    finally:
        await connection.close()


@app.post("/reservas/", response_model=ReservaResponse, status_code=201)
async def crear_reserva(
    reserva: ReservaCreate,
    current_user: dict = Depends(get_current_user),
):
    connection = await get_connection()
    try:
        cancha = await connection.fetchrow(
            "SELECT id FROM Canchas WHERE id = $1",
            reserva.cancha_id,
        )
        if not cancha:
            raise HTTPException(status_code=404, detail="La cancha solicitada no existe")

        conflicto = await connection.fetchrow(
            """
            SELECT id FROM Reservas
            WHERE cancha_id = $1
              AND fecha_reserva = $2
              AND estado IN ('pendiente', 'confirmada')
              AND hora_inicio < $4
              AND hora_fin   > $3
            """,
            reserva.cancha_id,
            reserva.fecha_reserva,
            reserva.hora_inicio,
            reserva.hora_fin,
        )
        if conflicto:
            raise HTTPException(
                status_code=409,
                detail=f"El horario de {reserva.hora_inicio} a {reserva.hora_fin} ya está reservado para esa cancha en esa fecha",
            )

        row = await connection.fetchrow(
            """
            INSERT INTO Reservas (usuario_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, estado)
            VALUES ($1, $2, $3, $4, $5, 'pendiente')
            RETURNING id, usuario_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, estado, created_at
            """,
            int(current_user["sub"]),
            reserva.cancha_id,
            reserva.fecha_reserva,
            reserva.hora_inicio,
            reserva.hora_fin,
        )
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear la reserva: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear la reserva: {e}")
    finally:
        await connection.close()


@app.put("/reservas/{reserva_id}/confirmar", response_model=ReservaResponse)
async def confirmar_reserva(
    reserva_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = await get_connection()
    try:
        reserva = await connection.fetchrow(
            "SELECT id, usuario_id, estado FROM Reservas WHERE id = $1",
            reserva_id,
        )
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        if reserva["usuario_id"] != int(current_user["sub"]):
            raise HTTPException(status_code=403, detail="No tienes permiso para confirmar esta reserva")

        if reserva["estado"] != "pendiente":
            raise HTTPException(
                status_code=400,
                detail=f"La reserva no puede confirmarse porque su estado actual es '{reserva['estado']}'",
            )

        row = await connection.fetchrow(
            """
            UPDATE Reservas
            SET estado = 'confirmada'
            WHERE id = $1
            RETURNING id, usuario_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, estado, created_at
            """,
            reserva_id,
        )
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al confirmar la reserva: {e}")
        raise HTTPException(status_code=500, detail=f"Error al confirmar la reserva: {e}")
    finally:
        await connection.close()


@app.get("/reservas/mis-reservas", response_model=list[ReservaResponse])
async def mis_reservas(current_user: dict = Depends(get_current_user)):
    connection = await get_connection()
    try:
        rows = await connection.fetch(
            """
            SELECT id, usuario_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, estado, created_at
            FROM Reservas
            WHERE usuario_id = $1
            ORDER BY fecha_reserva ASC, hora_inicio ASC
            """,
            int(current_user["sub"]),
        )
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al obtener las reservas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener las reservas: {e}")
    finally:
        await connection.close()


@app.delete("/reservas/{reserva_id}", status_code=204)
async def cancelar_reserva(
    reserva_id: int,
    current_user: dict = Depends(get_current_user),
):
    connection = await get_connection()
    try:
        reserva = await connection.fetchrow(
            "SELECT id, usuario_id, estado FROM Reservas WHERE id = $1",
            reserva_id,
        )
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")

        if reserva["usuario_id"] != int(current_user["sub"]):
            raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta reserva")

        if reserva["estado"] == "cancelada":
            raise HTTPException(status_code=400, detail="La reserva ya está cancelada")

        await connection.execute(
            "UPDATE Reservas SET estado = 'cancelada' WHERE id = $1",
            reserva_id,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar la reserva: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar la reserva: {e}")
    finally:
        await connection.close()