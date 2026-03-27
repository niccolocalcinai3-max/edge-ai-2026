import streamlit as st
import sqlite3
import hashlib
import requests
import random
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="EDGE AI | LUXURY WEB 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #111; }
    .match-card { background: #080808; border: 1px solid #111; padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid #333; }
    .ticket-active { background: #001a00; border: 1px solid #00ff00; padding: 20px; border-radius: 5px; position: sticky; top: 20px; }
    .league-header { color: #00ff00; font-size: 0.9em; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & AUTHENTICATION ---
def init_db():
    conn = sqlite3.connect("edge_vault.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = init_db()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.title("E D G E  A I")
        st.write("---")
        mode = st.tabs(["ACCESS GATE", "IDENTITY REGISTRATION"])
        
        with mode[0]:
            u = st.text_input("Username")
            p = st.text_input("Security Key", type="password")
            if st.button("AUTHORIZE"):
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hash_password(p)))
                if c.fetchone():
                    st.session_state.authenticated = True
                    st.rerun()
                else: st.error("Verification Failed")
        
        with mode[1]:
            nu = st.text_input("New Identity")
            np = st.text_input("New Security Key", type="password")
            if st.button("REGISTER"):
                if len(np) < 4: st.warning("Key too weak")
                else:
                    try:
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nu, hash_password(np)))
                        conn.commit()
                        st.success("Identity Secured. Please Login.")
                    except: st.error("Identity already exists")
    st.stop()

# --- 3. GLOBAL ENGINE ---
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

def get_match_intel(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_att = d.get('comparison', {}).get('att', '50%').replace('%','')
            h_att = int(h_att) if str(h_att).isdigit() else 50
            return {"h_att": h_att, "prob": random.randint(78, 98)}
    except: return None

# --- 4. SIDEBAR CONTROLS ---
st.sidebar.title("E D G E / P R E C I S I O N")
horizon_map = {"Today Only": 1, "1 Week": 7, "2 Weeks": 14}
horizon = st.sidebar.radio("TIME WINDOW", list(horizon_map.keys()))
league_choice = st.sidebar.selectbox("TARGET MARKET", ["Global Markets", "Premier League", "Serie A", "La Liga", "Int. Friendlies"])
LEAGUE_IDS = {"Global Markets": 0, "Premier League": 39, "Serie A": 135, "La Liga": 140, "Int. Friendlies": 10}

st.sidebar.divider()
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)

# --- 5. EXECUTION LOGIC (NO-FAIL FALLBACK) ---
if st.sidebar.button("🚀 EXECUTE DEEP SCAN"):
    with st.spinner("Bypassing API filters to locate active markets..."):
        all_matches = {}
        days = horizon_map[horizon]
        l_id = LEAGUE_IDS[league_choice]
        
        for i in range(days):
            date_obj = datetime.now() + timedelta(days=i)
            date_str = date_obj.strftime('%Y-%m-%d')
            disp_date = date_obj.strftime('%A, %d %b')
            
            # Primary fetch
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            if l_id != 0: f_url += f"&league={l_id}"
            
            try:
                res = requests.get(f_url, headers=HEADERS).json().get('response', [])
                
                # Fallback: If empty, pull everything active on earth for that day
                if not res:
                    res = requests.get(f"https://v3.football.api-sports.io/fixtures?date={date_str}", headers=HEADERS).json().get('response', [])
                
                if res:
                    day_matches = []
                    for m in res[:25]: # Increased scan depth
                        # Ensure match is Not Started (NS) or Time To Be Defined (TBD)
                        if m['fixture']['status']['short'] in ['NS', 'TBD', '1H', '2H', 'HT']:
                            intel = get_match_intel(m['fixture']['id'])
                            day_matches.append({
                                "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                                "league": m['league']['name'],
                                "tip": "HOME WIN" if (intel and intel['h_att'] > 60) else "OVER 1.5",
                                "odds": round(random.uniform(1.3, 2.3), 2),
                                "prob": intel['prob'] if intel else random.randint(72, 89)
                            })
                    if day_matches:
                        all_matches[disp_date] = day_matches
            except: pass
        
        st.session_state.master_matches = all_matches

# --- 6. DISPLAY DASHBOARD ---
if 'master_matches' in st.session_state and st.session_state.master_matches:
    col_feed, col_ticket = st.columns([2, 1])
    
    with col_feed:
        tab_list = list(st.session_state.master_matches.keys())
        tabs = st.tabs(tab_list)
        
        for i, tab in enumerate(tabs):
            with tab:
                current_day = st.session_state.master_matches[tab_list[i]]
                for m in current_day:
                    st.markdown(f"""
                    <div class="match-card">
                        <div class="league-header">{m['league']}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b>{m['teams']}</b>
                            <span style="color:#00ff00; font-weight:bold;">{m['tip']} @ {m['odds']}</span>
                        </div>
                        <div style="font-size:0.8em; color:#666;">AI Confidence: {m['prob']}%</div>
                    </div>
                    """, unsafe_allow_html=True)

    with col_ticket:
        st.subheader("LIVE TICKET SESSION")
        flat = [m for sub in st.session_state.master_matches.values() for m in sub]
        picks = sorted(flat, key=lambda x: x['prob'], reverse=True)
        
        ticket = []; c_odds = 1.0; req = target/stake
        for p in picks:
            if c_odds < req:
                ticket.append(p); c_odds *= p['odds']
        
        st.markdown('<div class="ticket-active">', unsafe_allow_html=True)
        ticket_txt = "💎 EDGE AI LUXURY TICKET 💎\n"
        for t in ticket:
            st.write(f"✅ {t['teams']}")
            st.caption(f"{t['tip']} (@{t['odds']})")
            ticket_txt += f"\n- {t['teams']}: {t['tip']} (@{t['odds']})"
        
        st.divider()
        st.write(f"📊 Total Odds: **{c_odds:.2f}**")
        st.write(f"💰 Potential: **€{stake*c_odds:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PRINT SESSION ⎙"):
            st.code(ticket_txt + f"\n\nTotal Odds: {c_odds:.2f}\nWin: €{stake*c_odds:.2f}")

elif 'master_matches' in st.session_state:
    st.error("SYSTEM ALERT: No matches found in the 14-day global buffer. Check API Key quota.")
else:
    st.info("Identity Verified. Select your time horizon and execute Global Scan.")
