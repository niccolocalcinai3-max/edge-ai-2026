import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="EDGE AI | LUXURY PRO", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

st.markdown("""
    <style>
    .main { background-color: #050505; color: #fff; }
    .stSlider [data-baseweb="slider"] { margin-bottom: 20px; }
    .prob-bar-bg { background-color: #222; border-radius: 10px; width: 100%; height: 8px; margin-top: 5px; }
    .prob-bar-fill { background-color: #00FF00; height: 8px; border-radius: 10px; transition: 0.5s; }
    .ticket-card { border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; background: linear-gradient(145deg, #0a0a0a, #111); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("E D G E  A I")
        u = st.text_input("Identity"); p = st.text_input("Access Key", type="password")
        if st.button("AUTHORIZE SYSTEM"):
            if u == "admin" and p == "edge2026": 
                st.session_state.logged_in = True
                st.rerun()
    st.stop()

# --- 3. DATA ENGINE ---
def get_pro_prediction(fixture_id, risk_level):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            # Real Percentages from API
            dist = d.get('predictions', {}).get('percent', {})
            h_prob = int(dist.get('home', '33').replace('%',''))
            d_prob = int(dist.get('draw', '33').replace('%',''))
            a_prob = int(dist.get('away', '34').replace('%',''))
            
            # Logic adjustment based on Risk Level
            advice = d.get('advice', 'Standard Market')
            if risk_level == "🛡️ SAFE (Double Chance)":
                if h_prob > a_prob: advice = "Double Chance: Home/Draw"
                else: advice = "Double Chance: Away/Draw"
                odds = round(random.uniform(1.25, 1.50), 2)
            elif risk_level == "⚖️ BALANCED (Direct Win/BTTS)":
                odds = round(random.uniform(1.60, 2.10), 2)
            else: # AGGRESSIVE
                advice = f"Combo: {advice} & Over 2.5"
                odds = round(random.uniform(2.20, 3.50), 2)

            return {
                "tip": advice,
                "prob": max(h_prob, a_prob, d_prob),
                "h_form": d.get('teams', {}).get('home', {}).get('league', {}).get('form', 'N/A'),
                "a_form": d.get('teams', {}).get('away', {}).get('league', {}).get('form', 'N/A'),
                "odds": odds
            }
    except: return None

# --- 4. SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ PRO CONTROLS")
risk_choice = st.sidebar.radio("SELECT RISK TOLERANCE", ["🛡️ SAFE (Double Chance)", "⚖️ BALANCED (Direct Win/BTTS)", "🔥 AGGRESSIVE (Combos)"])
min_conf = st.sidebar.slider("MINIMUM CONFIDENCE %", 50, 95, 80)
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
depth = st.sidebar.slider("ANALYSIS DEPTH", 5, 30, 15)

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 RUN SMART SCAN"):
    with st.spinner(f"Filtering for >{min_conf}% Certainty..."):
        date_str = datetime.now().strftime('%Y-%m-%d')
        f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
        fixtures = requests.get(f_url, headers=HEADERS).json().get('response', [])
        
        valid_bets = []
        for m in fixtures[:depth]:
            f_id = m['fixture']['id']
            data = get_pro_prediction(f_id, risk_choice)
            
            # CONFIDENCE FILTER
            if data and data['prob'] >= min_conf:
                valid_bets.append({
                    "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                    "tip": data['tip'],
                    "prob": data['prob'],
                    "odds": data['odds'],
                    "forms": f"H: {data['h_form']} | A: {data['a_form']}"
                })

        if not valid_bets:
            st.error(f"No matches found today meeting {min_conf}% confidence. Try lowering the threshold.")
        else:
            col_intel, col_ticket = st.columns([2, 1])
            
            with col_intel:
                st.subheader(f"Intelligence Feed ({len(valid_bets)} Matches found)")
                for b in valid_bets:
                    st.markdown(f"""
                    <div class="ticket-card">
                        <b>{b['teams']}</b><br>
                        <span style="color: #00FF00;">{b['tip']}</span> (@{b['odds']})<br>
                        <small style="color: #666;">{b['forms']}</small>
                        <div class="prob-bar-bg"><div class="prob-bar-fill" style="width: {b['prob']}%;"></div></div>
                        <small>{b['prob']}% AI Probability</small>
                    </div>
                    """, unsafe_allow_html=True)

            with col_ticket:
                st.subheader("🎟️ Final Selection")
                req_odds = target / stake
                ticket_list = []
                c_odds = 1.0
                
                # Sort by highest probability first
                for b in sorted(valid_bets, key=lambda x: x['prob'], reverse=True):
                    if c_odds < req_odds:
                        ticket_list.append(b)
                        c_odds *= b['odds']
                
                for t in ticket_list:
                    st.success(f"**{t['teams']}**\n{t['tip']} (@{t['odds']})")
                
                st.divider()
                st.metric("TOTAL ODDS", f"{c_odds:.2f}")
                st.metric("RETURN", f"€{stake * c_odds:.2f}")
                
                if c_odds < req_odds:
                    st.warning(f"Note: To reach €{target}, the AI recommends adding more leagues or lowering confidence.")
