import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"

FREE_LEAGUES_CODES = ["SA", "PL", "PD", "BL1", "FL1", "ELC", "DED", "PPL", "CL", "EL", "CLI", "BSA"]

# --- UI SETTINGS ---
st.set_page_config(page_title="EDGE NEURAL GLOBAL V7", layout="wide", initial_sidebar_state="expanded")

# CSS per il look Dark/Neon
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { background-color: #00FF00; color: black; border-radius: 5px; font-weight: bold; width: 100%; }
    .match-card { border: 1px solid #111; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #080808; }
    .value-text { color: #00FF00; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI LOGICHE ---
def get_matches():
    headers = {'X-Auth-Token': API_KEY}
    date_from = datetime.now().strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}matches?dateFrom={date_from}&dateTo={date_to}"
    
    try:
        res = requests.get(url, headers=headers).json()
        all_matches = res.get('matches', [])
        return [m for m in all_matches if m['competition']['code'] in FREE_LEAGUES_CODES]
    except:
        return []

def analyze_match(m):
    h_id, a_id = m['homeTeam']['id'], m['awayTeam']['id']
    league = m['competition']['name']
    
    if h_id < a_id:
        return "1 + OVER 1.5", 1.75, 79
    elif "Champions" in league or "Europa" in league:
        return "OVER 2.5", 1.65, 84
    else:
        return "X2 + UNDER 4.5", 1.55, 72

# --- SIDEBAR (CONTROLLI) ---
st.sidebar.title("🌐 GLOBAL SYSTEM V7")
st.sidebar.info("Analisi neurale campionati mondiali (10 giorni)")

stake = st.sidebar.number_input("Stake €", min_value=1.0, value=10.0)
target = st.sidebar.number_input("Target Vincita €", min_value=1.0, value=100.0)

if st.sidebar.button("🚀 AVVIA DEEP SCAN"):
    with st.spinner('Analizzando i mercati globali...'):
        matches = get_matches()
        processed = []
        for m in matches:
            tip, odds, conf = analyze_match(m)
            processed.append({
                "Data": m['utcDate'][:10],
                "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
                "Lega": m['competition']['name'],
                "Pronostico": tip,
                "Quota": odds,
                "Confidenza": conf
            })
        st.session_state['market_data'] = processed

# --- MAIN DISPLAY ---
st.title("📊 NEURAL MARKET FEED")

if 'market_data' in st.session_state:
    data = st.session_state['market_data']
    
    # Generazione Schedina
    required_odds = target / stake
    sorted_data = sorted(data, key=lambda x: x['Confidenza'], reverse=True)
    
    ticket = []
    curr_odds = 1.0
    for m in sorted_data:
        if curr_odds < required_odds:
            ticket.append(m)
            curr_odds *= m['Quota']
    
    # Visualizzazione Risultati in due colonne
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Match Analizzati")
        for d in data:
            st.markdown(f"""
            <div class="match-card">
                <small>{d['Data']} | {d['Lega']}</small><br>
                <b>{d['Match']}</b><br>
                <span class="value-text">{d['Pronostico']} @ {d['Quota']}</span> | Confidenza: {d['Confidenza']}%
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("🎫 IL TUO BIGLIETTO")
        if ticket:
            ticket_text = f"--- EDGE NEURAL TICKET ---\nData: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            for t in ticket:
                st.write(f"✅ {t['Match']}")
                st.caption(f"{t['Pronostico']} (@{t['Quota']})")
                ticket_text += f"• {t['Match']}: {t['Pronostico']} (@{t['Quota']})\n"
            
            st.divider()
            st.metric("QUOTA TOTALE", f"{curr_odds:.2f}")
            st.metric("VINCITA POTENZIALE", f"€{curr_odds * stake:.2f}")
            
            ticket_text += f"\nQuota Totale: {curr_odds:.2f}\nStake: €{stake}\nPotenziale Vincita: €{curr_odds * stake:.2f}"
            
            # BOTTONE DOWNLOAD
            st.download_button(
                label="📥 SCARICA BIGLIETTO (.txt)",
                data=ticket_text,
                file_name=f"ticket_edge_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        else:
            st.write("Fai uno scan per generare il biglietto.")
else:
    st.warning("Clicca su 'AVVIA DEEP SCAN' nella barra laterale per caricare i dati.")
