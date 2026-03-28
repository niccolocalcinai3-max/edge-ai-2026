import streamlit as st
import os

# --- CONFIGURAZIONE ---
SAVE_FILE = "gold_storage.txt"
st.set_page_config(page_title="EDGE PRO V25", layout="wide")

# --- DATABASE STRATEGIE CRAZY TIME ---
STRATEGIES = {
    "SAFE (Low Risk)": {
        "1. THE SHIELD (1-2)": "70% Copertura. Puntata: 4u su '1', 2u su '2'. Obiettivo: Conservazione capitale.",
        "2. LOW VOLATILITY MIX": "Copre 1, 2 e 5. Puntata: 3u su '1', 2u su '2', 1u su '5'. Recupero costante.",
        "3. THE GRINDER": "Punta solo su '1' e tutti i Bonus (0.5u ciascuno). Protegge dai giri vuoti.",
        "4. ANTI-VARIANCE": "80% della puntata su '2', 20% diviso tra i 4 Bonus. Bilanciamento perfetto.",
        "5. CONSERVATIVE BONUS": "Punta forte su '5' e '10' per pagare i tentativi sui Bonus Cash Hunt e Coin Flip."
    },
    "RISKY (High Reward)": {
        "6. BONUS HUNTER PRO": "Zero numeri. 1u su ogni Bonus. Richiede bankroll per resistere 15-20 giri a vuoto.",
        "7. THE CRAZY MAX": "Focus solo su Crazy Time (2u) e Pachinko (1u). Caccia al moltiplicatore folle.",
        "8. TOP SLOT AGGRESSIVE": "Punta 5u su '10' e 2u su Cash Hunt. Mira al boost della Top Slot.",
        "9. THE GAMBLER'S CHOICE": "Punta solo su Coin Flip e Crazy Time. Massima volatilità, massimo rischio.",
        "10. ALL-IN BONUSES": "Puntata pesante (5u ciascuno) solo sui 4 Bonus. Strategia 'Hit or Miss'."
    }
}

# --- UI STYLE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #050505 !important; color: #EEE !important; }
    .stButton>button { background-color: #111 !important; color: #FFF !important; border: 1px solid #333 !important; border-radius: 0px !important; width: 100%; transition: 0.2s; }
    .stButton>button:hover { background-color: #FFF !important; color: #000 !important; }
    .strategy-card { border: 1px solid #222; padding: 15px; background: #0A0A0A; margin-bottom: 10px; border-left: 3px solid #444; }
    .risk-tag { color: #FF4B4B; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; }
    .safe-tag { color: #00FF00; font-weight: bold; font-size: 0.7rem; text-transform: uppercase; }
    .sub-text { color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("EDGE_V25 / MASTER")
bankroll = st.sidebar.number_input("BANKROLL (€)", value=500.0)
mode = st.sidebar.radio("SELECT MODULE", ["SPORTS_BETTING", "CASINO_STRATEGIES"])

# --- MODULO CASINO ---
if mode == "CASINO_STRATEGIES":
    st.title("/ CRAZY_TIME_ENGINE")
    st.markdown("<p class='sub-text'>Algoritmi di ripartizione del rischio basati su RTP 96.08%</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("// SAFE_MODES")
        for name, desc in STRATEGIES["SAFE (Low Risk)"].items():
            st.markdown(f"""
                <div class="strategy-card">
                    <span class="safe-tag">STABLE</span><br>
                    <b style="font-size:1.1rem;">{name}</b><br>
                    <span style="color:#BBB;">{desc}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"CALCOLA STAKE: {name[:5]}"):
                stake = round(bankroll * 0.05, 2)
                st.success(f"Puntata consigliata per giro: €{stake}")

    with col2:
        st.subheader("// RISKY_MODES")
        for name, desc in STRATEGIES["RISKY (High Reward)"].items():
            st.markdown(f"""
                <div class="strategy-card" style="border-left: 3px solid #FF4B4B;">
                    <span class="risk-tag">AGGRESSIVE</span><br>
                    <b style="font-size:1.1rem;">{name}</b><br>
                    <span style="color:#BBB;">{desc}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"CALCOLA STAKE: {name[:5]}", key=name):
                stake = round(bankroll * 0.02, 2)
                st.warning(f"Rischio Elevato. Puntata max: €{stake}")

# --- MODULO SPORTS (IL TUO VECCHIO SCRIPT) ---
else:
    st.title("/ SPORTS_ANALYSIS")
    # ... (Qui va il resto del codice V24 per caricare Safe Elite, Target 100 e Gold Tips)
    st.info("Carica le strategie sportive dalla sidebar o aggiungi le tue Gold Tip.")
    # (Inserire qui la logica delle colonne col_left e col_right della V24)
