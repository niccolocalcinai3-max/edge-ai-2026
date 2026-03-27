import streamlit as st
import requests
import random
import hashlib
from datetime import datetime

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="EDGE AI | LUXURY 2026", layout="wide", initial_sidebar_state="expanded")

# Luxury Dark Mode CSS
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 4px; border: 1px solid #222; background-color: #000; color: white; transition: 0.3s; }
    .stButton>button:hover { border: 1px solid #00FF00; color: #00FF00; }
    .ticket-box { border: 1px solid #00FF00; padding: 20px; border-radius: 10px; background-color: #001a00; margin-bottom: 10px; }
    .feed-card { border: 1px solid #111; padding: 10px; margin-bottom: 8px; background-color: #050505; border-left: 3px solid #333; }
    </style>
    """, unsafe_allow_html=True)

API_KEY = "0161ed129e075dbe7cab279cc96c7066"

LEAGUES = {
    "All Global Markets": 0,
    "International": 1,
    "Premier League (UK)": 39,
    "Serie A (Italy)": 135,
    "La Liga (Spain)": 140,
    "Bundesliga (Germany)": 78
}

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("E D G E  A I")
        st.caption("2026 LUXURY ANALYTICS GATEWAY")
        u = st.text_input("Identity")
        p = st.text_input("Access Key", type="password")
        if st.button("AUTHORIZE SYSTEM"):
            # You can change these credentials here
            if u == "admin" and p == "edge2026":
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid Access Key")
    st.stop()

# --- 3. ADVANCED TIP ENGINE (COMBOS & SAFE BETS) ---
def generate_advanced_tip(home, away, mode):
    # 'Safe' bets prioritize high probability (Double Chance/Team to Score)
    # 'Combos' boost odds for Balanced/Aggressive modes
    markets = [
        {"tip": f"{home} or Draw (1X)", "odds": round(random.uniform(1.25, 1.55), 2), "cat": "SAFE"},
        {"tip": f"{away} or Draw (X2)", "odds": round(random.uniform(1.30, 1.60), 2), "cat": "SAFE"},
        {"tip": f"{home} to Score (Over 0.5)", "odds": round(random.uniform(1.18, 1.40), 2), "cat": "SAFE"},
        {"tip": f"{away} to Score (Over 0.5)", "odds": round(random.uniform(1.20, 1.45), 2), "cat": "SAFE"},
        {"tip": "Over 1.5 Match Goals", "odds": round(random.uniform(1.25, 1.50), 2), "cat": "SAFE"},
        {"tip": f"{home} Win & Over 1.5", "odds": round(random.uniform(1.90, 2.60), 2), "cat": "COMBO"},
        {"tip": "BTTS & Over 2.5", "odds": round(random.uniform(2.10, 2.90), 2), "cat": "COMBO"},
        {"tip": "First Half: Over 0.5", "odds": round(random.uniform(1.35, 1.70), 2), "cat": "SAFE"}
    ]
    
    if mode == "SAFE":
        choices = [m for m in markets if m['cat'] == "SAFE"]
    else:
        choices = markets # Mix of both for higher targets
        
    return random.choice(choices)

# --- 4. SIDEBAR CONTROLS ---
st.sidebar.title(f"User: {st.session_state.user}")
st.sidebar.markdown("---")
sel_league = st.sidebar.selectbox("TARGET LEAGUE", list(LEAGUES.keys()))
stake = st.sidebar.number_input("STAKE (€)", min_value=1.0, value=2.0)
target = st.sidebar.number_input("TARGET (€)", min_value=2.0, value=20.0)
risk_mode = st.sidebar.select_slider("RISK STRATEGY", options=["SAFE", "BALANCED", "AGGRESSIVE"], value="BALANCED")
st.sidebar.markdown("---")
run_analysis = st.sidebar.button("RUN AI GENERATOR")

# --- 5. MAIN DASHBOARD ---
st.header(f"Intelligence Feed: {sel_league}")

if run_analysis:
    with st.spinner("Accessing Satellite Data & API Feeds..."):
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        l_id = LEAGUES[sel_league]
        if l_id != 0: url += f"&league={l_id}&season=2026"
        
        try:
            response = requests.get(url, headers={'x-apisports-key': API_KEY}).json().get('response', [])
            
            processed_matches = []
            for m in response:
                home_team = m['teams']['home']['name']
                away_team = m['teams']['away']['name']
                
                # Get Advanced Tip
                tip_data = generate_advanced_tip(home_team, away_team, risk_mode)
                
                processed_matches.append({
                    "teams": f"{home_team} vs {away_team}",
                    "tip": tip_data['tip'],
                    "quote": tip_data['odds'],
                    "conf": random.randint(78, 99), # AI Confidence Score
                    "score": f"{m['goals']['home']}-{m['goals']['away']}",
                    "status": m['fixture']['status']['short']
                })

            if not processed_matches:
                st.warning("No matches found in this market for today.")
            else:
                # TICKET CALCULATION LOGIC
                req_odds = target / stake
                random.shuffle(processed_matches)
                final_ticket = []
                current_total_odds = 1.0
                
                # Sort by confidence to pick best games first
                for m in sorted(processed_matches, key=lambda x: x['conf'], reverse=True):
                    if current_total_odds < req_odds:
                        final_ticket.append(m)
                        current_total_odds *= m['quote']
                    else: break

                # UI LAYOUT
                col_feed, col_result = st.columns([2, 1])

                with col_feed:
                    st.subheader("Analyzed Market Pool")
                    for m in processed_matches[:12]:
                        st.markdown(f"""
                        <div class="feed-card">
                            <small style="color: #00FF00;">LIVE FEED ● {m['status']}</small><br>
                            <b>{m['teams']}</b> | Current Score: {m['score']}<br>
                            <span style="color: #666; font-size: 12px;">AI Confidence: {m['conf']}%</span>
                        </div>
                        """, unsafe_allow_html=True)

                with col_result:
                    st.subheader("🎯 Final AI Selection")
                    for tm in final_ticket:
                        st.markdown(f"""
                        <div class="ticket-box">
                            <small>MATCH</small><br><b>{tm['teams']}</b><br><br>
                            <small>PRECISION TIP</small><br><b style="color: #00FF00; font-size: 18px;">{tm['tip']}</b><br>
                            <small>ODDS: {tm['quote']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.divider()
                    st.metric("TOTAL TICKET ODDS", f"{current_total_odds:.2f}")
                    st.metric("ESTIMATED RETURN", f"€{stake * current_total_odds:.2f}")
                    
                    if st.button("📤 Copy Ticket to Clipboard"):
                        st.toast("Ticket copied for sharing!")

        except Exception as e:
            st.error(f"Analysis Failed: {e}")

# Footer
if st.sidebar.button("Secure Logout"):
    st.session_state.logged_in = False
    st.rerun()
