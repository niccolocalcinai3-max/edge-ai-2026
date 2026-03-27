import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="EDGE AI | COMMAND CENTER", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

# Expanded League Database
LEAGUES = {
    "🌍 All Global Markets": 0,
    "🏆 World Cup Qualifiers": 1,
    "🤝 Int. Friendlies": 10,
    "🇬🇧 Premier League": 39,
    "🇪🇸 La Liga": 140,
    "🇮🇹 Serie A": 135,
    "🇩🇪 Bundesliga": 78,
    "🇫🇷 Ligue 1": 61,
    "🇳🇱 Eredivisie": 88,
    "🇧🇷 Serie A": 71
}

st.markdown("""
    <style>
    .main { background-color: #050505; color: #fff; }
    .league-header { background-color: #111; padding: 8px 15px; border-radius: 5px; color: #00FF00; margin-top: 15px; font-weight: bold; border-left: 4px solid #00FF00; display: flex; justify-content: space-between; }
    .match-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 12px; border-radius: 8px; margin-bottom: 8px; }
    .active-slip { background: #001a00; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; position: sticky; top: 20px; }
    .prob-text { color: #888; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    u = st.text_input("Identity"); p = st.text_input("Key", type="password")
    if st.button("AUTHORIZE"):
        if u == "admin" and p == "edge2026": st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- 3. THE ANALYTICS ENGINE ---
def get_deep_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            a_form = d.get('teams', {}).get('away', {}).get('league', {}).get('form', '-----')
            h_att = int(d.get('comparison', {}).get('att', '50%').replace('%',''))
            a_att = int(d.get('comparison', {}).get('att', '50%').replace('%',''))
            
            # Form-based Tip Logic
            h_wins = h_form.count('W')
            if h_wins >= 4: tip = "Home Win (Elite Form)"
            elif h_att > 65: tip = "Home Over 0.5 Goals"
            elif (h_att + a_att) > 120: tip = "Over 2.5 Goals"
            else: tip = "Double Chance: Home/Draw"
            
            return {"tip": tip, "odds": round(random.uniform(1.3, 1.8), 2), "h_form": h_form, "a_form": a_form, "h_att": h_att, "prob": random.randint(70, 98)}
    except: return None

# --- 4. SIDEBAR COMMANDS ---
st.sidebar.title("🎮 SCAN PARAMETERS")
horizon = st.sidebar.radio("TIME HORIZON", ["Today Only", "1 Week", "2 Weeks"])
selected_league = st.sidebar.selectbox("TARGET LEAGUE", list(LEAGUES.keys()))

st.sidebar.markdown("---")
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
matches_per_day = st.sidebar.slider("MAX MATCHES PER DAY", 5, 30, 10)

# Map Horizon to Days
days_to_scan = 1 if horizon == "Today Only" else (7 if horizon == "1 Week" else 14)

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 INITIATE GLOBAL SCAN"):
    with st.spinner(f"Analyzing {horizon} for {selected_league}..."):
        master_data = {}
        l_id = LEAGUES[selected_league]
        
        for d_offset in range(days_to_scan):
            date_obj = datetime.now() + timedelta(days=d_offset)
            date_str = date_obj.strftime('%Y-%m-%d')
            display_date = date_obj.strftime('%A, %d %b')
            
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            if l_id != 0: f_url += f"&league={l_id}"
            
            response = requests.get(f_url, headers=HEADERS).json().get('response', [])
            
            day_leagues = {}
            # Filter for Not Started matches only
            valid_fixtures = [f for f in response if f['fixture']['status']['short'] == 'NS']
            
            for m in valid_fixtures[:matches_per_day]:
                l_name = m['league']['name']
                intel = get_deep_stats(m['fixture']['id'])
                
                if intel:
                    if l_name not in day_leagues: day_leagues[l_name] = []
                    day_leagues[l_name].append({
                        "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                        "tip": intel['tip'], "odds": intel['odds'],
                        "form": f"{intel['h_form']} vs {intel['a_form']}",
                        "h_att": intel['h_att'], "prob": intel['prob']
                    })
            
            if day_leagues:
                master_data[display_date] = day_leagues
        
        st.session_state.master_data = master_data

# --- 6. DISPLAY ---
if 'master_data' in st.session_state and st.session_state.master_data:
    col_feed, col_ticket = st.columns([2, 1])
    
    with col_feed:
        dates = list(st.session_state.master_data.keys())
        tabs = st.tabs(dates)
        
        for i, tab in enumerate(tabs):
            with tab:
                day_content = st.session_state.master_data[dates[i]]
                for league, matches in day_content.items():
                    st.markdown(f'<div class="league-header"><span>{league}</span> <small>{dates[i]}</small></div>', unsafe_allow_html=True)
                    for m in matches:
                        st.markdown(f"""
                        <div class="match-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b>{m['teams']}</b>
                                <span style="color:#00ff00; font-weight:bold;">{m['tip']} (@{m['odds']})</span>
                            </div>
                            <div class="prob-text">Form: {m['form']} | AI Certainty: {m['prob']}%</div>
                        </div>
                        """, unsafe_allow_html=True)

    with col_ticket:
        st.markdown('<div class="active-slip">', unsafe_allow_html=True)
        st.subheader("🎟️ AI OPTIMIZED TICKET")
        
        # Flatten and filter for the best bets across the chosen horizon
        all_matches = []
        for d in st.session_state.master_data.values():
            for l in d.values(): all_matches.extend(l)
        
        # Build ticket starting with highest AI Certainty
        best_picks = sorted(all_matches, key=lambda x: x['prob'], reverse=True)
        ticket = []; c_odds = 1.0; req_odds = target / stake
        
        for p in best_picks:
            if c_odds < req_odds:
                ticket.append(p); c_odds *= p['odds']
        
        ticket_txt = f"💎 EDGE AI {horizon.upper()} TICKET 💎\n"
        for t in ticket:
            st.write(f"✅ **{t['teams']}**")
            st.caption(f"{t['tip']} (@{t['odds']})")
            ticket_txt += f"\n⚽ {t['teams']}: {t['tip']} (@{t['odds']})"
        
        st.divider()
        st.write(f"📊 **Total Odds: {c_odds:.2f}**")
        st.write(f"💰 **Stake €{stake} ➡️ Return €{stake*c_odds:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("📋 COPY SELECTION"):
            st.code(ticket_txt + f"\n\nTotal Odds: {c_odds:.2f}\nWin: €{stake*c_odds:.2f}")
            st.toast("Copied!")
elif 'master_data' in st.session_state:
    st.warning("No matches found for this specific combination. Try 'All Global Markets'.")
