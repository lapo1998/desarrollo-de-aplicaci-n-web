# Módulo centralizado para la conexión con la base de datos MySQL
import mysql.connector


# Datos de conexión a la base de datos (ajusta usuario/contraseña a tu instalación)
CONFIG_DB = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "ferreteria",
}


# Abre y devuelve una nueva conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**CONFIG_DB)
