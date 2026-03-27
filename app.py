import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="EDGE AI | WEEKLY PRO", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

st.markdown("""
    <style>
    .main { background-color: #050505; color: #fff; }
    .day-header { color: #00FF00; border-bottom: 1px solid #222; padding-bottom: 5px; margin-top: 20px; }
    .match-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .active-slip { background: #001a00; border: 2px solid #00ff00; padding: 20px; border-radius: 10px; position: sticky; top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    u = st.text_input("Identity"); p = st.text_input("Key", type="password")
    if st.button("AUTHORIZE"):
        if u == "admin" and p == "edge2026": st.session_state.logged_in = True; st.rerun()
    st.stop()

# --- 3. ANALYTICS ENGINE ---
def get_match_intel(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            a_form = d.get('teams', {}).get('away', {}).get('league', {}).get('form', '-----')
            h_att = d.get('comparison', {}).get('att', '50%').replace('%','')
            
            # Logic: If Home Attack > 60%, Home scores. Else, Over 1.5.
            tip = "Home Over 0.5" if int(h_att) > 60 else "Match Over 1.5"
            return {"tip": tip, "odds": round(random.uniform(1.3, 1.6), 2), "h_form": h_form, "a_form": a_form, "h_att": h_att}
    except: return None

# --- 4. SIDEBAR CONTROLS ---
st.sidebar.title("🗓️ WEEKLY PLANNER")
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
scan_limit = st.sidebar.slider("MATCHES PER DAY", 5, 20, 10)

# --- 5. MAIN DASHBOARD ---
st.title("🎯 EDGE AI Intelligence Hub")

# Create Tabs for the next 7 Days
day_names = [(datetime.now() + timedelta(days=i)).strftime('%A (%d %b)') for i in range(7)]
tabs = st.tabs(day_names)

all_weekly_data = {}

# Button to Trigger Global Scan
if st.sidebar.button("🚀 SCAN FULL WEEK"):
    with st.spinner("Analyzing 7-Day Market Data..."):
        for i in range(7):
            date_str = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date_str}"
            fixtures = requests.get(f_url, headers=HEADERS).json().get('response', [])
            
            day_matches = []
            for m in fixtures[:scan_limit]:
                intel = get_match_intel(m['fixture']['id'])
                if intel:
                    day_matches.append({
                        "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                        "tip": intel['tip'],
                        "odds": intel['odds'],
                        "form": f"{intel['h_form']} vs {intel['a_form']}",
                        "h_att": intel['h_att']
                    })
            all_weekly_data[day_names[i]] = day_matches
        st.session_state.weekly_data = all_weekly_data

# Display Data in Tabs
if 'weekly_data' in st.session_state:
    col_main, col_slip = st.columns([2, 1])
    
    with col_main:
        for i, tab in enumerate(tabs):
            with tab:
                day_data = st.session_state.weekly_data.get(day_names[i], [])
                if not day_data:
                    st.info("No major matches processed for this day yet.")
                for m in day_data:
                    st.markdown(f"""
                    <div class="match-card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>{m['teams']}</b>
                            <span style="color:#00ff00;">{m['tip']} (@{m['odds']})</span>
                        </div>
                        <small style="color:#666;">Stats: {m['form']} | Att: {m['h_att']}%</small>
                    </div>
                    """, unsafe_allow_html=True)

    with col_slip:
        st.markdown('<div class="active-slip">', unsafe_allow_html=True)
        st.subheader("🎟️ ACTIVE TICKET")
        
        # Build Ticket from TODAY'S matches (Index 0)
        today_matches = st.session_state.weekly_data.get(day_names[0], [])
        req_odds = target / stake
        ticket = []
        c_odds = 1.0
        
        for m in sorted(today_matches, key=lambda x: int(x['h_att']), reverse=True):
            if c_odds < req_odds:
                ticket.append(m)
                c_odds *= m['odds']
        
        ticket_copy = "💎 EDGE AI WEEKLY SELECTION 💎\n"
        for t in ticket:
            st.write(f"✅ {t['teams']}\nBet: {t['tip']} (@{t['odds']})")
            ticket_copy += f"\n⚽ {t['teams']} -> {t['tip']} (@{t['odds']})"
        
        st.divider()
        st.write(f"**Total Odds: {c_odds:.2f}**")
        st.write(f"**Potential Win: €{stake * c_odds:.2f}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        ticket_copy += f"\n\n📊 Total Odds: {c_odds:.2f}\n💰 Return: €{stake*c_odds:.2f}"
        if st.button("📋 COPY SELECTION"):
            st.code(ticket_copy)
            st.toast("Copied!")
else:
    st.warning("Click 'SCAN FULL WEEK' to load the intelligence feed.")
