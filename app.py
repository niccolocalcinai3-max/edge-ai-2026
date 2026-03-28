import streamlit as st
import requests
import os
from datetime import datetime, timedelta

# --- CONFIGURAZIONE CORE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
SAVE_FILE = "gold_storage.txt"
LEAGUES = {"Serie A": "SA", "Premier League": "PL", "La Liga": "PD", "Bundesliga": "BL1", "Ligue 1": "FL1"}

st.set_page_config(page_title="EDGE PRO ULTIMATE", layout="wide")

# --- FUNZIONI MEMORIA ---
def save_gold(gold_list):
    with open(SAVE_FILE, "w") as f:
        for g in gold_list:
            f.write(f"{g['Match']}|{g['Tip']}|{g['Odds']}\n")

def load_gold():
    lst = []
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    lst.append({"Match": parts[0], "Tip": parts[1], "Odds": float(parts[2])})
    return lst

# --- DATABASE STRATEGIE CASINO ---
STRATEGIES_CASINO = {
    "SAFE (Low Risk)": {
        "1. THE SHIELD (1-2)": "Copertura 70%. Puntata: 4u su '1', 2u su '2'. Stabilità massima.",
        "2. LOW VOLATILITY MIX": "Copre 1, 2 e 5. Puntata: 3u su '1', 2u su '2', 1u su '5'.",
        "3. THE GRINDER": "Punta su '1' e tutti i Bonus (0.5u ciascuno). Protezione attiva.",
        "4. ANTI-VARIANCE": "80% su '2', 20% diviso sui 4 Bonus. Bilanciamento tecnico.",
        "5. CONSERVATIVE BONUS": "Punta su '5' e '10' per finanziare Cash Hunt e Coin Flip."
    },
    "RISKY (High Reward)": {
        "6. BONUS HUNTER PRO": "Solo Bonus (1u ciascuno). Richiede bankroll per 20 giri a vuoto.",
        "7. THE CRAZY MAX": "Focus solo su Crazy Time (2u) e Pachinko (1u). Caccia al Top Slot.",
        "8. TOP SLOT AGGRESSIVE": "5u su '10' e 2u su Cash Hunt. Mira ai moltiplicatori rari.",
        "9. THE GAMBLER'S CHOICE": "Solo Coin Flip e Crazy Time. Volatilità estrema.",
        "10. ALL-IN BONUSES": "Puntata pesante (5u ciascuno) solo sui 4 Bonus Game."
    }
}

