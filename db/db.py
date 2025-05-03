import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "ventas.db"

def connect_db():
    """Establece conexión con la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

def ejecutar_query(query, parameters=()):
    """Ejecuta una query de modificación"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        conn.commit()
        return cursor.lastrowid

def obtener_datos(query, parameters=()):
    """Obtiene resultados de una consulta SELECT"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        return cursor.fetchall()
