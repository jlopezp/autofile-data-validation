import pyodbc
from datetime import datetime
from config import DB_CONFIG

def get_connection():
    """
    Retorna conexión a SQL Server.
    """
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']}"
    )

def registrar_log(negocio, validacion, estado, detalle, usuario):
    """
    Inserta un log en la BD. 
    Si falla la conexión, imprime el error pero NO detiene el programa.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO logs_validaciones (fecha, negocio, validacion, estado, detalle, usuario)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, datetime.now(), negocio, validacion, estado, detalle, usuario)
        conn.commit()
    except Exception as e:
        print(f"[ADVERTENCIA] No se pudo registrar log en BD: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

