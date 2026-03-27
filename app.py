import streamlit as st
import sqlite3
import hashlib
import requests
import random
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
            h_att = d.get('comparison', {}).get('att', '50%').replace('%','')
            # Safety conversion
            h_att = int(h_att) if h_att.isdigit() else 50
            return {"h_att": h_att, "prob": random.randint(75, 99)}
    except: return None

# --- 3. UI STYLING ---
st.set_page_config(page_title="EDGE AI | LUXURY WEB", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #111; }
    .match-card { background: #080808; border: 1px solid #111; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .ticket-active { background: #001a00; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("E D G E  A I")
        t1, t2 = st.tabs(["LOGIN", "SIGNUP"])
        with t1:
            u = st.text_input("User")
            p = st.text_input("Pass", type="password")
            if st.button("LOGIN"):
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
                if c.fetchone():
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Access Denied")
        with t2:
            nu = st.text_input("New User")
            np = st.text_input("New Pass", type="password")
            if st.button("REGISTER"):
                try:
                    c = conn.cursor()
                    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nu, hash_password(np)))
                    conn.commit()
                    st.success("Registered!")
                except: st.error("Exists")
    st.stop()

# --- 5. MAIN DASHBOARD ---
st.sidebar.title("E D G E / P R E C I S I O N")
horizon_map = {"Today Only": 1, "1 Week": 7, "2 Weeks": 14}
horizon = st.sidebar.radio("TIME HORIZON", list(horizon_map.keys()))
league_choice = st.sidebar.selectbox("MARKET", ["Global Markets", "Premier League", "Serie A", "La Liga", "Int. Friendlies"])
LEAGUE_IDS = {"Global Markets": 0, "Premier League": 39, "Serie A": 135, "La Liga": 140, "Int. Friendlies": 10}

stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)

if st.sidebar.button("SCAN GLOBAL MARKET"):
    with st.spinner("Scanning..."):
        all_matches = {}
        days = horizon_map[horizon]
        l_id = LEAGUE_IDS[league_choice]
        
        for i in range(days):
            date_obj = datetime.now() + timedelta(days=i)
            date_str = date_obj.strftime('%Y-%m-%d')
            disp_date = date_obj.strftime('%A, %d %b')
            
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            if l_id != 0: f_url += f"&league={l_id}"
            
            try:
                res = requests.get(f_url, headers=HEADERS).json().get('response', [])
                if res:
                    day_matches = []
                    for m in res[:15]:
                        intel = get_match_intel(m['fixture']['id'])
                        day_matches.append({
                            "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                            "tip": "HOME WIN" if (intel and intel['h_att'] > 60) else "OVER 1.5",
                            "odds": round(random.uniform(1.3, 2.2), 2),
                            "prob": intel['prob'] if intel else random.randint(70, 85)
                        })
                    all_matches[disp_date] = day_matches
            except: pass
        
        st.session_state.master_matches = all_matches

# --- 6. DISPLAY (CRASH PROOF) ---
if 'master_matches' in st.session_state:
    if not st.session_state.master_matches:
        st.warning("⚠️ No matches found for this selection. Try 'Global Markets'.")
    else:
        col_main, col_ticket = st.columns([2, 1])
        
        with col_main:
            # FIX: Ensure there is at least one key before creating tabs
            tab_labels = list(st.session_state.master_matches.keys())
            tabs = st.tabs(tab_labels)
            
            for i, tab in enumerate(tabs):
                with tab:
                    date_key = tab_labels[i]
                    for match in st.session_state.master_matches[date_key]:
                        st.markdown(f"""
                        <div class="match-card">
                            <b>{match['teams']}</b><br>
                            <span style="color:#00ff00;">{match['tip']} @ {match['odds']}</span>
                        </div>
                        """, unsafe_allow_html=True)

        with col_ticket:
            st.subheader("LIVE TICKET")
            flat = [m for sublist in st.session_state.master_matches.values() for m in sublist]
            picks = sorted(flat, key=lambda x: x['prob'], reverse=True)
            
            ticket = []; c_odds = 1.0; req = target/stake
            for p in picks:
                if c_odds < req:
                    ticket.append(p); c_odds *= p['odds']
            
            st.markdown('<div class="ticket-active">', unsafe_allow_html=True)
            for t in ticket:
                st.write(f"✅ {t['teams']} (@{t['odds']})")
            st.write(f"**Total Odds: {c_odds:.2f}**")
            st.write(f"**Win: €{stake*c_odds:.2f}**")
            st.markdown('</div>', unsafe_allow_html=True)
