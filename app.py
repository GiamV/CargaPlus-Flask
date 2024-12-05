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

# Crear el modelo para la IA
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
  system_instruction="Eres un asistente de ayuda amable para ayudar a las personas a registrar su asistencia. Para socializar con una persona se amable, saluda si inicia la comunicacion con la persona. La comunicacion se reinicia cuando la persona reincia con un saludo, ejemplo: Hola, puedes ayudarme, necesito ayuda. El proceso de registro de asistencia es el siguiente, primero se solicitan datos, el correo y la contraseña a partir de obtener los datos estos se validan y se confirma la existencia del empleado para luego pedir si desea registrar su asistencia. El proceso de registro se da cuando la persona quiere registrar su asistencia o cuando la persona inicia la conversacion y no sabe que hacer, cuando tarda 10 segundos en tener o mostrar su duda inicia a preguntarle si quiere registrar su asistencia.",
)

history = []

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración de la clave secreta
app.config['SECRET_KEY'] = 'tu_clave_secreta'
login_manager_app = LoginManager(app)

# Inicialización del programador de tareas
timezone = pytz.timezone('America/Lima')
scheduler = BackgroundScheduler(timezone=timezone)

# Función de tarea programada
def ejecutar_tarea():
    print(f"Tarea ejecutada a la hora: {datetime.now()}")

# Programar la tarea para que se ejecute todos los días a las 11:00 p.m.
scheduler.add_job(ejecutar_tarea, 'cron', hour=0, minute=15)
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
    datos = listarUsuarios()
    return render_template('home.html', active_page="inicio", usuarios=datos['usuarios'], total=datos['total'])

@app.route('/volver')
def volver():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    conexion_MySQLdb = obtener_conexion()
    cursor = conexion_MySQLdb.cursor()

    id_usuario = current_user.id
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT * FROM asistencia WHERE id_usuario = %s AND fecha = %s AND hora_salida IS NULL", (id_usuario, fecha_hoy))
    registro_existente = cursor.fetchone()

    cursor.close()
    conexion_MySQLdb.close()

    return render_template('registro_asistencia.html', registro_existente=registro_existente, active_page="registro")

@app.route('/usuarios', methods=['GET', 'POST'])
@login_required
def usuario():
    datos = listarUsuarios()
    return render_template('usuarios/usuarios.html', active_page="usuarios", usuarios=datos['usuarios'], total=datos['total'], msg='El Registro fue un éxito', tipo=1)

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
    cur.execute('UPDATE usuarios SET estado=0 WHERE id=%s', (id))
    conexion_MySQLdb.commit()
    return redirect('/usuarios')

@app.route('/activar-usuario/<string:id>', methods=['GET', 'POST'])
def activarUsuario(id):
    conexion_MySQLdb = obtener_conexion()
    cur = conexion_MySQLdb.cursor(DictCursor)
    cur.execute('UPDATE usuarios SET estado=1 WHERE id=%s', (id))
    conexion_MySQLdb.commit()
    return redirect('/usuarios')

@app.route('/historial')
def historial():
    return render_template('historial.html', active_page="historial", asistencias=listarAsistencia(current_user.id))

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
    basepath = os.path.dirname(__file__)
    filename = secure_filename(file.filename)
    extension = os.path.splitext(filename)[1]
    nuevoNombreFile = stringAleatorio() + extension
    upload_path = os.path.join(basepath, 'static/img', nuevoNombreFile)
    file.save(upload_path)
    return nuevoNombreFile

try:
    app.run(debug=True, use_reloader=False)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
