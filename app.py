import streamlit as st
import requests
import random
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="EDGE AI | PRO DASHBOARD", layout="wide")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"
HEADERS = {'x-apisports-key': API_KEY}

st.markdown("""
    <style>
    .main { background-color: #050505; color: #eee; }
    .stat-card { border: 1px solid #222; padding: 15px; border-radius: 10px; background-color: #0a0a0a; margin-bottom: 15px; }
    .ticket-active { background: linear-gradient(135deg, #004d00 0%, #001a00 100%); padding: 20px; border-radius: 10px; border: 1px solid #00ff00; }
    .copy-btn { background-color: #111; border: 1px solid #333; color: #00ff00; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    u = st.text_input("Identity"); p = st.text_input("Key", type="password")
    if st.button("AUTHORIZE"):
        if u == "admin" and p == "edge2026": 
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- 3. ANALYTICS ENGINE ---
def get_deep_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
    try:
        res = requests.get(url, headers=HEADERS).json().get('response', [])
        if res:
            d = res[0]
            comp = d.get('comparison', {})
            h_att = comp.get('att', '50%').replace('%','')
            a_att = comp.get('att', '50%').replace('%','')
            h_form = d.get('teams', {}).get('home', {}).get('league', {}).get('form', '-----')
            a_form = d.get('teams', {}).get('away', {}).get('league', {}).get('form', '-----')
            
            # Decide Tip based on Attacking Strength
            if int(h_att) > 60: tip = "Home Team Over 0.5 Goals"
            elif int(a_att) > 60: tip = "Away Team Over 0.5 Goals"
            else: tip = "Over 1.5 Match Goals"
            
            return {
                "tip": tip, "odds": round(random.uniform(1.3, 1.7), 2),
                "h_att": h_att, "a_att": a_att, "h_form": h_form, "a_form": a_form
            }
    except: return None

# --- 4. SIDEBAR SETTINGS ---
st.sidebar.title("💎 EDGE AI CONTROL")
stake = st.sidebar.number_input("STAKE (€)", value=2.0)
target = st.sidebar.number_input("TARGET (€)", value=20.0)
pool = st.sidebar.slider("SCAN DEPTH", 10, 50, 25)
st.sidebar.markdown("---")

# --- 5. MAIN EXECUTION ---
if st.sidebar.button("🚀 INITIATE ANALYSIS"):
    with st.spinner("Processing Historical Data..."):
        f_url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        fixtures = requests.get(f_url, headers=HEADERS).json().get('response', [])
        
        analysis_results = []
        for m in fixtures[:pool]:
            s = get_deep_stats(m['fixture']['id'])
            if s:
                analysis_results.append({
                    "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                    "tip": s['tip'], "odds": s['odds'], 
                    "h_att": s['h_att'], "a_att": s['a_att'],
                    "h_form": s['h_form'], "a_form": s['a_form']
                })

        if analysis_results:
            col_stats, col_ticket = st.columns([2, 1])
            
            with col_stats:
                st.subheader("📊 Live Statistical Breakdown")
                for r in analysis_results:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div style="display: flex; justify-content: space-between;">
                            <b>{r['teams']}</b>
                            <span style="color: #00ff00;">Tip: {r['tip']}</span>
                        </div>
                        <div style="margin-top:10px; font-size: 0.8em; color: #888;">
                            Attack Power: Home {r['h_att']}% | Away {r['a_att']}% <br>
                            Recent Form: {r['h_form']} vs {r['a_form']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_ticket:
                st.subheader("🎟️ ACTIVE TICKET")
                req_odds = target / stake
                ticket_list = []
                c_odds = 1.0
                
                # Logic to build the ticket
                for r in sorted(analysis_results, key=lambda x: int(x['h_att']), reverse=True):
                    if c_odds < req_odds:
                        ticket_list.append(r)
                        c_odds *= r['odds']
                
                # Display the Active Ticket
                ticket_text = "✨ EDGE AI LUXURY TICKET ✨\n"
                with st.container():
                    st.markdown('<div class="ticket-active">', unsafe_allow_html=True)
                    for t in ticket_list:
                        match_str = f"⚽ {t['teams']}\n🔥 {t['tip']} (@{t['odds']})"
                        st.write(match_str)
                        ticket_text += f"\n{match_str}"
                    
                    st.markdown("---")
                    st.write(f"📊 **Total Odds: {c_odds:.2f}**")
                    st.write(f"💰 **Stake €{stake} ➡️ €{stake*c_odds:.2f}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    ticket_text += f"\n\n📊 Total Odds: {c_odds:.2f}\n💰 Win: €{stake*c_odds:.2f}\n🚀 Generated by Edge AI"
                
                # --- COPY BUTTON ---
                st.markdown("###")
                if st.button("📋 COPY TICKET TO CLIPBOARD"):
                    # Streamlit trick to "copy" via a text area or toast
                    st.code(ticket_text, language=None)
                    st.toast("Ticket copied! Paste it in Telegram/WhatsApp.")

        else:
            st.error("No matches found for analysis. Try again in 30 mins.")
