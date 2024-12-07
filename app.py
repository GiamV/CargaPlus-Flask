from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
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
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import google.generativeai as genai
from pymysql.cursors import DictCursor
import os
from werkzeug.utils import secure_filename

# Configuración del API Key para Google Generative AI
genai.configure(api_key="AIzaSyDItV4QhK26AYtqVajq-kFn3x6Lb43hTHM")

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction="Eres un asistente de ayuda amable para ayudar a las personas a registrar su asistencia. Para socializar con una persona se amable, saluda si inicia la comunicacion con la persona. La comunicacion se reinicia cuando la persona reincia con un saludo, ejemplo: Hola, puedes ayudarme, necesito ayuda. El proceso de registro de asistencia es el siguiente, primero se solicitan datos, el correo y la contraseña a partir de obtener los datos estos se validan y se confirma la existencia del empleado para luego pedir si desea registrar su asistencia. El proceso de registro se da cuando la persona quiere registrar su asistencia o cuando la persona inicia la conversacion y no sabe que hacer, cuando tarda 10 segundos en tener o mostrar su duda inicia a preguntarle si quiere registrar su asistencia. Los mensajes cuando se envian los datos deben ser: Gracias. Dame un momento para validar tus datos. Tus datos son correctos, Gustavo. ¿Deseas registrar tu asistencia ahora?, nunca incluyas: La palabra simulacion. Cuando ingreso los datos correo y contraseña, y me indiques que se esta registrando la asistencia no nigas Simulacion Exitosa, solo indica se asistencia registada y muestra un emoji. Me muestras esto en la conversacion: Gracias. Dame un momento para validar tus datos... (Simulación de validación) Tus datos son correctos, Gustavo. ¿Deseas registrar tu asistencia ahora?, no me indiques que es una simulacion. ",
)

history = []

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración de la clave secreta
app.config['SECRET_KEY'] = Config.SECRET_KEY
login_manager_app = LoginManager(app)

# Función que se ejecutará automáticamente
def ejecutar_tarea():
    print(f"Tarea ejecutada a la hora: {datetime.now()}")

# Zona horaria de Perú
timezone = pytz.timezone('America/Lima')

# Crear el programador
scheduler = BackgroundScheduler(timezone=timezone)

# Programar la tarea para que se ejecute todos los días a las 11:00 p.m.
scheduler.add_job(ejecutar_tarea, 'cron', hour=0, minute=15)

# Iniciar el programador
scheduler.start()

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

        if logged_user:
            login_user(logged_user)
            session['user_id'] = logged_user.id
            session['user_name'] = logged_user.nombre
            return redirect('/home')
        else:
            print('Contraseña inválida')
            return render_template('/auth/index.html')
    return render_template('/auth/index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('login')

@app.route('/home')
def home():
    print(listarUsuarios())
    datos = listarUsuarios()
    return render_template('home.html', active_page="inicio", usuarios=datos['usuarios'], total=datos['total'])

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


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor()

    # Obtener el ID del usuario actual desde current_user
    id_usuario = current_user.id

    # Comprobar si ya existe un registro de entrada para el usuario hoy
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM asistencia WHERE id_usuario = %s AND fecha = %s AND hora_salida IS NULL", (id_usuario, fecha_hoy))
    registro_existente = cursor.fetchone()  # Si existe un registro de entrada, se devolverá un registro

    if request.method == 'POST':
        print('Hola')
    '''
        if registro_existente:  # Si ya tiene una entrada, registrar la salida
            hora_salida = datetime.now().strftime('%H:%M:%S')
            cursor.execute("UPDATE asistencia SET hora_salida = %s WHERE id_usuario = %s AND fecha = %s", (hora_salida, id_usuario, fecha_hoy))
        else:  # Si no tiene una entrada, registrar la entrada
            hora_entrada = datetime.now().strftime('%H:%M:%S')
            cursor.execute("INSERT INTO asistencia (id_usuario, fecha, hora_entrada, hora_salida, status) VALUES (%s, %s, %s, NULL, 'Asistencia')", (id_usuario, fecha_hoy, hora_entrada))

        conexion_MySQLdb.commit()
        cursor.close()
        conexion_MySQLdb.close()
        return redirect(url_for('registro'))  # Redirigir para evitar reenvío de formulario
    '''
            
    cursor.close()
    conexion_MySQLdb.close()

    return render_template('registro_asistencia.html', registro_existente=registro_existente, active_page="registro")

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuario():
    print(listarUsuarios())
    datos = listarUsuarios()
    return render_template('usuarios/usuarios.html', active_page="usuarios", usuarios=datos['usuarios'], total=datos['total'], msg='El Registro fue un éxito', tipo=1)

# RUTAS
@app.route('/registrar-usuario', methods=['GET', 'POST'])
def addUsuario():
    return render_template('usuarios/add_usuarios.html', active_page="usuarios", roles=listarRoles())


@app.route('/usuario', methods=['POST'])
def formAddUsuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = User.generate_hash(request.form['password'])
        id_rol = request.form['id_rol']
        estado = request.form['estado']
        fecha_registro = datetime.now().strftime('%Y-%m-%d')

        if request.files['foto']:
            file = request.files['foto']
            foto = recibeFoto(file)
            
            # Insertamos los datos del usuario en la base de datos
            resultData = registrarUsuario(nombre, correo, password, id_rol, estado, foto)

            if resultData == 1:
                flash('El Registro fue un éxito', 'success')
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

@app.route('/form-update-usuario/<string:id>', methods=['GET', 'POST'])
def formViewUpdate(id):
    if request.method == 'GET':
        resultData = updateUsuario(id)
        if resultData:
            return render_template('usuarios/update_usuarios.html', dataInfo=resultData, roles=listarRoles())
        return redirect('/usuarios')
    return redirect('/usuarios')


@app.route('/actualizar-usuario/<string:id>', methods=['POST'])
def formActualizarUsuario(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        id_rol = request.form['id_rol']
        estado = request.form['estado']
        fotoActual = request.form['imageName']

        if request.files['foto']:
            file = request.files['foto']
            fotoForm = recibeFoto(file)
            resultData = recibeActualizarUsuario(nombre, correo, password, id_rol, estado, fotoForm, id)
        else:
            resultData = recibeActualizarUsuario(nombre, correo, password, id_rol, estado, fotoActual, id)

        if resultData == 1:
            return redirect('/usuarios')
        else:
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


@app.route('/historial')
def historial():
    print(listarAsistencia(current_user.id))
    return render_template('historial.html', active_page="historial",asistencias = listarAsistencia(current_user.id))

# CHATBOT RUTA
#@app.route("/chatbot")
#def chatbot_index():
#    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"reply": "Por favor, escribe algo."}), 400

    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(user_input)
    reply = response.text

    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [reply]})

    return jsonify({"reply": reply})


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

try:
    app.run(debug=True, use_reloader=False)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
