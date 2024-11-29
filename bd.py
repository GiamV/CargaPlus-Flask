import pymysql

class DevelopmentConfig():
    DEBUG = False

class Config:

    SECRET_KEY = 'B!1weNAt1T^%kvhUI*S^'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '1234'
    MYSQL_DB = 'SistemaAsistencia'

config = {
    'development': DevelopmentConfig
}

def obtener_conexion():
    try:
        conexion = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            db=Config.MYSQL_DB
            
        )
        print("Conexión exitosa a la base de datos.")
        return conexion
    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None