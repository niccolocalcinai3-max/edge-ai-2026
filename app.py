import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# --- CONFIGURAZIONE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
FREE_LEAGUES = {"SA": "SA", "PL": "PL", "PD": "PD", "BL1": "BL1", "FL1": "FL1"}

st.set_page_config(page_title="EDGE NOIR", layout="wide")

# --- CUSTOM CSS & PARTICLES EFFECT ---
st.markdown("""
    <style>
    /* Reset Minimalista */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'JetBrains Mono', monospace;
        background-color: #000000;
        color: #FFFFFF;
    }

    /* Background Particles Canvas */
    #particles-js {
        position: fixed;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        z-index: -1;
    }

    .stButton>button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 0px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    .match-box {
        border: 1px solid #333;
        padding: 20px;
        margin-bottom: 10px;
        background: rgba(10, 10, 10, 0.8);
        border-radius: 0px;
    }

    .gold-box {
        border: 1px solid #FFFFFF;
        padding: 20px;
        margin-bottom: 20px;
        background: #FFFFFF;
        color: #000000;
    }

    /* Nascondi header Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .metric-value { font-size: 2em; font-weight: 700; }
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
            this.size = Math.random() * 1.5;
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
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    function init() {
        for (let i = 0; i < 100; i++) { particles.push(new Particle()); }
    }
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animate);
    }
    init(); animate();
    </script>
    """, unsafe_allow_html=True)

# --- LOGICA ---
def get_time(utc_str):
    dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
    return dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Rome'))

# --- SIDEBAR ---
st.sidebar.title("[ EDGE_NOIR ]")
st.sidebar.markdown("---")
bankroll = st.sidebar.number_input("CAPITAL [€]", value=200.0)

st.sidebar.subheader("STRATEGIES")
if st.sidebar.button("-> LOAD_SAFE"):
    st.session_state['mode'] = "SAFE"
    st.session_state['matches'] = [
        {"Match": "JUVENTUS vs FIORENTINA", "Tip": "1X + U3.5", "Odds": 1.50, "Lega": "SERIE A"},
        {"Match": "LIVERPOOL vs EVERTON", "Tip": "OVER 2.5", "Odds": 1.62, "Lega": "PREMIER"},
        {"Match": "REAL MADRID vs VILLARREAL", "Tip": "1", "Odds": 1.45, "Lega": "LA LIGA"},
        {"Match": "LEVERKUSEN vs LEIPZIG", "Tip": "GOAL", "Odds": 1.55, "Lega": "BUNDESLIGA"}
    ]

if st.sidebar.button("-> LOAD_100"):
    st.session_state['mode'] = "RISK"
    st.session_state['matches'] = [
        {"Match": "BOLOGNA vs INTER", "Tip": "X", "Odds": 3.60, "Lega": "SERIE A"},
        {"Match": "NEWCASTLE vs MAN UTD", "Tip": "2 + GOAL", "Odds": 4.80, "Lega": "PREMIER"},
        {"Match": "ATH. BILBAO vs ATL. MADRID", "Tip": "1 + U2.5", "Odds": 4.20, "Lega": "LA LIGA"},
        {"Match": "DORTMUND vs STUTTGART", "Tip": "O3.5 + GOAL", "Odds": 3.20, "Lega": "BUNDESLIGA"},
        {"Match": "MARSEILLE vs NICE", "Tip": "X + U2.5", "Odds": 3.50, "Lega": "LIGUE 1"}
    ]

st.sidebar.divider()
g_match = st.sidebar.text_input("GOLD_MATCH")
g_tip = st.sidebar.text_input("GOLD_TIP")
g_odds = st.sidebar.number_input("GOLD_ODDS", value=1.50)
if st.sidebar.button("-> SAVE_GOLD"):
    st.session_state['gold'] = {"Match": g_match, "Tip": g_tip, "Odds": g_odds}

if st.sidebar.button("-> RESET"):
    st.session_state.clear()
    st.rerun()

# --- MAIN ---
c1, c2 = st.columns([2, 1])

with c1:
    if 'gold' in st.session_state:
        g = st.session_state['gold']
        st.markdown(f'<div class="gold-box"><b>[ GOLD_SELECTION ]</b><br>{g["Match"]} / {g["Tip"]} / @{g["Odds"]}</div>', unsafe_allow_html=True)
    
    st.subheader("[ MARKET_SCAN ]")
    if 'matches' in st.session_state:
        for m in st.session_state['matches']:
            st.markdown(f"""<div class="match-box">
                <small>{m['Lega']}</small><br>
                <b>{m['Match']}</b><br>
                <span>{m['Tip']} // @{m['Odds']}</span>
            </div>""", unsafe_allow_html=True)

with c2:
    st.subheader("[ SUMMARY ]")
    if 'matches' in st.session_state:
        total_odds = 1.0
        ticket_str = "--- EDGE NOIR TICKET ---\n"
        for m in st.session_state['matches']:
            total_odds *= m['Odds']
            ticket_str += f"| {m['Match']} -> {m['Tip']} (@{m['Odds']})\n"
        
        if 'gold' in st.session_state:
            total_odds *= st.session_state['gold']['Odds']
            ticket_str += f"| GOLD: {st.session_state['gold']['Match']} (@{st.session_state['gold']['Odds']})\n"

        stake = round(bankroll * (0.08 if st.session_state.get('mode') == "SAFE" else 0.02), 2)
        
        st.markdown(f"""
            <div style="border: 1px solid #333; padding: 20px;">
                <small>TOTAL_ODDS</small><br><span class="metric-value">{total_odds:.2f}</span><br><br>
                <small>STAKE_SUGGESTED</small><br><span class="metric-value">€{stake}</span><br><br>
                <small>EST_RETURN</small><br><span class="metric-value">€{round(total_odds * stake, 2)}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button("-> EXPORT_TXT", data=ticket_str, file_name="noir_ticket.txt")
