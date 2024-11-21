from random import sample
from bd import *  #Importando conexion BD
from datetime import datetime, time

import os
from werkzeug.utils import secure_filename
from pymysql.cursors import DictCursor




def listarAsistencia(id_usuario=''):
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor(DictCursor)
    cursor.execute("SELECT * FROM asistencia WHERE id_usuario = %s", [id_usuario])
    
    resultQueryData = cursor.fetchall() 
    
    return resultQueryData



def registrarAsistencia(id_usuario=''):
    # Conexión a la base de datos
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor(DictCursor)
    
    # Obtenemos la fecha actual
    fecha = datetime.now().strftime('%Y-%m-%d')  # Fecha en formato 'YYYY-MM-DD'
    hora_entrada = datetime.now().strftime('%H:%M:%S')    # Hora en formato 'HH:MM:SS'
    hora_entrada_actual = datetime.now().time()
# Definir rangos para el estado
    hora_asistencia = time(8, 0, 0)  # 8:00 AM
    hora_tardanza = time(23, 45, 0)  # 8:15 AM

    # Determinar el status basado en la hora de entrada
    if hora_entrada_actual < hora_asistencia:
        status = "Asistencia"
    elif hora_entrada_actual <= hora_tardanza:
        status = "Tardanza"
    else:
        status = "Falta"
    
    # SQL de inserción
    sql = """
        INSERT INTO asistencia (id_usuario, fecha, hora_entrada, hora_salida, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    # Los valores que insertaremos en la base de datos
    valores = (id_usuario, fecha, hora_entrada, None,status)
    print("Ejecutando SQL:", sql)
    print("Con valores:", valores)

    # Ejecutamos el SQL
    cursor.execute(sql, valores)
    conexion_MySQLdb.commit()
    # Cerrar conexiones
    cursor.close()
    conexion_MySQLdb.close()
    resultado_insert = cursor.rowcount #retorna 1 o 0
    print('Entro try')
    return resultado_insert 