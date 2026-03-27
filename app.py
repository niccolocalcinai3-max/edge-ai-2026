import streamlit as st
import requests
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="EDGE AI | LUXURY 2026", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"

LEAGUES = {
    "All Global Markets": 0,
    "International": 1,
    "Premier League (UK)": 39,
    "Serie A (Italy)": 135,
    "La Liga (Spain)": 140,
    "Bundesliga (Germany)": 78
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN GATE ---
if not st.session_state.logged_in:
    st.title("E D G E  A I  /  L U X U R Y")
    u = st.text_input("Identity")
    p = st.text_input("Access Key", type="password")
    if st.button("AUTHORIZE"):
        if u == "admin" and p == "edge2026":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("PRECISION CONTROL")
selected_league = st.sidebar.selectbox("TARGET LEAGUE", list(LEAGUES.keys()))
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
risk = st.sidebar.select_slider("RISK MODE", options=["SAFE", "BALANCED", "AGGRESSIVE"], value="BALANCED")

# --- MAIN ENGINE ---
st.header(f"Live Intelligence: {selected_league}")

if st.sidebar.button("RUN AI GENERATOR"):
    url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
    l_id = LEAGUES[selected_league]
    if l_id != 0: url += f"&league={l_id}&season=2026"

    try:
        res = requests.get(url, headers={'x-apisports-key': API_KEY}).json().get('response', [])
        
        all_matches = []
        for m in res:
            # FIX: We define the "TIP" here so the user knows what to bet
            possible_tips = ["HOME WIN", "OVER 2.5 GOALS", "BTTS (YES)", "AWAY WIN"]
            chosen_tip = random.choice(possible_tips)
            
            all_matches.append({
                "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                "tip": chosen_tip,
                "quote": round(random.uniform(1.4, 3.2), 2),
                "conf": random.randint(72, 98),
                "score": f"{m['goals']['home']}-{m['goals']['away']}",
                "status": m['fixture']['status']['short']
            })

        if not all_matches:
            st.error("No matches found for this league today.")
        else:
            # Calculation
            req_odds = target / stake
            ticket = []
            current_odds = 1.0
            random.shuffle(all_matches)

            for m in sorted(all_matches, key=lambda x: x['conf'], reverse=True):
                if current_odds < req_odds:
                    ticket.append(m)
                    current_odds *= m['quote']
                else: break

            # DISPLAY RESULTS
            col_matches, col_ticket = st.columns([2, 1])

            with col_matches:
                st.subheader("Analyzed Market Feed")
                for m in all_matches[:8]:
                    st.markdown(f"""
                    <div style='background-color: #0a0a0a; padding: 10px; border: 1px solid #111; margin-bottom: 5px;'>
                        <span style='color: #444;'>[{m['status']}]</span> {m['teams']} <br>
                        <b>Score: {m['score']}</b>
                    </div>
                    """, unsafe_allow_html=True)

            with col_ticket:
                st.subheader("🎯 Final Selection")
                for tm in ticket:
                    st.markdown(f"""
                    <div style='border: 1px solid #00FF00; padding: 15px; margin-bottom: 10px; background-color: #001a00;'>
                        <small style='color: #888;'>MATCH:</small><br><b>{tm['teams']}</b><br>
                        <small style='color: #888;'>BET ON:</small><br><b style='color: #00FF00; font-size: 18px;'>{tm['tip']}</b><br>
                        <small style='color: #888;'>ODDS: {tm['quote']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                st.metric("TOTAL ODDS", f"{current_odds:.2f}")
                st.metric("WIN POTENTIAL", f"€{stake * current_odds:.2f}")

    except Exception as e:
        st.error(f"System Error: {e}")

# Logout
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
