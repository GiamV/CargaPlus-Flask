from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, correo, password,estado="", rol="", nombre="",foto=""):
        self.id = id
        self.correo = correo
        self.password = password
        self.estado=estado
        self.rol = rol
        self.nombre = nombre
        self.foto = foto

    @classmethod
    def check_password(self, hashed_password, password):
        # Compara la contraseña proporcionada con el hash almacenado
        return check_password_hash(hashed_password, password)
    
    @classmethod
    def generate_hash(self, password):
        # Genera y devuelve el hash de la contraseña
        return generate_password_hash(password)


# Generar un hash de ejemplo
hashed_password = User.generate_hash("ingreso")
print(f"Hash generado: {hashed_password}")

# Verificar si la contraseña ingresada es correcta
correct = User.check_password(hashed_password, "ingreso")
print(f"¿La contraseña es correcta? {correct}")
