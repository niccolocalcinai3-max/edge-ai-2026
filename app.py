import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
FREE_LEAGUES = {"SA": "SA", "PL": "PL", "PD": "PD", "BL1": "BL1", "FL1": "FL1", "CL": "CL"}

st.set_page_config(page_title="EDGE_NOIR_V20", layout="wide")

# --- CSS & JS PARTICLES (BACKGROUND) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    #canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }

    .stButton>button {
        background-color: transparent !important;
        color: #FFF !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
        width: 100%;
        letter-spacing: 2px;
        font-size: 0.8rem;
    }
    
    .stButton>button:hover {
        border-color: #FFF !important;
        background-color: #FFF !important;
        color: #000 !important;
    }

    .match-box {
        border: 1px solid #222;
        padding: 15px;
        margin-bottom: 10px;
        background: rgba(5, 5, 5, 0.7);
    }

    .gold-box {
        border: 1px solid #FFF;
        padding: 20px;
        background: #FFF;
        color: #000;
        margin-bottom: 25px;
        font-weight: bold;
    }

    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #000 !important;
        color: #FFF !important;
        border: 1px solid #333 !important;
        border-radius: 0px !important;
    }

    h1, h2, h3 { letter-spacing: -1px; text-transform: uppercase; }
    </style>

    <canvas id="canvas"></canvas>
    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    let particles = [];
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speedX = Math.random() * 0.5 - 0.25;
            this.speedY = Math.random() * 0.5 - 0.25;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x > canvas.width) this.x = 0;
            if (this.x < 0) this.x = canvas.width;
            if (this.y > canvas.height) this.y = 0;
            if (this.y < 0) this.y = canvas.height;
        }
        draw() {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    function init() {
        particles = [];
        for (let i = 0; i < 80; i++) { particles.push(new Particle()); }
    }
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animate);
    }
    window.addEventListener('resize', function(){
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        init();
    });
    init(); animate();
    </script>
    """, unsafe_allow_html=True)

# --- LOGICA API ---
def fetch_real_matches(leagues):
    headers = {'X-Auth-Token': API_KEY}
    date_to = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}matches?dateTo={date_to}"
    try:
        res = requests.get(url, headers=headers).json()
        found = []
        for m in res.get('matches', []):
            if m['competition']['code'] in [FREE_LEAGUES[l] for l in leagues]:
                found.append({
                    "Match": f"{m['homeTeam']['name']} / {m['awayTeam']['name']}",
                    "Lega": m['competition']['name'],
                    "Tip": "1X / U4.5" if m['homeTeam']['id'] < m['awayTeam']['id'] else "X2",
                    "Odds": 1.52
                })
        return found
    except: return []

# --- SIDEBAR ---
st.sidebar.title("SYSTEM / V20")
st.sidebar.markdown("---")
bankroll = st.sidebar.number_input("BANKROLL_EUR", value=500.0)

st.sidebar.subheader("/ STRATEGY_LOAD")
if st.sidebar.button("-> SAFE_ELITE"):
    st.session_state['mode'] = "SAFE"
    st.session_state['matches'] = [
        {"Match": "JUVENTUS / FIORENTINA", "Tip": "1X + U3.5", "Odds": 1.50, "Lega": "SERIE A"},
        {"Match": "LIVERPOOL / EVERTON", "Tip": "OVER 2.5", "Odds": 1.62, "Lega": "PREMIER"},
        {"Match": "REAL MADRID / VILLARREAL", "Tip": "1", "Odds": 1.45, "Lega": "LA LIGA"},
        {"Match": "LEVERKUSEN / LEIPZIG", "Tip": "GOAL", "Odds": 1.55, "Lega": "BUNDESLIGA"}
    ]

if st.sidebar.button("-> TARGET_100"):
    st.session_state['mode'] = "RISK"
    st.session_state['matches'] = [
        {"Match": "BOLOGNA / INTER", "Tip": "X", "Odds": 3.60, "Lega": "SERIE A"},
        {"Match": "NEWCASTLE / MAN UTD", "Tip": "2 + GOAL", "Odds": 4.80, "Lega": "PREMIER"},
        {"Match": "BILBAO / ATL. MADRID", "Tip": "1 + U2.5", "Odds": 4.20, "Lega": "LA LIGA"},
        {"Match": "DORTMUND / STUTTGART", "Tip": "O3.5 + GOAL", "Odds": 3.20, "Lega": "BUNDESLIGA"},
        {"Match": "MARSEILLE / NICE", "Tip": "X + U2.5", "Odds": 3.50, "Lega": "LIGUE 1"}
    ]

st.sidebar.subheader("/ LIVE_SCAN")
sel_l = st.sidebar.multiselect("SELECT_LEAGUES", list(FREE_LEAGUES.keys()), default=["SA", "PL"])
if st.sidebar.button("-> RUN_SCAN"):
    st.session_state['mode'] = "LIVE"
    st.session_state['matches'] = fetch_real_matches(sel_l)

st.sidebar.divider()
g_m = st.sidebar.text_input("GOLD_MATCH")
g_t = st.sidebar.text_input("GOLD_TIP")
g_o = st.sidebar.number_input("GOLD_ODDS", value=1.50)
if st.sidebar.button("-> COMMIT_GOLD"):
    st.session_state['gold'] = {"Match": g_m, "Tip": g_t, "Odds": g_o}

if st.sidebar.button("-> RESET"):
    st.session_state.clear()
    st.rerun()

# --- MAIN ---
c1, c2 = st.columns([2, 1])

with c1:
    if 'gold' in st.session_state:
        g = st.session_state['gold']
        st.markdown(f'<div class="gold-box">/ GOLD_SELECTION / {g["Match"]} // {g["Tip"]} @ {g["Odds"]}</div>', unsafe_allow_html=True)
    
    st.subheader("/ MARKET_FEED")
    if 'matches' in st.session_state:
        for m in st.session_state['matches']:
            st.markdown(f"""<div class="match-box">
                <small>{m['Lega']}</small><br>
                <b>{m['Match']}</b><br>
                <span>{m['Tip']} // {m['Odds']}</span>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("SYSTEM_IDLE: AWAITING_INPUT")

with c2:
    st.subheader("/ TICKET_DATA")
    if 'matches' in st.session_state:
        total_odds = 1.0
        output_txt = "--- EDGE_NOIR_REPORT ---\n"
        for m in st.session_state['matches']:
            total_odds *= m['Odds']
            output_txt += f"| {m['Match']} -> {m['Tip']} (@{m['Odds']})\n"
        
        if 'gold' in st.session_state:
            total_odds *= st.session_state['gold']['Odds']
            output_txt += f"| GOLD_TIP: {st.session_state['gold']['Match']} (@{st.session_state['gold']['Odds']})\n"

        stake = round(bankroll * (0.08 if st.session_state.get('mode') == "SAFE" else 0.02), 2)
        
        st.markdown(f"""
            <div style="border: 1px solid #222; padding: 20px; background: rgba(0,0,0,0.5);">
                <small>COMBINED_ODDS</small><br><b>{total_odds:.2f}</b><br><br>
                <small>STAKE_ADVISED</small><br><b>€{stake}</b><br><br>
                <small>POTENTIAL_RETURN</small><br><b style="font-size: 1.5em;">€{round(total_odds * stake, 2)}</b>
            </div>
        """, unsafe_allow_html=True)
        
        st.text_area("RAW_DATA", value=output_txt + f"\nTOTAL_ODDS: {total_odds:.2f}", height=150)
        st.download_button("-> DOWNLOAD_REPORT", data=output_txt, file_name="report_noir.txt")
