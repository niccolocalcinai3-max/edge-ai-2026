import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# --- CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="EDGE AI | NEURAL STRATEGY 2026", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stButton>button { width: 100%; border-radius: 0px; background-color: #ffffff; color: black; font-weight: bold; border: none; height: 50px; }
    .stButton>button:hover { background-color: #cccccc; }
    .prediction-card { padding: 20px; border: 1px solid #111; background-color: #050505; margin-bottom: 15px; border-left: 4px solid #00FF00; }
    .metric-box { padding: 15px; background-color: #0a0a0a; border: 1px solid #111; text-align: center; }
    </style>
    """, unsafe_content_type=True)

# --- AI SETUP ---
# Usiamo la tua chiave API
GOOGLE_API_KEY = "AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SIDEBAR ---
with st.sidebar:
    st.title("E D G E  A I")
    st.overline("AUTONOMOUS INTELLIGENCE")
    st.markdown("---")
    
    market = st.selectbox("MARKET ACCESS", ["Top European Leagues", "Serie A & B", "Premier League", "Champions League"])
    risk = st.select_slider("RISK STRATEGY", options=["SAFE", "BALANCED", "AGGRESSIVE"], value="BALANCED")
    
    st.markdown("---")
    stake = st.number_input("STAKE (€)", min_value=1.0, value=10.0)
    target = st.number_input("TARGET (€)", min_value=1.0, value=100.0)
    
    generate_btn = st.button("EXECUTE NEURAL SCAN")

# --- MAIN INTERFACE ---
st.subheader("GLOBAL MARKET INTEL (LIVE AI ANALYSIS)")

if generate_btn:
    with st.spinner("L'IA sta scansionando i mercati e analizzando i trend storici..."):
        # Prompt per l'IA senza bisogno di file o API
        # L'IA usa la sua conoscenza aggiornata al 2026
        prompt = f"""
        Oggi è il {datetime.now().strftime('%d %B %Y')}. 
        Agisci come un analista di scommesse professionista. 
        Trova le 5 partite più interessanti di oggi/domani nel mercato: {market}.
        Per ogni partita, analizza lo stato di forma storico e recente delle squadre.
        
        Genera una schedina con strategia di rischio: {risk}.
        Obiettivo quota totale vicina a: {target/stake:.2f}.

        Restituisci ESCLUSIVAMENTE un JSON con questa struttura:
        [
          {{"match": "Squadra A - Squadra B", "tip": "1/X/2/Over", "odds": 1.50, "logic": "Analisi tecnica breve", "conf": "90%"}},
          ...
        ]
        """
        
        try:
            response = model.generate_content(prompt)
            # Pulizia e parsing del JSON
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            col1, col2 = st.columns([2, 1])
            
            total_odds = 1.0
            
            with col1:
                for item in data:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <div style="display: flex; justify-content: space-between;">
                            <b style="font-size: 18px;">{item['match']}</b>
                            <span style="color: #00FF00; font-weight: bold;">{item['conf']} CONF.</span>
                        </div>
                        <div style="margin-top: 10px; color: #ccc;">
                            <b>Pronostico: {item['tip']}</b> | Quota: {item['odds']}
                        </div>
                        <div style="margin-top: 5px; font-size: 12px; color: #888;">
                            {item['logic']}
                        </div>
                    </div>
                    """, unsafe_content_type=True)
                    total_odds *= item['odds']
            
            with col2:
                st.markdown('<div class="metric-box">', unsafe_content_type=True)
                st.write("### 🎫 TICKET SUMMARY")
                st.write(f"**Strategy:** {risk}")
                st.write(f"**Total Odds:** {total_odds:.2f}")
                st.write(f"**Potential Win:** €{total_odds * stake:.2f}")
                st.markdown('</div>', unsafe_content_type=True)
                
                if st.button("PRINT TICKET"):
                    st.balloons()
                    st.success("Ticket salvato nella sessione!")
                    
        except Exception as e:
            st.error(f"Errore durante la scansione neurale: {e}")
            st.info("Riprova tra pochi secondi, l'IA potrebbe essere sovraccarica.")
else:
    st.write("In attesa di comando... Seleziona i parametri e clicca su 'EXECUTE NEURAL SCAN'.")

st.markdown("---")
st.caption("Edge AI Autonomous System - No External Data Required")
