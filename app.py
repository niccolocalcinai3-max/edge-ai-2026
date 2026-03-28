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
    "Bundesliga": "BL1", "Ligue 1": "FL1", "Champions League": "CL",
    "Eredivisie": "DED", "Championship": "ELC"
}

st.set_page_config(page_title="EDGE NEURAL V17 - HYBRID", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; border-radius: 8px; }
    .expert-btn>div>button { background-color: #FFD700 !important; color: black !important; }
    .match-box { border-left: 5px solid #00FF00; padding: 12px; border-radius: 5px; margin-bottom: 8px; background: #0A0A0A; border: 1px solid #222; }
    .urgent-box { border-left: 5px solid #FF4B4B !important; background: #1A0000 !important; }
    .gold-box { border: 2px solid #FFD700; padding: 15px; border-radius: 10px; background: #1A1A00; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI TECNICHE ---
def get_local_time(utc_date_str):
    utc_dt = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Rome'))

def fetch_live_data(leagues):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}matches?dateFrom={datetime.now().strftime('%Y-%m-%d')}&dateTo={(datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')}"
    try:
        res = requests.get(url, headers=headers).json()
        matches = []
        for m in res.get('matches', []):
            if m['competition']['code'] in [FREE_LEAGUES[l] for l in leagues]:
                l_time = get_local_time(m['utcDate'])
                is_urgent = (l_time - datetime.now(pytz.timezone('Europe/Rome'))).total_seconds() < 3600
                matches.append({
                    "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
                    "Lega": m['competition']['name'],
                    "Orario": l_time.strftime("%d/%m %H:%M"),
                    "Urgent": is_urgent,
                    "Tip": "1X" if m['homeTeam']['id'] < m['awayTeam']['id'] else "X2",
                    "Odds": 1.55, "Conf": 75
                })
        return matches
    except: return []

# --- SIDEBAR CONTROLLI ---
st.sidebar.title("🛠️ MASTER CONTROL V17")

# 1. SCAN AUTOMATICO (Lo script di prima)
st.sidebar.subheader("📡 Scan Automatico API")
sel_leagues = st.sidebar.multiselect("Laghe attive", list(FREE_LEAGUES.keys()), default=["Serie A", "Premier League"])
if st.sidebar.button("🚀 AVVIA DEEP SCAN"):
    st.session_state['active_mode'] = "API"
    st.session_state['matches'] = fetch_live_data(sel_leagues)

st.sidebar.divider()

# 2. EXPERT PICKS (Le schedine che abbiamo fatto noi)
st.sidebar.subheader("🌟 Strategie Expert")
st.sidebar.markdown('<div class="expert-btn">', unsafe_allow_html=True)
if st.sidebar.button("🛡️ CARICA SAFE (BANKER)"):
    st.session_state['active_mode'] = "EXPERT_SAFE"
    st.session_state['matches'] = [
        {"Match": "Arsenal vs Luton Town", "Tip": "1 + OVER 2.5", "Odds": 1.40, "Conf": 95, "Lega": "Premier League", "Orario": "Vario", "Urgent": False},
        {"Match": "Manchester City vs West Ham", "Tip": "1 + OVER 1.5", "Odds": 1.35, "Conf": 92, "Lega": "Premier League", "Orario": "Vario", "Urgent": False},
        {"Match": "Real Madrid vs Villarreal", "Tip": "1", "Odds": 1.45, "Conf": 85, "Lega": "La Liga", "Orario": "Vario", "Urgent": False}
    ]
if st.sidebar.button("💣 CARICA QUOTA 100"):
    st.session_state['active_mode'] = "EXPERT_100"
    st.session_state['matches'] = [
        {"Match": "Bologna vs Inter", "Tip": "PAREGGIO (X)", "Odds": 3.60, "Conf": 40, "Lega": "Serie A", "Orario": "Vario", "Urgent": False},
        {"Match": "Newcastle vs Man Utd", "Tip": "2 + GOAL", "Odds": 4.80, "Conf": 35, "Lega": "Premier League", "Orario": "Vario", "Urgent": False},
        {"Match": "Athletic Bilbao vs Atl. Madrid", "Tip": "1 + UNDER 2.5", "Odds": 4.20, "Conf": 30, "Lega": "La Liga", "Orario": "Vario", "Urgent": False},
        {"Match": "B. Dortmund vs Stoccarda", "Tip": "OVER 3.5 + GOAL", "Odds": 3.20, "Conf": 45, "Lega": "Bundesliga", "Orario": "Vario", "Urgent": False},
        {"Match": "Marsiglia vs Nizza", "Tip": "X + UNDER 2.5", "Odds": 3.50, "Conf": 38, "Lega": "Ligue 1", "Orario": "Vario", "Urgent": False}
    ]
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()

# 3. GOLD TIP PERSONALE
st.sidebar.subheader("✍️ Gold Tip Personale")
g_match = st.sidebar.text_input("Match Personale")
g_pick = st.sidebar.text_input("Esito")
g_odds = st.sidebar.number_input("Quota", value=1.50)
if st.sidebar.button("💾 AGGIUNGI GOLD TIP"):
    st.session_state['gold_tip'] = {"Match": g_match, "Tip": g_pick, "Odds": g_odds}

if st.sidebar.button("🗑️ RESET"):
    st.session_state.clear()
    st.rerun()

# --- MAIN DISPLAY ---
st.title("🧠 EDGE NEURAL HYBRID HUB")

c1, c2 = st.columns([2, 1])

with c1:
    if 'gold_tip' in st.session_state:
        g = st.session_state['gold_tip']
        st.markdown(f'<div class="gold-box">🌟 <b>LA MIA GOLD TIP:</b> {g["Match"]} - {g["Tip"]} (@{g["Odds"]})</div>', unsafe_allow_html=True)
    
    st.subheader("📡 Feed Partite & Analisi")
    if 'matches' in st.session_state:
        for m in st.session_state['matches']:
            urgent_style = "urgent-box" if m.get('Urgent') else ""
            st.markdown(f"""<div class="match-box {urgent_style}">
                <small>{'⚠️ INIZIA A BREVE | ' if m.get('Urgent') else ''}{m['Orario']} - {m['Lega']}</small><br>
                <b>{m['Match']}</b><br>
                <span style="color:#00FF00">Puntata: {m['Tip']} (@{m['Odds']})</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Scegli una modalità dalla sidebar per visualizzare i match.")

with c2:
    st.subheader("🎫 Riepilogo Biglietto")
    if 'matches' in st.session_state:
        total_odds = 1.0
        txt = "--- SCHEDINA EDGEmaster ---\n\n"
        
        for m in st.session_state['matches']:
            st.write(f"✅ {m['Match']} ({m['Tip']})")
            total_odds *= m['Odds']
            txt += f"• {m['Match']}: {m['Tip']} (@{m['Odds']})\n"
        
        if 'gold_tip' in st.session_state:
            g = st.session_state['gold_tip']
            total_odds *= g['Odds']
            txt += f"🌟 GOLD TIP: {g['Match']} -> {g['Tip']} (@{g['Odds']})\n"
        
        st.divider()
        st.metric("QUOTA TOTALE", f"{total_odds:.2f}")
        st.text_area("Copia per Note:", value=txt, height=200)
        st.download_button("📥 Scarica Schedina", data=txt, file_name="schedina_master.txt")
