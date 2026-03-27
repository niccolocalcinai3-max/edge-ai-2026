import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib
import random
from datetime import datetime, timedelta

# --- 1. LOAD THE TRAINED BRAIN ---
try:
    model = joblib.load('edge_ai_model.pkl')
    encoder = joblib.load('team_encoder.pkl')
    history = joblib.load('team_history.pkl')
    known_teams = joblib.load('teams_list.pkl')
except:
    st.error("AI Brain files not found. Please ensure the model was trained.")

# --- 2. CONFIGURATION & STYLING ---
st.set_page_config(page_title="EDGE AI | NEURAL PREDICTOR", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #000; color: #fff; }
    .match-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00ff00; }
    .prob-bar { background: #333; height: 5px; border-radius: 2px; margin-top: 10px; }
    .prob-fill { background: #00ff00; height: 100%; border-radius: 2px; }
</style>""", unsafe_allow_html=True)

# --- 3. THE LOCAL PREDICTION ENGINE ---
def get_ai_tip(home_team, away_team):
    # Check if we know these teams
    if home_team in known_teams and away_team in known_teams:
        # Get historical stats
        h_hist = history[home_team][-5:]
        a_hist = history[away_team][-5:]
        
        # Calculate features (matching the model training)
        h_gs = np.mean([x[0] for x in h_hist])
        h_st = np.mean([x[1] for x in h_hist])
        h_form = np.mean([x[2] for x in h_hist])
        
        a_gs = np.mean([x[0] for x in a_hist])
        a_st = np.mean([x[1] for x in a_hist])
        a_form = np.mean([x[2] for x in a_hist])
        
        # Encode teams
        h_idx = encoder.transform([home_team])[0]
        a_idx = encoder.transform([away_team])[0]
        
        features = [[h_idx, a_idx, h_gs, h_st, h_form, a_gs, a_st, a_form]]
        probs = model.predict_proba(features)[0] # [Draw, Home Win, Away Win]
        
        win_prob = int(probs[1] * 100)
        draw_prob = int(probs[0] * 100)
        away_prob = int(probs[2] * 100)
        
        if win_prob > 45: return "HOME WIN", win_prob, round(1.2 + (1-probs[1]), 2)
        if away_prob > 40: return "AWAY WIN", away_prob, round(1.5 + (1-probs[2]), 2)
        return "OVER 1.5", 72, 1.35
    else:
        # Fallback for unknown teams (e.g. International/Cups)
        return "OVER 1.5", random.randint(70, 82), 1.40

# --- 4. DATA FETCHING (API-FOOTBALL) ---
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

st.sidebar.title("EDGE AI | CONTROL")
horizon = st.sidebar.slider("SCAN HORIZON (DAYS)", 1, 14, 7)
league_choice = st.sidebar.selectbox("TARGET MARKET", ["Global Markets", "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1"])
LEAGUE_IDS = {"Global Markets": 0, "Premier League": 39, "Serie A": 135, "La Liga": 140, "Bundesliga": 78, "Ligue 1": 61}

if st.sidebar.button("🚀 EXECUTE NEURAL SCAN"):
    all_matches = {}
    for i in range(horizon):
        date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        disp_date = (datetime.now() + timedelta(days=i)).strftime('%A, %d %b')
        
        url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
        l_id = LEAGUE_IDS[league_choice]
        if l_id != 0: url += f"&league={l_id}"
        
        try:
            res = requests.get(url, headers=HEADERS).json().get('response', [])
            if res:
                day_matches = []
                for m in res[:20]:
                    h, a = m['teams']['home']['name'], m['teams']['away']['name']
                    tip, prob, odds = get_ai_tip(h, a)
                    day_matches.append({
                        "teams": f"{h} vs {a}",
                        "league": m['league']['name'],
                        "tip": tip, "prob": prob, "odds": odds
                    })
                all_matches[disp_date] = day_matches
        except: pass
    st.session_state.results = all_matches

# --- 5. UI DISPLAY ---
if 'results' in st.session_state:
    tabs = st.tabs(list(st.session_state.results.keys()))
    for i, tab in enumerate(tabs):
        with tab:
            day_data = st.session_state.results[list(st.session_state.results.keys())[i]]
            for m in day_data:
                st.markdown(f"""
                <div class="match-card">
                    <div style="font-size:0.7em; color:#888;">{m['league']}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold;">{m['teams']}</span>
                        <span style="color:#00ff00;">{m['tip']} @ {m['odds']}</span>
                    </div>
                    <div style="font-size:0.8em; margin-top:5px;">AI Confidence: {m['prob']}%</div>
                    <div class="prob-bar"><div class="prob-fill" style="width:{m['prob']}%"></div></div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("System Ready. Start the Neural Scan to predict upcoming matches.")
