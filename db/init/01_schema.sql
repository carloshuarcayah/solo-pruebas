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
