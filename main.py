# Imports de LangChain
from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

# Import de Streamlit
import streamlit as st

# Configuración de la página de Streamlit
st.set_page_config(page_title="LangChain: Chat with search", page_icon="🦜") # Configuracion de la pagina
st.title("🧿 Asistente de Busqueda (Chat + Busqueda)") # Titulo principal

# Cuadro para ingresar la API Key de OpenAI
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password") # OpenAI API KEY BOX

# Cuadro para ingresar la API Key de OpenAI
tavily_api_key = st.sidebar.text_input("Tavily API Key", type="password") # Tavily API KEY BOX

# Inicializamos el historial de mensajes
msgs = StreamlitChatMessageHistory() # Seteamos el historial de mensajes

# Configuramos la memoria para almacenar el historial de la conversación
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

# Reseteamos el historial de mensajes si no hay mensajes o se presiona el botón de reset
if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()  # Limpiamos el historial
    msgs.add_ai_message("Hola mi nombre es Iris, soy la asistente personal de Iridia AI 🧿.")  # Añadimos un mensaje inicial del asistente
    msgs.add_ai_message("Con qué podría ayudarte? 🤔")  # Añadimos un mensaje inicial del asistente
    st.session_state.steps = {}  # Inicializamos los pasos de la sesión

# Definimos los avatares para el usuario y el asistente
avatars = {"human": "user", "ai": "assistant"}

# Renderizamos los mensajes previos en el chat
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):  # Mostramos el mensaje con el avatar correspondiente
        # Renderizamos los pasos intermedios si hay alguno guardado
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue  # Omitimos los pasos que generaron excepciones
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)  # Mostramos el log del paso
                st.write(step[1])  # Mostramos el resultado del paso
        st.write(msg.content)  # Mostramos el contenido del mensaje

# Capturamos la entrada del usuario en el chat
if prompt := st.chat_input(placeholder="Cual es el clima en Buenos Aires en este momento?"):
    st.chat_message("user").write(prompt)  # Mostramos la pregunta del usuario en el chat

    # Verificamos si la API Key de OpenAI está presente
    if not openai_api_key:
        st.info("Pibe, me parece que vas a tener que poner una api key de Open AI")  # Informamos al usuario que necesita la API Key
        st.stop()  # Detenemos la ejecución si no hay API Key

    # Configuramos el modelo de lenguaje de OpenAI
    llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, streaming=True)
    
    # Definimos las herramientas que el agente puede utilizar
    tools = [TavilySearchResults(max_results=3, tavily_api_key=tavily_api_key)]
    
    # Creamos el agente conversacional con las herramientas definidas
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    
    # Creamos el ejecutor del agente con las herramientas y la memoria
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    
    # Procesamos la respuesta del asistente
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)  # Configuramos el callback handler de Streamlit
        cfg = RunnableConfig()  # Configuramos los parámetros ejecutables
        cfg["callbacks"] = [st_cb]  # Añadimos el callback de Streamlit
        response = executor.invoke(prompt, cfg)  # Ejecutamos la invocación del prompt y obtenemos la respuesta
        st.write(response["output"])  # Mostramos la respuesta del asistente
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]  # Guardamos los pasos intermedios
