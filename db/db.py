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

def ejecutar_transaccion(queries):
    """
    Ejecuta múltiples queries en una sola transacción atómica.
    
    Args:
        queries (list): Lista de tuplas con (query, parametros)
        
    Returns:
        int: Último rowid de la última operación INSERT
        
    Ejemplo:
        queries = [
            ("INSERT INTO tabla1 ...", (param1,)),
            ("UPDATE tabla2 SET ...", (param2,))
        ]
        id = ejecutar_transaccion(queries)
    """
    conn = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        for query, params in queries:
            cursor.execute(query, params)
            
        conn.commit()
        return cursor.lastrowid
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
