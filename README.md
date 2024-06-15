# 🧿 Asistente de Busqueda (Chat + Busqueda)

## Setup (Linux)

1. Instalar un virtual environment `python3 -m venv venv`.
2. Correr el virtual environment `source venv venv/bin/activate`.
3. Instalar las dependencias `pip3 install -r requirements.txt`.
4. Tomar el archivo `.env.template` y configurar las api keys de OpenAI y Tavily.
    - En caso de que alla algun inconveniente probar exportando las variables de ambiente `export OPENAI_APIKEY=<openai-apikey> &&
export TAVILY_API_KEY=<tavaly-api-key>`.
5. Ejecutar con `streamlit main.py`.