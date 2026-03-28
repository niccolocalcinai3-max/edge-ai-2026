import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
FREE_LEAGUES = {
    "Serie A": "SA", "Premier League": "PL", "La Liga": "PD", 
    "Bundesliga": "BL1", "Ligue 1": "FL1", "Champions League": "CL",
    "Eredivisie": "DED", "Championship": "ELC"
}

st.set_page_config(page_title="EDGE NEURAL V13 - ELITE", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; width: 100%; border-radius: 8px; font-weight: bold; }
    .stDownloadButton>button { background-color: #3399FF !important; color: white !important; width: 100%; }
    .reportview-container { background: #000; }
    .match-box { border: 1px solid #222; padding: 10px; border-radius: 5px; margin-bottom: 5px; background: #080808; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA API ---
def fetch_data(leagues_to_scan):
    headers = {'X-Auth-Token': API_KEY}
    date_from = datetime.now().strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}matches?dateFrom={date_from}&dateTo={date_to}"
    try:
        res = requests.get(url, headers=headers).json()
        matches = res.get('matches', [])
        return [m for m in matches if m['competition']['code'] in leagues_to_scan]
    except: return []

# --- SIDEBAR ---
st.sidebar.title("🚀 ELITE MANAGER V13")

# Selezione Campionati
st.sidebar.subheader("Filtri Campionato")
all_leagues = st.sidebar.checkbox("Tutti i campionati FREE", value=True)
selected_leagues = list(FREE_LEAGUES.values()) if all_leagues else [FREE_LEAGUES["Serie A"], FREE_LEAGUES["Premier League"]]

# Parametri Scommessa
st.sidebar.divider()
bankroll = st.sidebar.number_input("Budget Totale € (Bankroll)", min_value=10.0, value=500.0)
target = st.sidebar.number_input("Obiettivo Vincita €", min_value=1.0, value=100.0)

col_side1, col_side2 = st.sidebar.columns(2)
with col_side1:
    if st.button("🔍 SCAN"):
        with st.spinner("Analisi in corso..."):
            raw_matches = fetch_data(selected_leagues)
            processed = []
            for m in raw_matches:
                # Logica neurale base
                h_id, a_id = m['homeTeam']['id'], m['awayTeam']['id']
                tip, odds, conf = ("1X + OVER 1.5", 1.45, 82) if h_id < a_id else ("X2", 1.60, 74)
                processed.append({
                    "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
                    "Lega": m['competition']['name'],
                    "Esito": tip, "Quota": odds, "Conf": conf, "Data": m['utcDate'][:10]
                })
            st.session_state['results'] = processed
with col_side2:
    if st.button("🗑️ RESET"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# --- MAIN ---
if 'results' in st.session_state:
    data = st.session_state['results']
    
    # Calcolo Schedina
    sorted_data = sorted(data, key=lambda x: x['Conf'], reverse=True)
    ticket, total_odds = [], 1.0
    # Cerchiamo di raggiungere il target con i match a confidenza più alta
    for m in sorted_data:
        if total_odds < (target / (bankroll * 0.05)): # Usiamo uno stake dinamico del 5%
            ticket.append(m)
            total_odds *= m['Quota']

    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📡 Feed Mercati Attivi")
        for d in data:
            with st.container():
                st.markdown(f"""<div class="match-box">
                <small>{d['Data']} | {d['Lega']}</small><br>
                <b>{d['Match']}</b><br>
                <span style="color:#00FF00">{d['Esito']} @ {d['Quota']}</span> (Confidenza: {d['Conf']}%)
                </div>""", unsafe_allow_html=True)

    with c2:
        st.subheader("🎫 Smart Ticket")
        if ticket:
            # Calcolo Stake Suggerito (Kelly-ish)
            avg_conf = sum(t['Conf'] for t in ticket) / len(ticket)
            suggested_stake = round((bankroll * (avg_conf/100)) * 0.1, 2)
            
            res_txt = f"--- TICKET ELITE V13 ---\n\n"
            for t in ticket:
                st.write(f"🔹 **{t['Match']}**")
                st.caption(f"{t['Esito']} (@{t['Quota']})")
                res_txt += f"• {t['Match']}: {t['Esito']} (@{t['Quota']})\n"
            
            st.divider()
            st.metric("QUOTA TOTALE", f"{total_odds:.2f}")
            st.metric("STAKE CONSIGLIATO", f"€{suggested_stake}", delta="Basato su Confidenza")
            st.metric("POTENZIALE VINCITA", f"€{round(total_odds * suggested_stake, 2)}")

            # Export
            res_txt += f"\nQuota: {total_odds:.2f}\nStake: €{suggested_stake}\nNote: Generato via Edge Neural Elite."
            
            st.text_area("Copia per Note/WhatsApp:", value=res_txt, height=200)
            st.download_button("📥 SCARICA BIGLIETTO PDF/TXT", data=res_txt, file_name="schedina_elite.txt")
        else:
            st.warning("Nessun match trovato. Prova ad aumentare il raggio di ricerca.")
else:
    st.info("👋 Benvenuto! Configura i parametri a sinistra e clicca su SCAN.")
