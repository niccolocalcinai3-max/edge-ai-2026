import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="EDGE NEURAL V16 - DUAL STRATEGY", layout="wide")

# UI Styling migliorato per la visibilità Gold
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; border-radius: 10px; }
    .gold-btn>div>button { background-color: #FFD700 !important; border: 2px solid #B8860B !important; }
    .safe-card { border-left: 5px solid #00FF00; background: #0A0A0A; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .risk-card { border-left: 5px solid #FF4B4B; background: #1A0505; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .section-title { color: #FFD700; font-size: 1.5em; font-weight: bold; border-bottom: 1px solid #FFD700; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA CARICAMENTO ESPERTO ---
def load_expert_picks(strategy):
    if strategy == "SAFE":
        st.session_state['active_ticket'] = [
            {"match": "Arsenal vs Luton Town", "tip": "1 + OVER 2.5", "odds": 1.40, "conf": 95},
            {"match": "Manchester City vs West Ham", "tip": "1 + OVER 1.5", "odds": 1.35, "conf": 92},
            {"match": "Real Madrid vs Villarreal", "tip": "1", "odds": 1.45, "conf": 85}
        ]
        st.session_state['strategy_name'] = "🛡️ STRATEGIA SAFE (BANKER)"
    else:
        st.session_state['active_ticket'] = [
            {"match": "Bologna vs Inter", "tip": "PAREGGIO (X)", "odds": 3.60, "conf": 40},
            {"match": "Newcastle vs Man Utd", "tip": "2 + GOAL", "odds": 4.80, "conf": 35},
            {"match": "Athletic Bilbao vs Atl. Madrid", "tip": "1 + UNDER 2.5", "odds": 4.20, "conf": 30},
            {"match": "B. Dortmund vs Stoccarda", "tip": "OVER 3.5 + GOAL", "odds": 3.20, "conf": 45},
            {"match": "Marsiglia vs Nizza", "tip": "X + UNDER 2.5", "odds": 3.50, "conf": 38}
        ]
        st.session_state['strategy_name'] = "💣 STRATEGIA SPECULATIVA (TARGET 100)"

# --- SIDEBAR CONTROLLI ---
st.sidebar.title("🎮 DUAL CONTROL PANEL")
st.sidebar.subheader("Carica Analisi Esperto")

# Bottoni per caricamento rapido
if st.sidebar.button("🛡️ CARICA SCHEDINA SAFE"):
    load_expert_picks("SAFE")

st.sidebar.markdown('<div class="gold-btn">', unsafe_allow_html=True)
if st.sidebar.button("💣 CARICA QUOTA 100"):
    load_expert_picks("RISK")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()
bankroll = st.sidebar.number_input("Tuo Budget €", min_value=10.0, value=200.0)

if st.sidebar.button("🗑️ RESET"):
    st.session_state.clear()
    st.rerun()

# --- MAIN DISPLAY ---
st.title("🧠 EXPERT MARKET ANALYSIS")

if 'active_ticket' in st.session_state:
    st.markdown(f'<div class="section-title">{st.session_state["strategy_name"]}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        total_odds = 1.0
        ticket_text = f"{st.session_state['strategy_name']}\nData: {datetime.now().strftime('%d/%m/%Y')}\n\n"
        
        for m in st.session_state['active_ticket']:
            card_style = "safe-card" if "SAFE" in st.session_state['strategy_name'] else "risk-card"
            st.markdown(f"""
                <div class="{card_style}">
                    <b style="font-size:1.2em;">{m['match']}</b><br>
                    <span style="color:#00FF00">Esito: {m['tip']}</span> | Quota: <b>{m['odds']}</b> | Confidenza: {m['conf']}%
                </div>
            """, unsafe_allow_html=True)
            total_odds *= m['odds']
            ticket_text += f"• {m['match']}: {m['tip']} (@{m['odds']})\n"

    with col2:
        st.subheader("📊 Calcolo Rendimento")
        # Calcolo dinamico dello stake (più alto per safe, minimo per quota 100)
        stake_factor = 0.10 if "SAFE" in st.session_state['strategy_name'] else 0.02
        suggested_stake = round(bankroll * stake_factor, 2)
        pot_win = round(total_odds * suggested_stake, 2)
        
        st.metric("QUOTA TOTALE", f"{total_odds:.2f}")
        st.metric("STAKE CONSIGLIATO", f"€{suggested_stake}")
        st.metric("POTENZIALE VINCITA", f"€{pot_win}")
        
        # Area per note/copia
        ticket_text += f"\nQUOTA TOTALE: {total_odds:.2f}\nSTAKE: €{suggested_stake}\nVINCITA: €{pot_win}"
        st.text_area("Copia per Note/WhatsApp:", value=ticket_text, height=200)
        
        st.download_button("📥 SCARICA BIGLIETTO", data=ticket_text, file_name="schedina_expert.txt")

else:
    st.info("👈 Seleziona una strategia dalla barra laterale per caricare i pronostici dell'Analista Senior.")
    st.image("https://img.icons8.com/nolan/512/statistics.png", width=100)
