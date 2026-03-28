import streamlit as st
import requests
import os
from datetime import datetime, timedelta

# --- CONFIGURAZIONE CORE ---
API_KEY = "0b3023a2a74049d0814cba1fea80ce26"
BASE_URL = "https://api.football-data.org/v4/"
SAVE_FILE = "gold_storage.txt"
LEAGUES = {"Serie A": "SA", "Premier League": "PL", "La Liga": "PD", "Bundesliga": "BL1", "Ligue 1": "FL1"}

st.set_page_config(page_title="EDGE PRO SHADOW", layout="wide")

# --- UI ENHANCEMENT (GLASSMORPHISM & ANIMATIONS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Global Reset */
    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #020202 !important; 
        color: #FFFFFF !important; 
    }

    /* Background Subtle Glow */
    .main {
        background: radial-gradient(circle at top right, #111 0%, #020202 100%);
    }

    /* Glass Cards */
    .st-emotion-cache-1r6slb0, .match-card, .strategy-card {
        background: rgba(15, 15, 15, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    .match-card:hover, .strategy-card:hover {
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px);
        background: rgba(20, 20, 20, 0.8) !important;
    }

    /* Premium Buttons */
    .stButton>button {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        height: 45px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }

    /* Secondary/Sidebar Buttons */
    section[data-testid="stSidebar"] .stButton>button {
        background: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stButton>button:hover {
        border: 1px solid #FFFFFF !important;
        background: rgba(255,255,255,0.05) !important;
    }

    /* Gold Card Special Style */
    .gold-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #E0E0E0 100%);
        color: #000000;
        padding: 15px;
        border-radius: 10px;
        font-weight: 700;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(255,255,255,0.1);
    }

    /* Status Dot Animation */
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #FFF;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
    }

    /* Typography */
    h1, h2, h3 { font-weight: 700; letter-spacing: -1px; }
    .sub-text { color: #666; font-size: 0.7rem; text-transform: uppercase; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI PERSISTENZA ---
def save_gold(gold_list):
    with open(SAVE_FILE, "w") as f:
        for g in gold_list: f.write(f"{g['Match']}|{g['Tip']}|{g['Odds']}\n")

def load_gold():
    lst = []
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3: lst.append({"Match": parts[0], "Tip": parts[1], "Odds": float(parts[2])})
    return lst

# --- DATABASE CASINO ---
STRATEGIES_CASINO = {
    "SAFE": {
        "SHIELD 1-2": "Copre 70%. Focus conservazione capitale.",
        "VOLATILITY MIX": "Copre 1, 2, 5. Bilanciamento costante.",
        "THE GRINDER": "Punta su '1' + Tutti i Bonus.",
        "ANTI-VARIANCE": "80% su '2', 20% su Bonus.",
        "CONSERVATIVE": "Numeri alti (5-10) pagano i Bonus."
    },
    "RISKY": {
        "BONUS HUNTER": "Solo Bonus Game. Volatilità massima.",
        "CRAZY MAX": "Focus Crazy Time + Pachinko.",
        "TOP SLOT AGG.": "Puntata su '10' + Cash Hunt.",
        "GAMBLER CHOICE": "Solo Coin Flip + Crazy Time.",
        "ALL-IN BONUS": "Puntata pesante solo su 4 Bonus."
    }
}

# --- INITIALIZATION ---
if 'expert_data' not in st.session_state: st.session_state['expert_data'] = []
if 'gold_list' not in st.session_state: st.session_state['gold_list'] = load_gold()

# --- SIDEBAR MASTER ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 1.5rem;'>SYSTEM_V26</h1>", unsafe_allow_html=True)
    st.markdown("<div class='status-dot'></div> <span style='font-size:0.8rem;'>CORE ACTIVE</span>", unsafe_allow_html=True)
    st.divider()
    bankroll = st.number_input("BANKROLL (€)", value=500.0)
    module = st.radio("SELECT ENGINE", ["SPORTS_BETTING", "CASINO_STRATEGIES"])
    
    st.divider()
    if module == "SPORTS_BETTING":
        st.subheader("STRATEGIES")
        if st.button("LOAD SAFE ELITE"):
            st.session_state['expert_data'] = [
                {"Match": "Juventus v Fiorentina", "Tip": "1X + U3.5", "Odds": 1.50, "Lega": "SERIE A"},
                {"Match": "Liverpool v Everton", "Tip": "Over 2.5", "Odds": 1.62, "Lega": "PREMIER"},
                {"Match": "Real Madrid v Villarreal", "Tip": "Segno 1", "Odds": 1.45, "Lega": "LA LIGA"},
                {"Match": "Leverkusen v Leipzig", "Tip": "Goal", "Odds": 1.55, "Lega": "BUNDESLIGA"}
            ]
            st.session_state['mode_name'] = "SAFE"
        
        if st.button("LOAD TARGET 100"):
            st.session_state['expert_data'] = [
                {"Match": "Bologna v Inter", "Tip": "X", "Odds": 3.60, "Lega": "SERIE A"},
                {"Match": "Newcastle v Man Utd", "Tip": "2 + Goal", "Odds": 4.80, "Lega": "PREMIER"},
                {"Match": "Bilbao v Atl. Madrid", "Tip": "1 + U2.5", "Odds": 4.20, "Lega": "LA LIGA"},
                {"Match": "Dortmund v Stuttgart", "Tip": "O3.5 + Goal", "Odds": 3.20, "Lega": "BUNDESLIGA"},
                {"Match": "Marseille v Nice", "Tip": "X + U2.5", "Odds": 3.50, "Lega": "LIGUE 1"}
            ]
            st.session_state['mode_name'] = "RISK"
            
        st.divider()
        st.subheader("GOLD TIP")
        g_m = st.text_input("MATCH")
        g_t = st.text_input("TIP")
        g_o = st.number_input("ODDS", value=1.50)
        if st.button("SAVE GOLD"):
            if g_m and g_t:
                st.session_state['gold_list'].append({"Match": g_m, "Tip": g_t, "Odds": g_o})
                save_gold(st.session_state['gold_list'])
                st.rerun()
    
    if st.button("RESET ALL DATA"):
        if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
        st.session_state.clear()
        st.rerun()

# --- MAIN ENGINE ---
col_main, col_ticket = st.columns([2, 1], gap="large")

if module == "SPORTS_BETTING":
    with col_main:
        st.markdown("<p class='sub-text'>Real-Time Market Analysis</p>", unsafe_allow_html=True)
        st.title("SPORTS_ANALYSIS")
        
        if st.session_state['gold_list']:
            for g in st.session_state['gold_list']:
                st.markdown(f"<div class='gold-card'>{g['Match']} // {g['Tip']} @{g['Odds']}</div>", unsafe_allow_html=True)

        if st.session_state['expert_data']:
            for m in st.session_state['expert_data']:
                st.markdown(f"""
                    <div class="match-card">
                        <span class="sub-text">{m['Lega']}</span><br>
                        <b style="font-size:1.1rem;">{m['Match']}</b><br>
                        <span style="opacity:0.8;">{m['Tip']} // @{m['Odds']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No strategies loaded. Use the sidebar to initiate.")

    with col_ticket:
        st.subheader("TICKET_SUMMARY")
        combined = st.session_state['expert_data'] + st.session_state['gold_list']
        if combined:
            total_odds = 1.0
            for m in combined: total_odds *= m['Odds']
            stake = round(bankroll * (0.08 if st.session_state.get('mode_name')=="SAFE" else 0.02), 2)
            
            st.markdown(f"""
                <div class='match-card' style='background:rgba(255,255,255,0.03) !important;'>
                    <p class='sub-text'>Combined Odds</p><h2>{total_odds:.2f}</h2>
                    <p class='sub-text'>Stake Advisable</p><h3>€{stake}</h3>
                    <p class='sub-text'>Est. Return</p><h2 style="color:#FFF;">€{round(total_odds * stake, 2)}</h2>
                </div>
            """, unsafe_allow_html=True)
            st.download_button("EXPORT TICKET", "Ticket Data Here", file_name="ticket.txt")
        else:
            st.write("Ticket empty.")

else: # MODULE CASINO
    with col_main:
        st.markdown("<p class='sub-text'>Probability Engines</p>", unsafe_allow_html=True)
        st.title("CASINO_STRATEGIES")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### // SAFE")
            for name, desc in STRATEGIES_CASINO["SAFE"].items():
                st.markdown(f"<div class='strategy-card'><b>{name}</b><br><small style='color:#888;'>{desc}</small></div>", unsafe_allow_html=True)
                if st.button(f"SELECT {name}"): st.toast(f"Stake: €{round(bankroll*0.05,2)}")
        with c2:
            st.markdown("### // RISKY")
            for name, desc in STRATEGIES_CASINO["RISKY"].items():
                st.markdown(f"<div class='strategy-card' style='border-left:3px solid #666;'><b>{name}</b><br><small style='color:#888;'>{desc}</small></div>", unsafe_allow_html=True)
                if st.button(f"SELECT {name}", key=name+"_btn"): st.toast(f"Stake: €{round(bankroll*0.02,2)}")
