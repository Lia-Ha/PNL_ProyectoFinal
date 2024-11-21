import pandas as pd
import streamlit as st
from datetime import datetime
from copy import deepcopy
from openai import OpenAI
import pytz
import json
import logging

# Configura el logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define la API Key directamente en el código
#api_key = "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"


client = OpenAI(api_key=st.secrets["api_key"])

# Configuración inicial de la página
st.set_page_config(page_title="Nova-Infor", page_icon=":pot_of_food:")
st.title("👨‍💻Nova-Infor")

# Mensaje de bienvenida
intro = """¡Bienvenido a Nova-Infor Plus! Soy tu asistente virtual especializado en orientación académica dentro de Ingeniería Informática."""
st.markdown(intro)

# Cargar archivos CSV y manejar errores
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

# Generar el prompt del sistema con datos específicos
def get_system_prompt():
    """Crea el prompt para el modelo, incluyendo reglas basadas en los datos cargados."""
    return f"""
    Eres un asistente virtual experto en orientación académica para estudiantes de Ingeniería Informática.
    Basándote en la información de los siguientes archivos:
    - Entrevistas_maestros.csv: Incluye experiencias y especialidades de profesores.
    - Entrevistas_estudiantes.csv: Contiene testimonios y motivaciones de estudiantes.
    - Entrevistas_maestros_ver2.csv: Proporciona detalles adicionales sobre trayectoria profesional.

    **Reglas importantes:**
    1. Solo utiliza la información contenida en estos archivos. Si no tienes datos suficientes, responde que no hay información disponible.
    2. Proporciona respuestas claras y concisas basadas únicamente en los datos.
    3. Personaliza las respuestas según las necesidades del usuario, utilizando ejemplos relevantes.
    4. Nunca combines información de profesores diferentes sin indicación explícita del usuario.
    """

# Configurar el cliente de OpenAI
client = OpenAI(api_key=st.secrets["api_key"])

def generate_response(user_input):
    """Genera la respuesta basada en el input del usuario."""
    system_prompt = get_system_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    try:
        completion = client.chat_completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.5,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error al generar respuesta: {e}")
        return "Hubo un problema al generar la respuesta. Por favor, intenta nuevamente."

# Mostrar los datos cargados para referencia (opcional)
if st.checkbox("Mostrar datos cargados"):
    with st.expander("Datos de estudiantes"):
        st.dataframe(estudiantes)
    with st.expander("Datos de maestros"):
        st.dataframe(maestros)
    with st.expander("Datos de maestros (versión 2)"):
        st.dataframe(maestros_ver2)

# Entrada del usuario y procesamiento
user_input = st.chat_input("Escribe tu pregunta aquí...")
if user_input:
    st.chat_message("user", avatar="👤").markdown(user_input)
    response = generate_response(user_input)
    st.chat_message("assistant", avatar="🤖").markdown(response)

# Botón para limpiar la conversación
if st.button("Reiniciar conversación"):
    st.experimental_rerun()
