CREATE TABLE IF NOT EXISTS Usuarios (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    apellido    VARCHAR(100) NOT NULL,
    dni         VARCHAR(8) UNIQUE NOT NULL,
    telefono    VARCHAR(9) NOT NULL,
    password    TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usuarios_dni ON Usuarios(dni);

CREATE TABLE IF NOT EXISTS Canchas (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    ubicacion           VARCHAR(255) NOT NULL,
    disponible          BOOLEAN NOT NULL DEFAULT TRUE,
    cantidad_jugadores  INT NOT NULL,
    precio              NUMERIC(10, 2) NOT NULL,
    fecha               TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_canchas_nombre ON Canchas(LOWER(nombre));

CREATE TABLE IF NOT EXISTS Reservas (
    id              SERIAL PRIMARY KEY,
    usuario_id      INT NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    cancha_id       INT NOT NULL REFERENCES Canchas(id) ON DELETE CASCADE,
    fecha_reserva   DATE NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente'
                    CHECK (estado IN ('pendiente', 'confirmada', 'cancelada')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (hora_fin > hora_inicio)
);

CREATE INDEX IF NOT EXISTS idx_reservas_usuario ON Reservas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_reservas_cancha_fecha ON Reservas(cancha_id, fecha_reserva);
