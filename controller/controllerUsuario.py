from random import sample
from bd import *  #Importando conexion BD
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from pymysql.cursors import DictCursor







#Creando una funcion para obtener la lista de carros.
def listarUsuarios():
    conexion_MySQLdb = obtener_conexion()  # Creando mi instancia a la conexión de BD

    # Cursor para obtener los datos de los usuarios
    cur_usuarios = conexion_MySQLdb.cursor()
    cur_usuarios.execute('''
        SELECT u.id, u.nombre, u.correo, u.estado, u.fecha_registro, u.foto, r.nombre_rol AS nombre_rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id
    ''')
    resultadoUsuarios = cur_usuarios.fetchall()
    columnas = [desc[0] for desc in cur_usuarios.description]
    listaUsuarios = [dict(zip(columnas, fila)) for fila in resultadoUsuarios]

    # Cursor para obtener el conteo total
    cur_conteo = conexion_MySQLdb.cursor()
    cur_conteo.execute('SELECT COUNT(*) FROM usuarios where estado=1')
    totalUsuarios = cur_conteo.fetchone()[0]

    # Cerrar los cursores y la conexión
    cur_usuarios.close()
    cur_conteo.close()
    conexion_MySQLdb.close()

    # Retornar los datos en un diccionario
    return {
        'usuarios': listaUsuarios,
        'total': totalUsuarios
    }


def updateUsuario(id=''):
        conexion_MySQLdb = obtener_conexion()
        cursor = conexion_MySQLdb.cursor(DictCursor)
        
        cursor.execute("SELECT * FROM usuarios WHERE id = %s LIMIT 1", [id])
        resultQueryData = cursor.fetchone() #Devolviendo solo 1 registro
        return resultQueryData




def registrarUsuario(nombre='', correo='', password='', id_rol='', estado='', foto=''):
    # Conexión a la base de datos
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor(DictCursor)
    
    # Obtenemos la fecha actual
    fecha_registro = datetime.now().strftime('%Y-%m-%d')  # Fecha en formato 'YYYY-MM-DD'
    
    # SQL de inserción
    sql = """
        INSERT INTO usuarios (nombre, correo, password, id_rol, fecha_registro, estado, foto)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    # Los valores que insertaremos en la base de datos
    valores = (nombre, correo, password, id_rol, fecha_registro, estado, foto)
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



def  recibeActualizarUsuario(nombre, correo, password, id_rol, estado, foto, id):
        conexion_MySQLdb = obtener_conexion()
        cur = conexion_MySQLdb.cursor(DictCursor)
        cur.execute("""
            UPDATE usuarios
            SET 
                nombre   = %s,
                correo  = %s,
                password    = %s,
                id_rol   = %s,
                estado = %s,
                foto= %s
            WHERE id=%s
            """, (nombre, correo, password, id_rol, estado, foto, id))
        conexion_MySQLdb.commit()
        
        cur.close() #cerrando conexion de la consulta sql
        conexion_MySQLdb.close() #cerrando conexion de la BD
        resultado_update = cur.rowcount #retorna 1 o 0
        return resultado_update








    

    





#Crear un string aleatorio para renombrar la foto 
# y evitar que exista una foto con el mismo nombre
def stringAleatorio():
    string_aleatorio = "0123456789abcdefghijklmnopqrstuvwxyz_"
    longitud         = 20
    secuencia        = string_aleatorio.upper()
    resultado_aleatorio  = sample(secuencia, longitud)
    string_aleatorio     = "".join(resultado_aleatorio)
    return string_aleatorio