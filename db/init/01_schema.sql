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
