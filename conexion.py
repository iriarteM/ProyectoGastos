import sqlite3

def conectar_bd():
    try:
        conexion = sqlite3.connect('database/database.db')
        return conexion

    except sqlite3.Error as ex:
        print("Error al conectar a la base de datos SQLite:", ex)
        return None

def ejecutar_query(conexion, query, parametros=None):
    try:
        cursor = conexion.cursor()
        if parametros is None:
            cursor.execute(query)
        else:
            cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        return resultados

    except sqlite3.Error as ex:
        print("Error al ejecutar la consulta:", ex)
        return None

def cerrar_bd(conexion):
    if conexion is not None:
        conexion.close()
