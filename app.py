import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EDGE AI | NEURAL CONSOLE", layout="wide")

# --- STYLE LUXURY ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stChatMessage { background-color: #080808; border: 1px solid #111; border-radius: 0px; margin-bottom: 10px; }
    .prediction-card { padding: 15px; border-left: 4px solid #00FF00; background-color: #050505; border-top: 1px solid #111; border-right: 1px solid #111; border-bottom: 1px solid #111; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
GOOGLE_API_KEY = "AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SESSION STATE PER LA CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("E D G E  A I")
    st.caption("NEURAL INTERFACE v2.6")
    st.markdown("---")
    stake = st.number_input("STAKE (€)", min_value=1.0, value=10.0)
    if st.button("CLEAR CHAT"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN DISPLAY ---
st.title("NEURAL SCANNER CONSOLE")
st.write("Digita la tua richiesta nella barra in basso per analizzare i mercati.")

# Visualizza i messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- CHAT INPUT BAR ---
if prompt := st.chat_input("Chiedimi delle partite (es: 'Analizza la Serie A di oggi')"):
    
    # 1. Mostra il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Genera risposta dell'IA
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Neural Streams..."):
            
            full_prompt = f"""
            Oggi è il {datetime.now().strftime('%d/%B/%Y')}. 
            User Request: {prompt}
            
            Agisci come analista esperto. Trova i match reali e fornisci i dati.
            Rispondi SEMPRE con una breve introduzione e poi una lista di match in questo formato HTML:
            <div class="prediction-card">
                <b>SQUADRE</b><br>
                PRONOSTICO @ QUOTA | CONFIDENZA %<br>
                <small>LOGICA BREVE</small>
            </div>
            """
            
            try:
                response = model.generate_content(full_prompt)
                ai_response = response.text
                
                # Visualizza e salva
                st.markdown(ai_response, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                error_msg = "Sistemi sovraccarichi. Riprova tra un istante."
                st.error(error_msg)

# --- INFO FOOTER ---
if not st.session_state.messages:
    st.info("💡 Suggerimento: Prova a scrivere 'Dammi una schedina da quota 5.00 per oggi' oppure 'Quali sono i match più sicuri in Premier League?'")