# --- UI STYLE (STRICT NOIR) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #050505 !important; color: #EEE !important; }
    .stButton>button { background-color: #111 !important; color: #FFF !important; border: 1px solid #333 !important; border-radius: 0px !important; width: 100%; transition: 0.2s; font-size: 0.8rem; }
    .stButton>button:hover { background-color: #FFF !important; color: #000 !important; }
    .match-card { border: 1px solid #222; padding: 15px; background: #0A0A0A; margin-bottom: 10px; }
    .gold-card { border: 1px solid #FFF; padding: 10px; background: #FFF; color: #000; margin-bottom: 5px; font-weight: bold; font-size: 0.85rem; }
    .strategy-card { border: 1px solid #222; padding: 15px; background: #0A0A0A; margin-bottom: 10px; border-left: 3px solid #444; }
    .sub-text { color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; }
    .risk-tag { color: #FF4B4B; font-weight: bold; font-size: 0.7rem; }
    .safe-tag { color: #00FF00; font-weight: bold; font-size: 0.7rem; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'expert_data' not in st.session_state: st.session_state['expert_data'] = []
if 'gold_list' not in st.session_state: st.session_state['gold_list'] = load_gold()

# --- SIDEBAR MASTER ---
st.sidebar.title("EDGE_MASTER / V25")
bankroll = st.sidebar.number_input("BANKROLL (€)", value=500.0)
module = st.sidebar.radio("SELECT MODULE", ["SPORTS_BETTING", "CASINO_STRATEGIES"])

# --- MODULO 1: SPORTS ---
if module == "SPORTS_BETTING":
    st.sidebar.divider()
    st.sidebar.subheader("1. EXPERT STRATEGIES")
    if st.sidebar.button("LOAD SAFE ELITE"):
        st.session_state['expert_data'] = [
            {"Match": "Juventus v Fiorentina", "Tip": "1X + U3.5", "Odds": 1.50, "Lega": "SERIE A"},
            {"Match": "Liverpool v Everton", "Tip": "Over 2.5", "Odds": 1.62, "Lega": "PREMIER"},
            {"Match": "Real Madrid v Villarreal", "Tip": "Segno 1", "Odds": 1.45, "Lega": "LA LIGA"},
            {"Match": "Leverkusen v Leipzig", "Tip": "Goal", "Odds": 1.55, "Lega": "BUNDESLIGA"}
        ]
        st.session_state['mode_name'] = "SAFE"

    if st.sidebar.button("LOAD TARGET 100"):
        st.session_state['expert_data'] = [
            {"Match": "Bologna v Inter", "Tip": "X", "Odds": 3.60, "Lega": "SERIE A"},
            {"Match": "Newcastle v Man Utd", "Tip": "2 + Goal", "Odds": 4.80, "Lega": "PREMIER"},
            {"Match": "Bilbao v Atl. Madrid", "Tip": "1 + U2.5", "Odds": 4.20, "Lega": "LA LIGA"},
            {"Match": "Dortmund v Stuttgart", "Tip": "O3.5 + Goal", "Odds": 3.20, "Lega": "BUNDESLIGA"},
            {"Match": "Marseille v Nice", "Tip": "X + U2.5", "Odds": 3.50, "Lega": "LIGUE 1"}
        ]
        st.session_state['mode_name'] = "RISK"

    st.sidebar.divider()
    st.sidebar.subheader("2. PERMANENT GOLD")
    g_m = st.sidebar.text_input("MATCH")
    g_t = st.sidebar.text_input("TIP")
    g_o = st.sidebar.number_input("ODDS", value=1.50)
    if st.sidebar.button("ADD GOLD TIP"):
        if g_m and g_t:
            st.session_state['gold_list'].append({"Match": g_m, "Tip": g_t, "Odds": g_o})
            save_gold(st.session_state['gold_list'])
            st.rerun()

    if st.sidebar.button("CLEAR ALL GOLD"):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        st.session_state['gold_list'] = []
        st.rerun()

    # --- MAIN CONTENT SPORTS ---
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.title("/ SPORTS_FEED")
        if st.session_state['gold_list']:
            st.markdown("<p class='sub-text'>Saved Gold Tips</p>", unsafe_allow_html=True)
            for g in st.session_state['gold_list']:
                st.markdown(f"<div class='gold-card'>{g['Match']} // {g['Tip']} // @{g['Odds']}</div>", unsafe_allow_html=True)
            st.divider()

        if st.session_state['expert_data']:
            for m in st.session_state['expert_data']:
                st.markdown(f"<div class='match-card'><small>{m['Lega']}</small><br><b>{m['Match']}</b><br>{m['Tip']} // @{m['Odds']}</div>", unsafe_allow_html=True)
        else: st.info("SYSTEM_IDLE: Select strategy or Gold Tip.")

    with col_right:
        st.subheader("/ TICKET")
        combined = st.session_state['expert_data'] + st.session_state['gold_list']
        if combined:
            total_odds = 1.0
            txt = ""
            for m in combined:
                total_odds *= m['Odds']
                txt += f"| {m['Match']} -> {m['Tip']} (@{m['Odds']})\n"
            
            stake_pct = 0.08 if st.session_state.get('mode_name') == "SAFE" else 0.02
            stake = round(bankroll * stake_pct, 2)
            
            st.markdown(f"""<div style="border-top:1px solid #333; padding-top:10px;">
                <p class='sub-text'>Odds</p><h2>{total_odds:.2f}</h2>
                <p class='sub-text'>Stake</p><h3>€{stake}</h3>
                <p class='sub-text'>Return</p><h2 style="color:#FFF;">€{round(total_odds * stake, 2)}</h2>
            </div>""", unsafe_allow_html=True)
            st.text_area("COPY", value=txt, height=150)
        else: st.write("EMPTY")

# --- MODULO 2: CASINO ---
else:
    st.title("/ CASINO_STRATEGIES")
    st.markdown("<p class='sub-text'>Crazy Time Mathematical Engines</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("// SAFE_MODES")
        for name, desc in STRATEGIES_CASINO["SAFE (Low Risk)"].items():
            st.markdown(f"""<div class="strategy-card"><span class="safe-tag">STABLE</span><br><b>{name}</b><br><small>{desc}</small></div>""", unsafe_allow_html=True)
            if st.button(f"CALC: {name[:8]}", key=name):
                st.success(f"Stake consigliato: €{round(bankroll * 0.05, 2)}")
                
    with c2:
        st.subheader("// RISKY_MODES")
        for name, desc in STRATEGIES_CASINO["RISKY (High Reward)"].items():
            st.markdown(f"""<div class="strategy-card" style="border-left:3px solid #FF4B4B;"><span class="risk-tag">AGGRESSIVE</span><br><b>{name}</b><br><small>{desc}</small></div>""", unsafe_allow_html=True)
            if st.button(f"CALC: {name[:8]}", key=name):
                st.warning(f"Stake consigliato: €{round(bankroll * 0.02, 2)}")
