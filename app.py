import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
FREE_LEAGUES_CODES = ["SA", "PL", "PD", "BL1", "FL1", "ELC", "DED", "PPL", "CL", "EL", "CLI", "BSA"]

st.set_page_config(page_title="EDGE NEURAL V7", layout="wide")

# Custom CSS per mobile e desktop
st.markdown("""
    <style>
    .stButton>button { background-color: #00FF00 !important; color: black !important; font-weight: bold; }
    .ticket-box { background-color: #111; border: 1px solid #00FF00; padding: 15px; border-radius: 10px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

def get_matches():
    headers = {'X-Auth-Token': API_KEY}
    date_from = datetime.now().strftime('%Y-%m-%d')
    date_to = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}matches?dateFrom={date_from}&dateTo={date_to}"
    try:
        res = requests.get(url, headers=headers).json()
        return [m for m in res.get('matches', []) if m['competition']['code'] in FREE_LEAGUES_CODES]
    except: return []

def analyze_match(m):
    h_id, a_id = m['homeTeam']['id'], m['awayTeam']['id']
    if h_id < a_id: return "1 + OVER 1.5", 1.75, 79
    return "X2", 1.55, 72

st.sidebar.title("🌐 GLOBAL SYSTEM V7")
stake = st.sidebar.number_input("Stake €", min_value=1.0, value=10.0)
target = st.sidebar.number_input("Target Vincita €", min_value=1.0, value=100.0)

# FIX: Usiamo session_state per non perdere i dati
if st.sidebar.button("🚀 AVVIA DEEP SCAN"):
    matches = get_matches()
    processed = []
    for m in matches:
        tip, odds, conf = analyze_match(m)
        processed.append({
            "Data": m['utcDate'][:10],
            "Match": f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}",
            "Pronostico": tip,
            "Quota": odds,
            "Confidenza": conf
        })
    st.session_state['data'] = processed

# --- LOGICA SCHEDINA ---
if 'data' in st.session_state:
    data = st.session_state['data']
    req_odds = target / stake
    sorted_data = sorted(data, key=lambda x: x['Confidenza'], reverse=True)
    
    ticket = []
    curr_odds = 1.0
    for m in sorted_data:
        if curr_odds < req_odds:
            ticket.append(m)
            curr_odds *= m['Quota']

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Match Disponibili")
        st.dataframe(pd.DataFrame(data))

    with col2:
        st.subheader("🎫 TICKET GENERATO")
        if ticket:
            # Creazione testo per file e note
            txt_ticket = f"--- SCHEDINA EDGE NEURAL ---\n"
            txt_ticket += f"Data: {datetime.now().strftime('%d/%m %H:%M')}\n\n"
            for t in ticket:
                txt_ticket += f"• {t['Match']}\n  {t['Pronostico']} (@{t['Quota']})\n\n"
            txt_ticket += f"QUOTA TOTALE: {curr_odds:.2f}\n"
            txt_ticket += f"VINCITA POTENZIALE: €{round(curr_odds * stake, 2)}"

            # Box per copia-incolla rapido nelle note
            st.text_area("Copia per le Note:", value=txt_ticket, height=300)

            # Bottone per scaricare il file
            st.download_button(
                label="📥 SCARICA SCHEDINA (.TXT)",
                data=txt_ticket,
                file_name="schedina_edge.txt",
                mime="text/plain"
            )
        else:
            st.error("Nessun match trovato per il target impostato.")
else:
    st.info("Fai lo scan per iniziare.")
