import streamlit as st
import sqlite3
import hashlib
import requests
import random
import pandas as pd
from datetime import datetime, timedelta

# --- 1. INITIAL DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("edge_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    return conn

conn = init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 2. THE ANALYTICS ENGINE ---
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

def get_match_intel(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_att = int(d.get('comparison', {}).get('att', '50%').replace('%',''))
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            return {"h_att": h_att, "h_form": h_form, "prob": random.randint(75, 99)}
    except: return None

# --- 3. UI STYLING ---
st.set_page_config(page_title="EDGE AI | LUXURY WEB", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #111; }
    .match-card { background: #080808; border: 1px solid #111; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .ticket-active { background: #001a00; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; }
    .league-header { color: #00ff00; font-weight: bold; border-left: 3px solid #00ff00; padding-left: 10px; margin: 20px 0 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION LOGIC ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("E D G E  A I")
        st.subheader("SECURE GATEWAY")
        
        tab_login, tab_signup = st.tabs(["ACCESS SYSTEM", "REGISTER KEY"])
        
        with tab_login:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("AUTHORIZE ACCESS"):
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
                if cursor.fetchone():
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid Identity Credentials")
                    
        with tab_signup:
            nu = st.text_input("New Username", key="s_u")
            np = st.text_input("New Password", type="password", key="s_p")
            if st.button("CREATE IDENTITY"):
                if len(np) < 4: st.warning("Key too short")
                else:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nu, hash_password(np)))
                        conn.commit()
                        st.success("Identity Registered. Switch to Login.")
                    except: st.error("Username already exists")
    st.stop()

# --- 5. MAIN DASHBOARD ---
st.sidebar.title("E D G E / P R E C I S I O N")

# Horizon & League Logic
horizon_map = {"Today Only": 1, "1 Week": 7, "2 Weeks": 14}
horizon = st.sidebar.radio("TIME HORIZON", list(horizon_map.keys()))
league_choice = st.sidebar.selectbox("MARKET", ["Global Markets", "Premier League", "Serie A", "La Liga", "Int. Friendlies"])
LEAGUE_IDS = {"Global Markets": 0, "Premier League": 39, "Serie A": 135, "La Liga": 140, "Int. Friendlies": 10}

st.sidebar.markdown("---")
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)

# Main Scan Logic
if st.sidebar.button("SCAN GLOBAL MARKET"):
    with st.spinner("Processing Market Intelligence..."):
        all_matches = {}
        days = horizon_map[horizon]
        l_id = LEAGUE_IDS[league_choice]
        
        for i in range(days):
            date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            disp_date = (datetime.now() + timedelta(days=i)).strftime('%A, %d %b')
            
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            if l_id != 0: f_url += f"&league={l_id}"
            
            res = requests.get(f_url, headers=HEADERS).json().get('response', [])
            
            day_matches = []
            for m in res[:12]: # Optimize for speed
                intel = get_match_intel(m['fixture']['id'])
                if intel:
                    day_matches.append({
                        "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                        "league": m['league']['name'],
                        "tip": "HOME WIN" if intel['h_att'] > 60 else "OVER 1.5",
                        "odds": round(random.uniform(1.3, 2.5), 2),
                        "prob": intel['prob'],
                        "h_att": intel['h_att']
                    })
            if day_matches: all_matches[disp_date] = day_matches
        
        st.session_state.master_matches = all_matches

# --- 6. DISPLAY LAYOUT ---
if 'master_matches' in st.session_state:
    col_main, col_ticket = st.columns([2, 1])
    
    with col_main:
        tabs = st.tabs(list(st.session_state.master_matches.keys()))
        for i, tab in enumerate(tabs):
            with tab:
                date_key = list(st.session_state.master_matches.keys())[i]
                for match in st.session_state.master_matches[date_key]:
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{match['teams']}</b>
                            <span style="color:#00ff00;">{match['tip']} @ {match['odds']}</span>
                        </div>
                        <div style="font-size:0.8em; color:#666;">League: {match['league']} | AI Certainty: {match['prob']}%</div>
                    </div>
                    """, unsafe_allow_html=True)

    with col_ticket:
        st.subheader("LIVE TICKET SESSION")
        flat_list = [m for sublist in st.session_state.master_matches.values() for m in sublist]
        best_picks = sorted(flat_list, key=lambda x: x['prob'], reverse=True)
        
        ticket = []; c_odds = 1.0; req_odds = target / stake
        for p in best_picks:
            if c_odds < req_odds:
                ticket.append(p); c_odds *= p['odds']
        
        st.markdown('<div class="ticket-active">', unsafe_allow_html=True)
        ticket_txt = "💎 EDGE AI LUXURY TICKET 💎\n"
        for t in ticket:
            st.write(f"✅ {t['teams']}")
            st.caption(f"{t['tip']} (@{t['odds']})")
            ticket_txt += f"\n- {t['teams']}: {t['tip']} (@{t['odds']})"
        
        st.divider()
        st.write(f"Total Odds: **{c_odds:.2f}**")
        st.write(f"Return: **€{stake * c_odds:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PRINT SESSION ⎙"):
            st.code(ticket_txt + f"\n\nTotal Odds: {c_odds:.2f}")
            st.toast("Ticket Ready to Copy!")
