from random import sample
from bd import *  #Importando conexion BD
from datetime import datetime
import os
from werkzeug.utils import secure_filename

#Creando una funcion para obtener la lista de carros.
def listarRoles():
    conexion_MySQLdb = obtener_conexion()  # Creando mi instancia a la conexión de BD
    cur = conexion_MySQLdb.cursor()

    querySQL = "SELECT * FROM roles"
    cur.execute(querySQL)
    resultadoBusqueda = cur.fetchall()  # fetchall() Obtener todos los registros

    # Obtener los nombres de las columnas
    columnas = [desc[0] for desc in cur.description]

    # Convertir las filas de resultados a diccionarios
    listaRoles = []
    for fila in resultadoBusqueda:
        rol = dict(zip(columnas, fila))  # Emparejar los nombres de las columnas con los valores de cada fila
        listaRoles.append(rol)

    cur.close()  # Cerrando conexión SQL
    conexion_MySQLdb.close()  # Cerrando conexión de la BD    

    return listaRoles