from flask import Flask, request, jsonify, render_template
import google.generativeai as genai


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
  system_instruction="Eres un asistente de ayuda amable para ayudar a las personas a registrar su asistencia. Para socializar con una persona se amable, saluda si inicia la comunicacion con la persona. La comunicacion se reinicia cuando la persona reincia con un saludo, ejemplo: Hola, puedes ayudarme, necesito ayuda. El proceso de registro de asistencia es el siguiente, primero se solicitan datos, el correo y la contraseña a partir de obtener los datos estos se validan y se confirma la existencia del empleado para luego pedir si desea registrar su asistencia. El proceso de registro se da cuando la persona quiere registrar su asistencia o cuando la persona inicia la conversacion y no sabe que hacer, cuando tarda 10 segundos en tener o mostrar su duda inicia a preguntarle si quiere registrar su asistencia.",
)

history = []

# Configurar Flask
app = Flask(__name__)

@app.route("/chatbot")
def index():
    return render_template("chatbot.html")  # Cargar la página de inicio (frontend)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"reply": "Por favor, escribe algo."}), 400

    # Crear sesión de chat
    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(user_input)
    reply = response.text

    # Actualizar historial de chat
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [reply]})

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)  # Servir en el puerto 5000
