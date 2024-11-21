import pandas as pd
import streamlit as st
from datetime import datetime
from copy import deepcopy
import openai
import logging
from fuzzywuzzy import fuzz

# Configurar logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración inicial de la página
st.set_page_config(page_title="Nova-Infor", page_icon=":computer:")
st.title("👨‍💻 Nova-Infor")

# Mensaje de bienvenida
st.markdown(
    """
    ¡Bienvenido a Nova-Infor, tu consejero virtual en Ingeniería Informática!
    """
)

# Inicializar la clave API con manejo de errores
try:
    openai.api_key = st.secrets["api_key"]
except KeyError:
    st.error("⚠️ La clave `api_key` no está configurada. Agrega esta clave en el archivo `secrets.toml` o en los secretos de Streamlit Cloud.")
    st.stop()

# Cargar datos desde archivos CSV con validación
@st.cache_data
def load_data(file_path):
    """Cargar datos desde un archivo CSV con validación."""
    try:
        data = pd.read_csv(file_path)
        if data.empty:
            raise ValueError(f"El archivo {file_path} está vacío.")
        return data
    except FileNotFoundError:
        st.error(f"❌ El archivo {file_path} no fue encontrado. Verifica la ubicación.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo {file_path}: {e}")
        st.stop()

# Cargar los datos
maestros_df = load_data("Entrevistas_maestros.csv")
estudiantes_df = load_data("Entrevistas_estudiantes.csv")

# Verificar si la columna 'Pregunta' existe
def check_columns(df):
    """Verifica que la columna 'Pregunta' exista en el DataFrame"""
    if "Pregunta" not in df.columns:
        st.error("❌ La columna 'Pregunta' no existe en el archivo CSV.")
        st.stop()

check_columns(maestros_df)
check_columns(estudiantes_df)

# Procesar los datos
def process_data(data):
    """Procesar un DataFrame en un diccionario para búsquedas."""
    result = {}
    for index, row in data.iterrows():
        pregunta = row.get("Pregunta", "").strip()
        if pregunta:
            # Verificar si las columnas tienen datos válidos
            result[pregunta] = {col: (row.get(col, "").strip() if isinstance(row.get(col), str) else "") for col in data.columns if col != "Pregunta"}
    return result

maestros_data = process_data(maestros_df)
estudiantes_data = process_data(estudiantes_df)

# Prompt inicial del sistema
def get_system_prompt():
    """Define el prompt del sistema para el chatbot."""
    return """
    Eres un chatbot experto en orientación académica para estudiantes de Ingeniería Informática.
    Tu objetivo es ayudar a los estudiantes a descubrir su especialidad ideal dentro de la carrera.
    Si no tienes una respuesta directa en tus datos, proporciona una respuesta general y útil.
    """

# Buscar respuesta en los datos
def buscar_respuesta(pregunta_usuario, datos):
    """Buscar una respuesta basada en similitud en los datos proporcionados."""
    max_similarity = 0
    best_match = None
    for pregunta in datos.keys():
        similarity = fuzz.ratio(pregunta.lower(), pregunta_usuario.lower())
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = pregunta
    if max_similarity > 70:  # Umbral de similitud
        return datos[best_match]
    return None

# Generar respuesta con OpenAI
def generate_response(prompt, temperature=0.1, max_tokens=1000):
    """Generar una respuesta combinando datos y OpenAI."""
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # Intentar encontrar una respuesta en los datos de maestros
    respuesta = buscar_respuesta(prompt, maestros_data)
    
    if respuesta:
        # Si se encuentra una respuesta en los datos, devuélvela
        response = "\n".join([f"**{k}:** {v}" for k, v in respuesta.items() if v])
        st.session_state["messages"].append({"role": "assistant", "content": response})
        return response
    else:
        # Usar OpenAI si no hay respuesta directa
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state["messages"],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = completion.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            st.error(f"❌ Error al generar respuesta con OpenAI: {e}")
            logging.error(f"Error OpenAI: {e}")
            return "Lo siento, no puedo responder en este momento."

# Verificar contenido inapropiado
def check_for_inappropriate_content(prompt):
    """Verifica si el prompt contiene contenido inapropiado usando la API de Moderación."""
    try:
        response = openai.Moderation.create(input=prompt)
        if response["results"][0]["flagged"]:
            return True
        return False
    except Exception as e:
        logging.error(f"Error en la API de Moderación: {e}")
        return False

# Inicializar el estado de la sesión
initial_state = [
    {"role": "system", "content": get_system_prompt()},
    {"role": "assistant", "content": "¡Hola! Soy tu asistente virtual para elegir la especialidad ideal en Ingeniería Informática. ¿En qué puedo ayudarte?"},
]

if "messages" not in st.session_state:
    st.session_state["messages"] = deepcopy(initial_state)

# Botón para eliminar conversación
if st.button("Eliminar conversación", key="clear"):
    st.session_state["messages"] = deepcopy(initial_state)

# Mostrar el historial de mensajes
for message in st.session_state["messages"]:
    avatar = "👨‍💻" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    if check_for_inappropriate_content(prompt):
        with st.chat_message("assistant", avatar="👨‍💻"):
            st.markdown("Por favor, mantengamos la conversación respetuosa.")
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        response = generate_response(prompt)
        with st.chat_message("assistant", avatar="👨‍💻"):
            st.markdown(response)
