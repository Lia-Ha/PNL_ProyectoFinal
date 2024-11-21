import pandas as pd
import streamlit as st
from datetime import datetime
from openai import OpenAI
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Botón para reiniciar conversación
if st.button("Reiniciar conversación"):
    st.experimental_rerun()

# Configuración inicial de la página
st.set_page_config(page_title="Nova-Infor Plus", page_icon="💡")
st.title("👨‍💻 Nova-Infor Plus")

# Mensaje de bienvenida
intro = """¡Bienvenido a Nova-Infor Plus! Tu asistente virtual especializado en orientación académica dentro de Ingeniería Informática."""
st.markdown(intro)

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
    """Crea el prompt para el modelo, incluyendo reglas basadas en los datos cargados."""
    return f"""
    Eres un asistente virtual experto en orientación académica para estudiantes de Ingeniería Informática.
    Basándote en la información de los siguientes archivos:
    - Entrevistas_maestros.csv: Experiencias y especialidades de profesores.
    - Entrevistas_estudiantes.csv: Testimonios y motivaciones de estudiantes.
    - Entrevistas_maestros_ver2.csv: Detalles adicionales sobre trayectoria profesional.

    **Reglas importantes:**
    1. Solo utiliza la información contenida en estos archivos. Si no tienes datos suficientes, responde que no hay información disponible.
    2. Proporciona respuestas claras y personalizadas según los intereses del usuario.
    3. Utiliza ejemplos relevantes y específicos basados en los datos disponibles.
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

# Mostrar datos cargados y filtros de búsqueda
if st.checkbox("Mostrar datos cargados y buscar información"):
    with st.expander("Datos de estudiantes"):
        st.dataframe(estudiantes)
    with st.expander("Datos de maestros"):
        st.dataframe(maestros)
    with st.expander("Datos de maestros (versión 2)"):
        st.dataframe(maestros_ver2)

    # Agregar filtros para explorar datos
    st.subheader("Buscar información específica")
    search_column = st.selectbox("Selecciona una columna para buscar", estudiantes.columns)
    search_query = st.text_input("Introduce un término de búsqueda")
    if search_query:
        filtered_data = estudiantes[estudiantes[search_column].str.contains(search_query, na=False, case=False)]
        st.write(f"Resultados encontrados para '{search_query}':")
        st.dataframe(filtered_data)

# Mostrar preguntas sugeridas en tabla y permitir consultas
st.subheader("Preguntas sugeridas")

# Crear tabla en formato Markdown para preguntas
table = """
| **Pregunta** |
|--------------|
| ¿Qué especialidades son las más recomendadas según los profesores? |
| ¿Qué retos enfrentaron los estudiantes al elegir su carrera?       |
| ¿Qué habilidades se necesitan para destacar en Ingeniería Informática? |
| ¿Cómo encontrar información sobre las especialidades más demandadas? |
"""
st.markdown(table)

# Entrada del usuario y procesamiento
st.subheader("Haz tu consulta")
user_input = st.chat_input("Escribe tu pregunta aquí...")
if user_input:
    st.chat_message("user", avatar="👤").markdown(user_input)
    response = generate_response(user_input)
    st.chat_message("assistant", avatar="🤖").markdown(response)

# Herramienta para explorar especialidades
if st.checkbox("Explorar especialidades"):
    st.subheader("Explorar especialidades")
    if maestros is not None:
        specializations = maestros["Especialidad"].unique()
        selected_specialization = st.selectbox("Selecciona una especialidad", specializations)
        specialization_data = maestros[maestros["Especialidad"] == selected_specialization]
        st.write(f"Información sobre la especialidad '{selected_specialization}':")
        st.dataframe(specialization_data)
