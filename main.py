import streamlit as st
import pandas as pd
from copy import deepcopy
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuración inicial de la página
st.set_page_config(page_title="Nova-Infor", page_icon="🤖", layout="wide")

# Título y mensaje inicial con estilo
st.title("👨‍💻 Nova-Infor: Tu Asistente Académico")
st.subheader("Explora y decide tu especialidad ideal en Ingeniería Informática")
st.markdown("¡Bienvenido! Nova-Infor te ayudará a tomar decisiones informadas sobre tu especialidad. 🚀")

# Cargar datos desde archivos CSV
@st.cache_data
def load_csv(file_path):
    """Cargar datos desde un archivo CSV."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error al cargar el archivo {file_path}: {e}")
        return None

# Cargar entrevistas
maestros = load_csv("Entrevistas_maestros.csv")
estudiantes = load_csv("Entrevistas_estudiantes.csv")

# Prompt del sistema
def get_system_prompt(maestros, estudiantes):
    """Definir el prompt del chatbot basado en los datos."""
    return f"""
Eres un asistente virtual experto en orientación académica en Ingeniería Informática. 
Basándote en los datos de los archivos CSV de **maestros** y **estudiantes**, ayuda a los usuarios a explorar y decidir su especialidad.

### Datos disponibles:
- Maestros: {list(maestros.columns) if maestros is not None else "No hay datos cargados"}
- Estudiantes: {list(estudiantes.columns) if estudiantes is not None else "No hay datos cargados"}

### Instrucciones:
1. Responde exclusivamente utilizando la información de los datos proporcionados.
2. Usa un tono amigable y profesional.
3. Si no hay datos suficientes, sé honesto y pide aclaraciones al usuario.
"""

# Estado inicial de la conversación
initial_state = [
    {"role": "system", "content": get_system_prompt(maestros, estudiantes)},
    {"role": "assistant", "content": "Hola 👋, soy Nova-Infor. ¿Cómo puedo ayudarte a explorar tus opciones de especialidad?"},
]

# Inicializar mensajes en el estado de sesión
if "messages" not in st.session_state:
    st.session_state["messages"] = deepcopy(initial_state)

# Mostrar el historial de mensajes
for message in st.session_state["messages"]:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Entrada de usuario
if user_input := st.chat_input(placeholder="Escribe tu pregunta aquí..."):
    # Mostrar el mensaje del usuario
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Generar respuesta simulada basada en datos
    if maestros is not None and estudiantes is not None:
        response = f"Gracias por tu pregunta. Según los datos, aquí tienes un consejo basado en los maestros y estudiantes..."
    else:
        response = "Por el momento, no tengo datos suficientes para responder. Por favor, verifica que los archivos estén cargados."

    # Mostrar respuesta del asistente
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response)

    # Guardar mensajes en el estado de la sesión
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": response})

# Botón para reiniciar la conversación
clear_button = st.button("🗑️ Reiniciar conversación", key="clear")
if clear_button:
    st.session_state["messages"] = deepcopy(initial_state)  # Reiniciar los mensajes
    st.experimental_rerun()
