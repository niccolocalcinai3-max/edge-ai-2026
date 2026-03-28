import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- CORE SETTINGS ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
LEAGUES = {"Serie A": "SA", "Premier League": "PL", "La Liga": "PD", "Bundesliga": "BL1", "Ligue 1": "FL1"}

st.set_page_config(page_title="EDGE PRO", layout="wide")

# --- CLEAN NOIR UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #050505 !important;
        color: #EEEEEE !important;
    }

    /* Minimalist Buttons */
    .stButton>button {
        background-color: #111 !important;
        color: #FFF !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        padding: 10px 20px !important;
        width: 100%;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #FFF !important;
        color: #000 !important;
        border-color: #FFF !important;
    }

    /* Match Cards */
    .match-card {
        border: 1px solid #222;
        padding: 20px;
        background: #0A0A0A;
        margin-bottom: 12px;
    }
    
    .gold-header {
        border: 1px solid #FFF;
        background: #FFF;
        color: #000;
        padding: 15px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }

    /* Subtitle styling */
    .sub-text { color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Metrics box */
    .summary-box {
        border-top: 2px solid #FFF;
        padding-top: 20px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- API LOGIC ---
def run_api_scan(selected_codes):
    headers = {'X-Auth-Token': API_KEY}
    # Scanning next 7 days
    url = f"{BASE_URL}matches?dateTo={(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}"
    try:
        response = requests.get(url, headers=headers).json()
        matches = response.get('matches', [])
        found = []
        for m in matches:
            if m['competition']['code'] in selected_codes:
                found.append({
                    "Match": f"{m['homeTeam']['shortName']} v {m['awayTeam']['shortName']}",
                    "Lega": m['competition']['name'],
                    "Tip": "1X" if m['homeTeam']['id'] < m['awayTeam']['id'] else "X2",
                    "Odds": 1.55
                })
        return found
    except Exception as e:
        st.error(f"API Error: Check Connection")
        return []

# --- SIDEBAR ---
st.sidebar.title("EDGE_SYSTEM_V21")
st.sidebar.markdown("---")

bankroll = st.sidebar.number_input("BANKROLL (€)", value=500.0)

st.sidebar.subheader("1. EXPERT STRATEGIES")
if st.sidebar.button("LOAD SAFE ELITE"):
    st.session_state['data'] = [
        {"Match": "Juventus v Fiorentina", "Tip": "1X + U3.5", "Odds": 1.50, "Lega": "SERIE A"},
        {"Match": "Liverpool v Everton", "Tip": "Over 2.5", "Odds": 1.62, "Lega": "PREMIER"},
        {"Match": "Real Madrid v Villarreal", "Tip": "Segno 1", "Odds": 1.45, "Lega": "LA LIGA"},
        {"Match": "Leverkusen v Leipzig", "Tip": "Goal", "Odds": 1.55, "Lega": "BUNDESLIGA"}
    ]
    st.session_state['mode_name'] = "SAFE ELITE"

if st.sidebar.button("LOAD QUOTA 100"):
    st.session_state['data'] = [
        {"Match": "Bologna v Inter", "Tip": "X", "Odds": 3.60, "Lega": "SERIE A"},
        {"Match": "Newcastle v Man Utd", "Tip": "2 + Goal", "Odds": 4.80, "Lega": "PREMIER"},
        {"Match": "Bilbao v Atl. Madrid", "Tip": "1 + U2.5", "Odds": 4.20, "Lega": "LA LIGA"},
        {"Match": "Dortmund v Stuttgart", "Tip": "O3.5 + Goal", "Odds": 3.20, "Lega": "BUNDESLIGA"},
        {"Match": "Marseille v Nice", "Tip": "X + U2.5", "Odds": 3.50, "Lega": "LIGUE 1"}
    ]
    st.session_state['mode_name'] = "TARGET 100"

st.sidebar.divider()
st.sidebar.subheader("2. LIVE MARKET SCAN")
sel_leagues = st.sidebar.multiselect("Select Leagues", list(LEAGUES.keys()), default=["Serie A"])
if st.sidebar.button("RUN LIVE SCAN"):
    codes = [LEAGUES[l] for l in sel_leagues]
    with st.spinner("Accessing API..."):
        st.session_state['data'] = run_api_scan(codes)
        st.session_state['mode_name'] = "LIVE SCAN"

st.sidebar.divider()
if st.sidebar.button("RESET SYSTEM"):
    st.session_state.clear()
    st.rerun()

# --- MAIN CONTENT ---
col_main, col_ticket = st.columns([2, 1])

with col_main:
    st.title("ANALYSIS_FEED")
    
    if 'data' in st.session_state and st.session_state['data']:
        st.markdown(f"<p class='sub-text'>Mode: {st.session_state.get('mode_name', 'None')}</p>", unsafe_allow_html=True)
        for m in st.session_state['data']:
            st.markdown(f"""
                <div class="match-card">
                    <span class="sub-text">{m['Lega']}</span><br>
                    <b style="font-size:1.2rem;">{m['Match']}</b><br>
                    <span style="color:#FFF;">{m['Tip']}</span> // <span style="color:#888;">@{m['Odds']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Select a strategy or run a scan to begin.")

with col_ticket:
    st.subheader("YOUR_TICKET")
    
    if 'data' in st.session_state and st.session_state['data']:
        total_odds = 1.0
        ticket_txt = "--- EDGE PRO TICKET ---\n\n"
        
        for m in st.session_state['data']:
            total_odds *= m['Odds']
            ticket_txt += f"| {m['Match']} -> {m['Tip']} (@{m['Odds']})\n"
        
        # Risk Management Logic
        mode = st.session_state.get('mode_name', '')
        stake_pct = 0.08 if "SAFE" in mode else 0.02
        stake = round(bankroll * stake_pct, 2)
        win = round(total_odds * stake, 2)
        
        st.markdown(f"""
            <div class="summary-box">
                <p class="sub-text">Total Odds</p>
                <h2 style="margin:0;">{total_odds:.2f}</h2>
                <br>
                <p class="sub-text">Suggested Stake</p>
                <h3 style="margin:0;">€{stake}</h3>
                <br>
                <p class="sub-text">Est. Return</p>
                <h2 style="margin:0; color:#FFF;">€{win}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.download_button("DOWNLOAD TICKET", data=ticket_txt, file_name="edge_ticket.txt")
        st.text_area("COPY FOR NOTES", value=ticket_txt, height=150)
    else:
        st.write("Ticket is empty.")
