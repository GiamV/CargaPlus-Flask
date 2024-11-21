from element.User import User
from bd import *


class ModelUser():

    @classmethod
    def login(self, user):
        try:
            print
            conexion_MySQLdb = obtener_conexion()
            cursor = conexion_MySQLdb.cursor()
            sql = """
            SELECT u.id, u.nombre, u.correo, u.estado, u.password, r.nombre_rol AS nombre_rol
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id
            WHERE u.correo = %s
            """
            cursor.execute(sql, (user.correo))
            row = cursor.fetchone()
            

            if row != None:
                print('encontre a alguien')
                print(user.password)
                print(row[4])
                
                # Validar la contraseña
                password_valida = User.check_password(row[4], user.password)
                if password_valida:
                    # Crear el objeto User solo si la contraseña es válida
                    return User(row[0], row[1], row[2], row[3], row[4], row[5])
                else:
                    print('Contraseña incorrecta')
                    return None  # Contraseña incorrecta
            else:
                print('estoy en controller')
                return None  # Usuario no encontrado
        except Exception as ex:
            raise Exception(ex)


    @classmethod
    def get_by_id(cls, id):
        try:
            # Establecemos la conexión
            conexion_MySQLdb = obtener_conexion()
            cursor = conexion_MySQLdb.cursor()

            # Usamos parámetros preparados
            sql = """
            SELECT u.id, u.correo, u.password, u.estado, r.nombre_rol, u.nombre, u.foto
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id
            WHERE U.id = %s
            """
            cursor.execute(sql, (id))

            # Recuperamos la fila
            row = cursor.fetchone()

            # Devolvemos un objeto User si se encontró el usuario
            if row != None:
                print('logueado')
                return User(row[0], row[1], row[2],row[3],row[4],row[5],row[6])
            else:
                return None
        except Exception as ex:
            # Mostramos una excepción genérica si algo falla
            raise Exception(f"Error al obtener el usuario: {str(ex)}")