import streamlit as st
from openai import OpenAI

# Título de la app
st.title("Integración con OpenAI")

# Verificar si la clave API está configurada en los secretos
api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error(
        "⚠️ La clave API para OpenAI no está configurada. "
        "Por favor, verifica el archivo `secrets.toml` o "
        "la configuración de secretos en Streamlit Cloud."
    )
else:
    try:
        # Inicializar cliente OpenAI solo si la clave está disponible
        client = OpenAI(api_key=api_key)
        st.success("✅ Cliente OpenAI configurado correctamente.")
        
        # Entrada de texto para interactuar con el modelo
        user_input = st.text_input("Escribe un texto para completar:")

        if user_input:
            with st.spinner("Generando respuesta..."):
                # Llamar a la API de OpenAI para completar el texto
                response = client.Completion.create(
                    model="text-davinci-003",
                    prompt=user_input,
                    max_tokens=50
                )
                # Mostrar el resultado
                completion = response['choices'][0]['text'].strip()
                st.text_area("Respuesta del modelo:", value=completion, height=200)
    except Exception as e:
        st.error(f"Error al inicializar el cliente OpenAI: {e}")

# Instrucciones adicionales
st.markdown(
    """
    ### Cómo usar esta aplicación:
    1. Asegúrate de tener configurada la clave API de OpenAI en `secrets.toml` o en los secretos de Streamlit Cloud.
    2. Ingresa un texto en el cuadro de entrada y espera la respuesta del modelo.
    """
)
