# Módulo centralizado para la conexión con la base de datos PostgreSQL
import os
import psycopg2


# Si existe DATABASE_URL (como en Render al desplegar), la usamos.
# Si no existe, usamos la configuración local para desarrollar en tu computadora.
DATABASE_URL = os.environ.get("DATABASE_URL")

# Datos de conexión local (ajusta usuario/contraseña a tu instalación de pgAdmin)
CONFIG_DB = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "loja1998",
    "dbname": "ferreteria",
}


# Abre y devuelve una nueva conexión a la base de datos
def obtener_conexion():
    if DATABASE_URL:
        # Render entrega el link con sslmode requerido
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    return psycopg2.connect(**CONFIG_DB)
