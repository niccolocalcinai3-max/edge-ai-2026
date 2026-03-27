import streamlit as st
import requests
from datetime import datetime, timedelta

# --- 1. CONFIG ---
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

# Updated to include the IDs that are ACTIVE right now
LEAGUES = {
    "🌐 ALL ACTIVE": 0,
    "🏆 International Friendlies": 10,
    "🌍 World Cup Qualifiers": 1,
    "🇬🇧 Premier League (Resumes April)": 39,
    "🇪🇸 La Liga (Resumes April)": 140
}

# --- 2. THE SMART SCANNER ---
def force_fetch(date_str, league_id):
    url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
    if league_id != 0:
        url += f"&league={league_id}"
    
    res = requests.get(url, headers=HEADERS).json().get('response', [])
    
    # FALLBACK: If your specific league is empty, try International Friendlies
    if not res and league_id != 10:
        st.info(f"No matches in selected league. Checking International Friendlies instead...")
        fallback_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}&league=10"
        res = requests.get(fallback_url, headers=HEADERS).json().get('response', [])
    return res

# --- 3. UI ---
st.title("EDGE AI | 24/7 FIXTURE FINDER")
mode = st.radio("TIME WINDOW", ["Today", "1 Week", "2 Weeks"])
choice = st.selectbox("LEAGUE", list(LEAGUES.keys()))

if st.button("EXECUTE SCAN"):
    days = 1 if mode == "Today" else (7 if mode == "1 Week" else 14)
    found_count = 0
    
    for i in range(days):
        date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        matches = force_fetch(date_str, LEAGUES[choice])
        
        if matches:
            found_count += len(matches)
            with st.expander(f"📅 {date_str} - {len(matches)} Matches"):
                for m in matches[:10]:
                    st.write(f"⚽ **{m['teams']['home']['name']} vs {m['teams']['away']['name']}**")
                    st.caption(f"League: {m['league']['name']} | Kickoff: {m['fixture']['date'][11:16]}")
    
    if found_count == 0:
        st.error("Still nothing. This usually means your API Key has hit its daily limit.")
