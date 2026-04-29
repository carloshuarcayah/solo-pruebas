import asyncpg
from loguru import logger
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(override=True)


async def get_connection():
    try:
        connection = await asyncpg.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),  
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        logger.info("Conexión a la base de datos establecida correctamente")
        return connection

    except Exception as e:
        logger.error(f"Error al conectar con la BD intenta nueva mente")
        raise ValueError(e)



asyncio.run(get_connection())