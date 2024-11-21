from flask import Flask, render_template, request, jsonify,redirect, url_for,flash, session
from bd import obtener_conexion 
from controller.controllerUsuario import *
from controller.controllerRoles import *
from controller.controllerLogin import *
from controller.controllerAsistencia import *
from element.User import User
from datetime import datetime
from bd import *
from flask import session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user



from pymysql.cursors import DictCursor


app= Flask (__name__)

app.config['SECRET_KEY'] = Config.SECRET_KEY
login_manager_app=LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(id)


@app.route('/')
def index():
    return redirect('login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['correo'], request.form['password'])
        logged_user = ModelUser.login(user)

        if logged_user != None:  # Usuario encontrado  # Contraseña válida
            login_user(logged_user)
            session['user_id'] = logged_user.id
            session['user_name'] = logged_user.nombre
            return redirect('/home')
        else:
            print('Contraseña inválida')
            return render_template('/auth/index.html')
    else:
        print('Usuario no encontrado---------------')
        return render_template('/auth/index.html')
    
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect('login')
    

@app.route('/home')
def home():
    return render_template('home.html', active_page="inicio")



@app.errorhandler(401)
def status_401(error):
    return redirect('/login')

@app.errorhandler(404)
def status_404(error):
    return render_template('404.html'), 404


@app.route('/volver')
def volver():
    if current_user.is_authenticated:  # Verifica si el usuario está autenticado
        return redirect(url_for('home'))  # Redirige a la página principal (o la que prefieras)
    else:
        return redirect(url_for('login'))  # Si no está autenticado, redirige al login


    

@app.route('/registro')
def registro():
    return render_template('registro_asistencia.html', active_page="registro" )



@app.route('/usuarios', methods=['GET','POST'])
@login_required
def usuario():
    print(listarUsuarios())

    return render_template('usuarios/usuarios.html', active_page="usuarios", usuarios = listarUsuarios(),msg='El Registro fue un éxito', tipo=1 )


#RUTAS
@app.route('/registrar-usuario', methods=['GET','POST'])
def addUsuario():
    return render_template('usuarios/add_usuarios.html',  active_page="usuarios", roles=listarRoles())







@app.route('/usuario', methods=['POST'])
def formAddUsuario():
    if request.method == 'POST':
        # Obteniendo los datos del formulario
        nombre = request.form['nombre']
        correo = request.form['correo']
        password =User.generate_hash(request.form['password']) 
        id_rol = request.form['id_rol']
        estado = request.form['estado']
        fecha_registro = datetime.now().strftime('%Y-%m-%d')
        
        if request.files['foto'] != '':
            file = request.files['foto']
            foto = recibeFoto(file)

            # Insertamos los datos del usuario en la base de datos
            resultData = registrarUsuario(nombre, correo, password, id_rol, estado, foto)

            if resultData == 1:
                flash('El Registro fue un éxito', 'success')  # 'success' indica el tipo de mensaje
                session['msg'] = 'El Registro fue un éxito'
                session['tipo'] = 1
            else:
                flash('Error al registrar usuario', 'error')
                session['msg'] = 'Error al registrar usuario'
                session['tipo'] = 0
        else:
            flash('Debe cargar una foto', 'warning')
            session['msg'] = 'Debe cargar una foto'
            session['tipo'] = 2

        return redirect('/usuarios')
    
    

@app.route('/registro-asistencia', methods=['POST'])
def formAddAsistencia():
    if request.method == 'POST':
        resultData = registrarAsistencia(current_user.id)
        if resultData == 1:
            flash('El Registro fue un éxito', 'success')  # 'success' indica el tipo de mensaje
            session['msg'] = 'El Registro fue un éxito'
            session['tipo'] = 1
        else:
            flash('Error al registrar Asistencia', 'error')
            session['msg'] = 'Error al registrar Asistencia'
            session['tipo'] = 0

    return redirect('/home')





@app.route('/form-update-usuario/<string:id>', methods=['GET','POST'])
def formViewUpdate(id):
    if request.method == 'GET':
        resultData = updateUsuario(id)
        if resultData:
             return render_template('usuarios/update_usuarios.html',  dataInfo = resultData, roles=listarRoles())
            
        else:
            return redirect('/usuarios',msg='No existe el carro', tipo= 1)
    else:
        return redirect('/usuarios',msg = 'Metodo HTTP incorrecto', tipo=1)          





@app.route('/actualizar-usuario/<string:id>', methods=['POST'])
def  formActualizarUsuario(id):
    if request.method == 'POST':
        # Obteniendo los datos del formulario
        nombre              = request.form['nombre']
        correo             = request.form['correo']
        password           = request.form['password']
        id_rol             = request.form['id_rol']
        estado             = request.form['estado']
        
        fotoActual = request.form['imageName']
        #Script para recibir el archivo (foto)
        if(request.files['foto']):
            file     = request.files['foto']
            fotoForm = recibeFoto(file)
            resultData = recibeActualizarUsuario(nombre, correo, password, id_rol, estado, fotoForm, id)
        else:
            resultData = recibeActualizarUsuario(nombre, correo, password, id_rol, estado, fotoActual, id)

        if(resultData ==1):
            return redirect('/usuarios')
        else:
            msg ='No se actualizo el registro'
            return redirect('/usuarios')
        


@app.route('/desactivar-usuario/<string:id>', methods=['GET', 'POST'])
def desactivarUsuario(id):
    conexion_MySQLdb = obtener_conexion()
    cur = conexion_MySQLdb.cursor(DictCursor)
    # Actualiza el estado a 0 (desactivado)
    cur.execute('UPDATE usuarios SET estado=0 WHERE id=%s', (id))
    # Asegúrate de hacer commit para que los cambios se guarden en la base de datos
    conexion_MySQLdb.commit()

    # Redirigir de vuelta a la lista de carros o a otra página
    return redirect('/usuarios')

        
@app.route('/activar-usuario/<string:id>', methods=['GET', 'POST'])
def activarUsuario(id):
    conexion_MySQLdb = obtener_conexion()
    cur = conexion_MySQLdb.cursor(DictCursor)
    # Actualiza el estado a 0 (desactivado)
    cur.execute('UPDATE usuarios SET estado=1 WHERE id=%s', (id))
    # Asegúrate de hacer commit para que los cambios se guarden en la base de datos
    conexion_MySQLdb.commit()

    # Redirigir de vuelta a la lista de carros o a otra página
    return redirect('/usuarios')


    
def recibeFoto(file):
    print(file)
    basepath = os.path.dirname (__file__) #La ruta donde se encuentra el archivo actual
    filename = secure_filename(file.filename) #Nombre original del archivo

    #capturando extensión del archivo ejemplo: (.png, .jpg, .pdf ...etc)
    extension           = os.path.splitext(filename)[1]
    nuevoNombreFile     = stringAleatorio() + extension
    #print(nuevoNombreFile)
        
    upload_path = os.path.join (basepath, 'static/img', nuevoNombreFile) 
    file.save(upload_path)

    return nuevoNombreFile

#! --------------------------------------------------------------------------

@app.route('/historial')
def historial():
    print(listarAsistencia(current_user.id))
    return render_template('historial.html', active_page="historial",asistencias = listarAsistencia(current_user.id))







if __name__ == '__main__':
    # Asegúrate de que config existe y está bien configurado
    app.bd.from_object(config['development'])
    
    # Configuración explícita del LoginManager
    login_manager_app.login_view = 'login'

    
    # Ejecutar aplicación (sin debug para manejar errores correctamente)
    app.run()



