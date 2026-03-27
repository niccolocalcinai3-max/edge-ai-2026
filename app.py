import streamlit as st
import requests
import random
import hashlib
from datetime import datetime

# --- CONFIGURATION & LEAGUE DATA ---
st.set_page_config(page_title="EDGE AI | LUXURY 2026", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"

# League Mapping (Same as your Desktop Version)
LEAGUES = {
    "All Global Markets": 0,
    "International (Nationals)": 1,
    "Premier League (UK)": 39,
    "Serie A (Italy)": 135,
    "La Liga (Spain)": 140,
    "Bundesliga (Germany)": 78
}

# --- AUTHENTICATION (Simplified for this update) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("E D G E  A I  /  L O G I N")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Access Luxury Engine"):
        if u == "admin" and p == "edge2026": # Default credentials
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- SIDEBAR: LEAGUE & MATCH FILTERS ---
st.sidebar.title("🎯 CONTROL PANEL")
st.sidebar.markdown("---")

# 1. Choose League
selected_league_name = st.sidebar.selectbox("SELECT TARGET LEAGUE", list(LEAGUES.keys()))
league_id = LEAGUES[selected_league_name]

# 2. Analysis Depth (How many matches to pull)
match_limit = st.sidebar.slider("ANALYSIS DEPTH (Matches)", 10, 100, 50)

# 3. Strategy & Math
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
risk = st.sidebar.select_slider("RISK MODE", options=["SAFE", "BALANCED", "AGGRESSIVE"], value="BALANCED")

st.sidebar.markdown("---")
gen_btn = st.sidebar.button("RUN AI ANALYSIS")

# --- MAIN DISPLAY ---
st.header(f"Intelligence Feed: {selected_league_name}")

if gen_btn:
    with st.spinner(f"Analyzing {selected_league_name}..."):
        # API URL Construction with League Filter
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        if league_id != 0:
            url += f"&league={league_id}&season=2026"
            
        try:
            res = requests.get(url, headers={'x-apisports-key': API_KEY}).json().get('response', [])
            
            # Filter and store matches
            all_matches = []
            for m in res[:match_limit]:
                all_matches.append({
                    "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                    "quote": round(random.uniform(1.3, 3.5), 2), # In real use, pull real odds here
                    "conf": random.randint(70, 99),
                    "status": m['fixture']['status']['short']
                })

            if not all_matches:
                st.warning(f"No live or upcoming matches found for {selected_league_name} today.")
            else:
                # Calculation Logic
                req_odds = target / stake
                random.shuffle(all_matches)
                ticket = []
                current_odds = 1.0
                
                for m in sorted(all_matches, key=lambda x: x['conf'], reverse=True):
                    if current_odds < req_odds:
                        ticket.append(m)
                        current_odds *= m['quote']
                    else: break

                # UI Display
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Analyzed Markets")
                    for m in all_matches[:10]: # Show top 10 analyzed
                        st.write(f"🔍 {m['teams']} | Confidence: {m['conf']}%")

                with col2:
                    st.subheader("🎯 Final Ticket")
                    st.info(f"League: {selected_league_name}\nTarget: €{target}")
                    for tm in ticket:
                        st.success(f"**{tm['teams']}**\nOdds: {tm['quote']}")
                    
                    st.metric("Total Odds", f"{current_odds:.2f}")
                    st.metric("Potential Return", f"€{round(stake * current_odds, 2)}")

        except Exception as e:
            st.error(f"API Error: {e}")

# Footer
st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
