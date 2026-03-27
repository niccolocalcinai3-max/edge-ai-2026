import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="EDGE AI | GLOBAL LEAGUE", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

# League Database (Re-added)
LEAGUES = {
    "🌍 All Global Markets": 0,
    "🇬🇧 Premier League": 39,
    "🇮🇹 Serie A": 135,
    "🇪🇸 La Liga": 140,
    "🇩🇪 Bundesliga": 78,
    "🇫🇷 Ligue 1": 61,
    "🇳🇱 Eredivisie": 88,
    "🇧🇷 Serie A (Brazil)": 71
}

st.markdown("""
    <style>
    .main { background-color: #050505; color: #fff; }
    .match-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #333; }
    .active-slip { background: #001a00; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; position: sticky; top: 20px; }
    .badge-high { background-color: #00ff00; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("E D G E  A I")
        u = st.text_input("Identity"); p = st.text_input("Key", type="password")
        if st.button("AUTHORIZE"):
            if u == "admin" and p == "edge2026": st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- 3. DEEP ANALYTICS ENGINE ---
def get_match_intel(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            a_form = d.get('teams', {}).get('away', {}).get('league', {}).get('form', '-----')
            h_att = d.get('comparison', {}).get('att', '50%').replace('%','')
            
            # Badge Logic: If Home team won 4/5 or 5/5
            is_high_value = h_form.count('W') >= 4
            
            # Smart Tip based on real stats
            if int(h_att) > 65: tip = "Home Over 0.5 Goals"
            elif h_form.count('W') > a_form.count('W'): tip = "Double Chance: Home/Draw"
            else: tip = "Over 1.5 Match Goals"
            
            return {"tip": tip, "odds": round(random.uniform(1.3, 1.65), 2), "h_form": h_form, "a_form": a_form, "h_att": h_att, "high_val": is_high_value}
    except: return None

# --- 4. SIDEBAR CONTROLS ---
st.sidebar.title("🗓️ WEEKLY STRATEGIST")
target_league = st.sidebar.selectbox("CHOOSE LEAGUE", list(LEAGUES.keys()))
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
scan_limit = st.sidebar.slider("MATCHES PER DAY", 10, 50, 20)

# --- 5. MAIN DASHBOARD ---
day_names = [(datetime.now() + timedelta(days=i)).strftime('%A (%d %b)') for i in range(7)]
tabs = st.tabs(day_names)

if st.sidebar.button("🚀 EXECUTE GLOBAL SCAN"):
    with st.spinner(f"Scanning {target_league} for 7 days..."):
        all_weekly_data = {}
        l_id = LEAGUES[target_league]
        
        for i in range(7):
            date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            if l_id != 0: f_url += f"&league={l_id}&season=2026"
            
            fixtures = requests.get(f_url, headers=HEADERS).json().get('response', [])
            
            day_matches = []
            for m in fixtures[:scan_limit]:
                intel = get_match_intel(m['fixture']['id'])
                if intel:
                    day_matches.append({
                        "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                        "tip": intel['tip'], "odds": intel['odds'],
                        "form": f"{intel['h_form']} vs {intel['a_form']}",
                        "h_att": intel['h_att'], "high_val": intel['high_val']
                    })
            all_weekly_data[day_names[i]] = day_matches
        st.session_state.weekly_data = all_weekly_data

# Display Logic
if 'weekly_data' in st.session_state:
    col_main, col_slip = st.columns([2, 1])
    
    with col_main:
        for i, tab in enumerate(tabs):
            with tab:
                day_data = st.session_state.weekly_data.get(day_names[i], [])
                if not day_data:
                    st.warning("No fixtures found for this league on this day.")
                for m in day_data:
                    badge = '<span class="badge-high">HIGH VALUE</span>' if m['high_val'] else ""
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{m['teams']}</b> {badge}
                            <span style="color:#00ff00;">{m['tip']} (@{m['odds']})</span>
                        </div>
                        <small style="color:#666;">Form: {m['form']} | Att Power: {m['h_att']}%</small>
                    </div>
                    """, unsafe_allow_html=True)

    with col_slip:
        st.markdown('<div class="active-slip">', unsafe_allow_html=True)
        st.subheader("🎟️ ACTIVE TICKET")
        
        # Build Ticket from selected Tab (or default to Today)
        current_matches = st.session_state.weekly_data.get(day_names[0], [])
        req_odds = target / stake
        ticket = []; c_odds = 1.0
        
        for m in sorted(current_matches, key=lambda x: int(x['h_att']), reverse=True):
            if c_odds < req_odds:
                ticket.append(m); c_odds *= m['odds']
        
        ticket_copy = "💎 EDGE AI SELECTION 💎\n"
        for t in ticket:
            st.write(f"✅ {t['teams']}\nBet: {t['tip']} (@{t['odds']})")
            ticket_copy += f"\n⚽ {t['teams']} -> {t['tip']} (@{t['odds']})"
        
        st.divider()
        st.write(f"**Total Odds: {c_odds:.2f}**")
        st.write(f"**Potential Win: €{stake * c_odds:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("📋 COPY TICKET"):
            st.code(ticket_copy + f"\n\n📊 Total Odds: {c_odds:.2f}\n💰 Return: €{stake*c_odds:.2f}")
            st.toast("Copied!")
else:
    st.info("Select a League and click 'EXECUTE GLOBAL SCAN' to populate the 7-day feed.")
