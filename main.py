import streamlit as st
import pandas as pd
from openai import OpenAI
import logging

# Configuración inicial de la página
st.set_page_config(page_title="Nova-Infor Plus", page_icon="💡")

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Título de la aplicación
st.title("👨‍💻 Nova-Infor Plus")

# Mensaje de bienvenida
intro = """¡Bienvenido a Nova-Infor Plus! Tu asistente virtual especializado en orientación académica dentro de Ingeniería Informática."""
st.markdown(intro)

# Manejo del estado de la sesión
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # Inicializar mensajes

# Botón para reiniciar conversación
if st.button("🔄 Reiniciar conversación"):
    st.session_state["messages"] = []  # Limpiar mensajes
    st.experimental_rerun()  # Recargar la aplicación

# Función para cargar archivos CSV y manejar errores
def load_csv(file_path):
    try:
        data = pd.read_csv(file_path)
        st.success(f"Archivo '{file_path}' cargado correctamente.")
        return data
    except Exception as e:
        st.error(f"No se pudo cargar el archivo '{file_path}': {e}")
        return None

# Cargar los archivos
maestros = load_csv("Entrevistas_maestros.csv")
estudiantes = load_csv("Entrevistas_estudiantes.csv")
maestros_ver2 = load_csv("Entrevistas_maestros_ver2.csv")

# Verificar consistencia de datos
if not (maestros is not None and estudiantes is not None and maestros_ver2 is not None):
    st.warning("Algunos archivos no se cargaron correctamente. Asegúrate de subir todos los archivos necesarios.")

# Generar el prompt del sistema con datos específicos
def get_system_prompt():
    return """
    Eres un asistente virtual experto en orientación académica para estudiantes de Ingeniería Informática.
    Basándote en la información de los siguientes archivos:
    - Entrevistas_maestros.csv
    - Entrevistas_estudiantes.csv
    - Entrevistas_maestros_ver2.csv

    **Reglas importantes**:
    1. Utiliza únicamente la información contenida en los archivos.
    2. Responde con claridad y personalización.
    3. Indica si la información no está disponible.
    """

# Configurar el cliente de OpenAI
client = OpenAI(api_key=st.secrets["api_key"])

def generate_response(user_input):
    """Genera la respuesta basada en el input del usuario."""
    system_prompt = get_system_prompt()
    messages = [{"role": "system", "content": system_prompt}] + st.session_state["messages"] + [{"role": "user", "content": user_input}]
    try:
        completion = client.chat_completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=1000
        )
        response = completion.choices[0].message.content
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["messages"].append({"role": "assistant", "content": response})
        return response
    except Exception as e:
        logging.error(f"Error al generar respuesta: {e}")
        return "Hubo un problema al generar la respuesta. Por favor, intenta nuevamente."

# Generar preguntas sugeridas
st.subheader("Preguntas sugeridas")
suggested_questions = [
    "¿Qué especialidades son las más recomendadas según los profesores?",
    "¿Qué retos enfrentaron los estudiantes al elegir su carrera?",
    "¿Qué habilidades se necesitan para destacar en Ingeniería Informática?",
    "¿Cómo encontrar información sobre las especialidades más demandadas?"
]
for question in suggested_questions:
    if st.button(question):
        response = generate_response(question)
        st.chat_message("assistant", avatar="🤖").markdown(response)

# Entrada del usuario y procesamiento
st.subheader("Haz tu consulta")
user_input = st.chat_input("Escribe tu pregunta aquí...")
if user_input:
    st.chat_message("user", avatar="👤").markdown(user_input)
    response = generate_response(user_input)
    st.chat_message("assistant", avatar="🤖").markdown(response)
