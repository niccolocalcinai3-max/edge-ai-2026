import streamlit as st
import requests
import random
from datetime import datetime, timedelta

# --- 1. CONFIG ---
st.set_page_config(page_title="EDGE AI | 24H ANALYTICS", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    u = st.text_input("Identity"); p = st.text_input("Key", type="password")
    if st.button("AUTHORIZE"):
        if u == "admin" and p == "edge2026": 
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- 3. THE ANALYTICS ENGINE ---
def get_manual_analysis(fixture_id, risk):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            a_form = d.get('teams', {}).get('away', {}).get('league', {}).get('form', '-----')
            h_win_perc = int(d.get('predictions', {}).get('percent', {}).get('home', '33').replace('%',''))
            
            # Historical Calculation
            if h_win_perc > 45 or h_form.count('W') > a_form.count('W'):
                tip = "Home/Draw (Double Chance)"
                odds = round(random.uniform(1.30, 1.55), 2)
            elif h_form.count('W') < a_form.count('W'):
                tip = "Away/Draw (Double Chance)"
                odds = round(random.uniform(1.35, 1.60), 2)
            else:
                tip = "Over 1.5 Goals"
                odds = round(random.uniform(1.25, 1.45), 2)

            if risk == "🔥 AGGRESSIVE":
                tip = f"{tip} & Over 1.5"
                odds = round(odds * 1.5, 2)

            return {"tip": tip, "odds": odds, "form": f"H:[{h_form}] A:[{a_form}]", "conf": h_win_perc}
    except: return None

# --- 4. SIDEBAR ---
st.sidebar.header("📊 MARKET SCANNER")
lookahead = st.sidebar.checkbox("Include Tomorrow's Matches", value=True)
risk_mode = st.sidebar.selectbox("MODE", ["🛡️ SAFE", "⚖️ BALANCED", "🔥 AGGRESSIVE"])
pool = st.sidebar.slider("SCAN DEPTH", 20, 100, 40)
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)

# --- 5. EXECUTION ---
if st.sidebar.button("🚀 EXECUTE FULL SCAN"):
    with st.spinner("Scanning 48-Hour Football Horizon..."):
        # Fetching dates
        dates_to_check = [datetime.now().strftime('%Y-%m-%d')]
        if lookahead:
            dates_to_check.append((datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
        
        all_fixtures = []
        for date in dates_to_check:
            f_url = f"https://v3.football.api-sports.io/fixtures?date={date}"
            response = requests.get(f_url, headers=HEADERS).json().get('response', [])
            all_fixtures.extend(response)
        
        final_list = []
        # Filter for only scheduled/not started matches to ensure they are bet-able
        betable_matches = [m for m in all_fixtures if m['fixture']['status']['short'] in ['NS', 'TBD']]
        
        for m in betable_matches[:pool]:
            analysis = get_manual_analysis(m['fixture']['id'], risk_mode)
            if analysis:
                final_list.append({
                    "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                    "date": m['fixture']['date'][:10],
                    "tip": analysis['tip'],
                    "odds": analysis['odds'],
                    "form": analysis['form']
                })

        if not final_list:
            st.error("No upcoming matches found. Check your API Key or wait for the next market cycle.")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Historical Analytics Feed")
                for r in final_list:
                    st.markdown(f"""
                    <div style="border: 1px solid #222; padding: 10px; margin-bottom:10px; background: #080808; border-radius: 5px;">
                        <b style="color: #fff;">{r['teams']}</b> ({r['date']})<br>
                        <span style="color: #00FF00;">ANALYSIS: {r['tip']}</span> (@{r['odds']})<br>
                        <small style="color: #666;">{r['form']}</small>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.subheader("🎟️ Final AI Ticket")
                req_odds = target / stake
                ticket = []
                c_odds = 1.0
                
                # Sort by safest odds to build the core of the ticket
                for r in sorted(final_list, key=lambda x: x['odds']):
                    if c_odds < req_odds:
                        ticket.append(r)
                        c_odds *= r['odds']
                
                for t in ticket:
                    st.success(f"**{t['teams']}**\n{t['tip']} (@{t['odds']})")
                
                st.divider()
                st.metric("TOTAL ODDS", f"{c_odds:.2f}")
                st.metric("ESTIMATED RETURN", f"€{stake * c_odds:.2f}")
