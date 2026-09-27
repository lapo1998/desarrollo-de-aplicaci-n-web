# Módulo centralizado para la conexión con la base de datos PostgreSQL
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

CONFIG_DB = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "dbname": os.environ.get("DB_NAME", "ferreteria"),
    "client_encoding": "utf-8",
    # Fuerza los mensajes de error del servidor en inglés (sin tildes),
    # para evitar un error de codificación de psycopg2 en Windows.
    "options": "-c lc_messages=C",
}


def obtener_conexion():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    return psycopg2.connect(**CONFIG_DB)