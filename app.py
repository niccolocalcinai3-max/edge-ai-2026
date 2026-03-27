import streamlit as st
import requests
from datetime import datetime, timedelta

# --- CONFIG ---
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

LEAGUES = {
    "🌐 ALL ACTIVE (Recommended Now)": 0,
    "🏆 International Friendlies": 10,
    "🌍 WC Qualifiers": 1,
    "🇬🇧 Premier League": 39,
    "🇪🇸 La Liga": 140,
    "🇮🇹 Serie A": 135
}

st.sidebar.title("EDGE AI CONTROL")
mode = st.sidebar.radio("WINDOW", ["Today", "1 Week", "2 Weeks"])
target_league = st.sidebar.selectbox("LEAGUE", list(LEAGUES.keys()))

# --- THE FIX ---
def fetch_fixtures(date_str, league_id):
    url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
    if league_id != 0:
        url += f"&league={league_id}"
    
    try:
        response = requests.get(url, headers=HEADERS).json()
        fixtures = response.get('response', [])
        # If specific league is empty, but user didn't pick "All", warn them
        return fixtures
    except:
        return []

if st.sidebar.button("RUN DEEP SCAN"):
    days = 1 if mode == "Today" else (7 if mode == "1 Week" else 14)
    l_id = LEAGUES[target_league]
    
    st.write(f"### 📊 Results for {target_league} ({mode})")
    
    found_any = False
    for i in range(days):
        scan_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        data = fetch_fixtures(scan_date, l_id)
        
        if data:
            found_any = True
            with st.expander(f"Matches for {scan_date}"):
                for m in data[:15]: # Limit to top 15 per day
                    st.write(f"⚽ **{m['teams']['home']['name']} vs {m['teams']['away']['name']}**")
                    st.caption(f"League: {m['league']['name']} | Status: {m['fixture']['status']['long']}")
        
    if not found_any:
        st.error(f"Zero matches found for {target_league}. NOTE: Major European leagues are currently on International Break until April 3-10.")
        st.info("💡 **Switch to 'ALL ACTIVE' or 'International Friendlies' to see today's big games like Spain vs Serbia!**")
