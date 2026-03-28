import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
FREE_LEAGUES = {
    "Serie A": "SA", "Premier League": "PL", "La Liga": "PD", 
    "Bundesliga": "BL1", "Ligue 1": "FL1", "Champions League": "CL"
}

st.set_page_config(page_title="EDGE NEURAL V18 - DEFINITIVE", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; border-radius: 8px; height: 45px; }
    .expert-btn>div>button { background-color: #FFD700 !important; color: black !important; border: 2px solid #B8860B; }
    .match-box { border-left: 5px solid #00FF00; padding: 12px; border-radius: 5px; margin-bottom: 8px; background: #0A0A0A; border: 1px solid #222; }
    .urgent-box { border-left: 5px solid #FF4B4B !important; background: #1A0000 !important; }
    .gold-box { border: 2px solid #FFD700; padding: 15px; border-radius: 10px; background: #1A1A00; margin-bottom: 20px; }
    .metric-box { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI ---
def get_local_time(utc_date_str):
    utc_dt = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Rome'))

# --- SIDEBAR ---
st.sidebar.title("🛠️ MASTER CONTROL V18")
bankroll = st.sidebar.number_input("Budget Totale (Bankroll) €", min_value=10.0, value=200.0)

# 1. STRATEGIE EXPERT (LE TUE SCHEDINE PREFERITE)
st.sidebar.subheader("🌟 Strategie Analista Senior")
st.sidebar.markdown('<div class="expert-btn">', unsafe_allow_html=True)

if st.sidebar.button("🛡️ CARICA SAFE (NEURAL ELITE)"):
    st.session_state['mode'] = "SAFE"
    st.session_state['matches'] = [
        {"Match": "Juventus vs Fiorentina", "Tip": "1X + Under 3.5", "Odds": 1.50, "Lega": "Serie A", "Conf": 88},
        {"Match": "Liverpool vs Everton", "Tip": "Over 2.5 Gol", "Odds": 1.62, "Lega": "Premier League", "Conf": 85},
        {"Match": "Real Madrid vs Villarreal", "Tip": "Segno 1", "Odds": 1.45, "Lega": "La Liga", "Conf": 90},
        {"Match": "Bayer Leverkusen vs RB Leipzig", "Tip": "Goal (G/G)", "Odds": 1.55, "Lega": "Bundesliga", "Conf": 82}
    ]

if st.sidebar.button("💣 CARICA TARGET 100"):
    st.session_state['mode'] = "QUOTA_100"
    st.session_state['matches'] = [
        {"Match": "Bologna vs Inter", "Tip": "Pareggio (X)", "Odds": 3.60, "Lega": "Serie A", "Conf": 40},
        {"Match": "Newcastle vs Man Utd", "Tip": "2 + Goal", "Odds": 4.80, "Lega": "Premier League", "Conf": 35},
        {"Match": "Athletic Bilbao vs Atl. Madrid", "Tip": "1 + Under 2.5", "Odds": 4.20, "Lega": "La Liga", "Conf": 30},
        {"Match": "B. Dortmund vs Stoccarda", "Tip": "Over 3.5 + Goal", "Odds": 3.20, "Conf": 45, "Lega": "Bundesliga"},
        {"Match": "Marsiglia vs Nizza", "Tip": "X + Under 2.5", "Odds": 3.50, "Conf": 38, "Lega": "Ligue 1"}
    ]
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()

# 2. SCAN API (QUELLO DI PRIMA)
st.sidebar.subheader("📡 Scan Live API")
sel_leagues = st.sidebar.multiselect("Campionati", list(FREE_LEAGUES.keys()), default=["Serie A", "Premier League"])
if st.sidebar.button("🚀 AVVIA DEEP SCAN"):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}matches?dateFrom={datetime.now().strftime('%Y-%m-%d')}&dateTo={(datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')}"
    res = requests.get(url, headers=headers).json()
    st.session_state['matches'] = []
    for m in res.get('matches', []):
        if m['competition']['code'] in [FREE_LEAGUES[l] for l in sel_leagues]:
            st.session_state['matches'].append({
                "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
                "Lega": m['competition']['name'],
                "Orario": get_local_time(m['utcDate']).strftime("%d/%m %H:%M"),
                "Tip": "1X" if m['homeTeam']['id'] < m['awayTeam']['id'] else "X2",
                "Odds": 1.55
            })

# 3. GOLD TIP
st.sidebar.subheader("✍️ Aggiungi Gold Tip")
g_match = st.sidebar.text_input("Partita Personale")
g_tip = st.sidebar.text_input("Esito")
g_odds = st.sidebar.number_input("Quota", value=1.50)
if st.sidebar.button("💾 SALVA GOLD TIP"):
    st.session_state['gold_tip'] = {"Match": g_match, "Tip": g_tip, "Odds": g_odds}

if st.sidebar.button("🗑️ RESET"):
    st.session_state.clear()
    st.rerun()

# --- MAIN ---
st.title("🧠 EDGE NEURAL V18 - HYBRID CENTER")

c1, c2 = st.columns([2, 1])

with c1:
    if 'gold_tip' in st.session_state:
        g = st.session_state['gold_tip']
        st.markdown(f'<div class="gold-box">🌟 <b>LA MIA GOLD TIP:</b> {g["Match"]} - {g["Tip"]} (@{g["Odds"]})</div>', unsafe_allow_html=True)
    
    st.subheader("📡 Analisi Partite Caricate")
    if 'matches' in st.session_state:
        for m in st.session_state['matches']:
            st.markdown(f"""<div class="match-box">
                <small>{m.get('Orario', 'Analisi Esperta')} - {m['Lega']}</small><br>
                <b>{m['Match']}</b><br>
                <span style="color:#00FF00">Suggerimento: {m['Tip']} (@{m['Odds']})</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Utilizza la sidebar per caricare una schedina o fare uno scan.")

with c2:
    st.subheader("🎫 Calcolo Vincite")
    if 'matches' in st.session_state:
        t_odds = 1.0
        txt = f"--- SCHEDINA {st.session_state.get('mode', 'CUSTOM')} ---\n\n"
        
        for m in st.session_state['matches']:
            t_odds *= m['Odds']
            txt += f"• {m['Match']}: {m['Tip']} (@{m['Odds']})\n"
        
        if 'gold_tip' in st.session_state:
            t_odds *= st.session_state['gold_tip']['Odds']
            txt += f"🌟 GOLD TIP: {st.session_state['gold_tip']['Match']} (@{st.session_state['gold_tip']['Odds']})\n"

        # Calcolo Stake dinamico basato sul rischio
        risk_factor = 0.08 if st.session_state.get('mode') == "SAFE" else 0.02
        s_stake = round(bankroll * risk_factor, 2)
        
        st.markdown(f"""<div class="metric-box">
            <h4 style='margin:0'>QUOTA TOTALE: {t_odds:.2f}</h4><br>
            STAKE CONSIGLIATO: €{s_stake}<br>
            <h3 style='color:#00FF00'>VINCITA: €{round(t_odds * s_stake, 2)}</h3>
        </div>""", unsafe_allow_html=True)
        
        st.text_area("Copia per Note:", value=txt + f"\nQuota: {t_odds:.2f}\nStake: €{s_stake}", height=200)
        st.download_button("📥 Scarica .txt", data=txt, file_name="schedina_edge.txt")
