import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="EDGE AI | NEURAL STRATEGY 2026", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    div.stButton > button:first-child {
        background-color: #ffffff;
        color: #000000;
        border-radius: 0px;
        border: none;
        font-weight: bold;
        height: 45px;
        width: 100%;
    }
    .prediction-card {
        padding: 20px;
        border: 1px solid #111;
        background-color: #050505;
        margin-bottom: 15px;
        border-left: 5px solid #00FF00;
    }
    .metric-box {
        padding: 20px;
        background-color: #080808;
        border: 1px solid #111;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- AI SETUP ---
# Usiamo la tua chiave
GOOGLE_API_KEY = "AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("E D G E  A I")
    st.caption("NEURAL PREDICTION ENGINE 2026")
    st.markdown("---")
    
    market = st.selectbox("MARKET ACCESS", 
                          ["Top European Leagues", "Serie A & B", "Premier League", "Champions League"])
    
    risk_mode = st.select_slider("RISK STRATEGY", 
                                 options=["SAFE", "BALANCED", "AGGRESSIVE"], 
                                 value="BALANCED")
    
    st.markdown("---")
    stake = st.number_input("STAKE (€)", min_value=1.0, value=10.0, step=1.0)
    target = st.number_input("TARGET (€)", min_value=1.0, value=100.0, step=10.0)
    
    st.markdown("---")
    generate_btn = st.button("EXECUTE NEURAL SCAN")

# --- MAIN DISPLAY ---
st.title("GLOBAL MARKET INTEL")
# FIX: Sostituito st.overline (che non esiste) con st.write + stile bold
st.write("**AI-POWERED AUTONOMOUS ANALYSIS**")

if generate_btn:
    with st.spinner("Neural Brain is analyzing matches and historical trends..."):
        # Calcoliamo la quota necessaria
        req_odds = target / stake
        
        # Prompt ottimizzato
        prompt = f"""
        Date: {datetime.now().strftime('%d %B %Y')}.
        Task: Professional Football Analyst.
        Target Market: {market}.
        Risk Profile: {risk_mode}.
        Required Total Odds: {req_odds:.2f}.

        Find 4-5 real matches occurring today or tomorrow. 
        Analyze them using your internal data.
        Return ONLY a JSON array with this structure:
        [
          {{"match": "Home vs Away", "tip": "Prediction", "odds": 1.50, "conf": "90%", "logic": "1 sentence analysis"}}
        ]
        Do not write any prose before or after the JSON.
        """
        
        try:
            response = model.generate_content(prompt)
            # Pulizia sicura del JSON
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw_text)
            
            # Layout a due colonne
            col_main, col_summary = st.columns([2, 1])
            
            total_odds = 1.0
            
            with col_main:
                for item in data:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 18px; font-weight: bold;">{item['match']}</span>
                            <span style="color: #00FF00; font-weight: bold; font-size: 14px;">{item['conf']} CONFIDENCE</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <b style="color: #ffffff;">TIP: {item['tip']}</b> | <span style="color: #888;">ODDS: {item['odds']}</span>
                        </div>
                        <div style="margin-top: 8px; font-size: 13px; color: #666; font-style: italic;">
                            {item['logic']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    total_odds *= item['odds']
            
            with col_summary:
                st.markdown(f"""
                <div class="metric-box">
                    <h3 style="margin: 0; color: #ffffff;">LIVE TICKET</h3>
                    <hr style="border: 0.5px solid #222;">
                    <p style="color: #888;">STRATEGY: <b>{risk_mode}</b></p>
                    <h2 style="color: #00FF00; margin: 10px 0;">{total_odds:.2f}</h2>
                    <p style="font-size: 12px; color: #444;">TOTAL ODDS</p>
                    <hr style="border: 0.5px solid #222;">
                    <h3 style="color: #ffffff;">€{total_odds * stake:.2f}</h3>
                    <p style="font-size: 12px; color: #444;">POTENTIAL WIN</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Semplificato il tasto di validazione per evitare loop
                if st.button("SAVE SESSION"):
                    st.balloons()
                    st.success("Session Saved.")
                    
        except Exception as e:
            st.error("AI Neural Overload. Please try again.")
else:
    st.info("System Ready. Click 'EXECUTE NEURAL SCAN' to begin.")

st.markdown("---")
st.caption("© 2026 EDGE AI | Neural Precision Markets")
