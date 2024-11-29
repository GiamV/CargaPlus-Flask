from random import sample
from bd import *  #Importando conexion BD
from datetime import datetime, time

import os
from werkzeug.utils import secure_filename
from pymysql.cursors import DictCursor
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler



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
    
    # Obtenemos la fecha y hora actuales
    fecha = datetime.now().strftime('%Y-%m-%d')  # Fecha en formato 'YYYY-MM-DD'
    hora_actual = datetime.now().strftime('%H:%M:%S')  # Hora en formato 'HH:MM:SS'

    # Verificar si ya existe un registro de entrada sin salida para hoy
    consulta = """
        SELECT id, hora_entrada, hora_salida
        FROM asistencia
        WHERE id_usuario = %s AND fecha = %s AND hora_salida IS NULL
        ORDER BY hora_entrada DESC
        LIMIT 1
    """
    cursor.execute(consulta, (id_usuario, fecha))
    registro_existente = cursor.fetchone()

    if registro_existente:
        # Si hay un registro sin hora de salida, actualizamos con la hora actual
        sql_update = """
            UPDATE asistencia
            SET hora_salida = %s
            WHERE id = %s
        """
        cursor.execute(sql_update, (hora_actual, registro_existente['id']))
        conexion_MySQLdb.commit()
        mensaje = 0
    else:
        # Si no hay registro de entrada, creamos uno nuevo con la hora actual como entrada
        hora_entrada_actual = datetime.now().time()

        # Definir rangos para el estado
        hora_asistencia = time(8, 0, 0)  # 8:00 AM
        hora_tardanza = time(8, 15, 0)  # 8:15 AM

        # Determinar el estado basado en la hora de entrada
        if hora_entrada_actual < hora_asistencia:
            status = "Asistencia"
        elif hora_entrada_actual <= hora_tardanza:
            status = "Tardanza"
        else:
            status = "Falta"

        # Crear un nuevo registro de entrada
        sql_insert = """
            INSERT INTO asistencia (id_usuario, fecha, hora_entrada, hora_salida, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (id_usuario, fecha, hora_actual, None, status)
        cursor.execute(sql_insert, valores)
        conexion_MySQLdb.commit()
        mensaje = 1

    # Cerrar conexiones
    cursor.close()
    conexion_MySQLdb.close()
    
    # Retornar un mensaje indicando el resultado
    return mensaje


def registrarFaltasAutomatica():
    # Conexión a la base de datos
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor(DictCursor)

    # Obtenemos la fecha actual
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Consulta para obtener los usuarios que no registraron asistencia en el día actual
    consulta = """
        SELECT u.id AS id_usuario
        FROM usuarios u
        LEFT JOIN asistencia a ON u.id = a.id_usuario AND a.fecha = %s
        WHERE a.id IS NULL
    """
    cursor.execute(consulta, (fecha_hoy,))
    usuarios_sin_asistencia = cursor.fetchall()

    # Insertar registros de falta para cada usuario que no asistió
    sql_insert_falta = """
        INSERT INTO asistencia (id_usuario, fecha, hora_entrada, hora_salida, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    for usuario in usuarios_sin_asistencia:
        cursor.execute(sql_insert_falta, (usuario['id_usuario'], fecha_hoy, None, None, "Falta"))

    # Confirmar cambios
    conexion_MySQLdb.commit()

    # Cerrar conexiones
    cursor.close()
    conexion_MySQLdb.close()
    
    print(f"Se registraron faltas automáticamente para los usuarios sin asistencia el día {fecha_hoy}.")


'''
import pytz

# Zona horaria de Perú
timezone = pytz.timezone('America/Lima')

# Crear el programador
scheduler = BackgroundScheduler(timezone=timezone)

# Programar la tarea para que se ejecute todos los días a las 11:00 p.m.
scheduler.add_job(registrarFaltasAutomatica, 'cron', hour=23, minute=0)

# Iniciar el programador
scheduler.start()

try:
    while True:
        pass  # Mantener el programa en ejecución
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
'''