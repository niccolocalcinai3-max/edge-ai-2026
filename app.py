import streamlit as st
import requests
import random
import hashlib
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="EDGE AI | LUXURY 2026", layout="wide", initial_sidebar_state="expanded")
API_KEY = "0161ed129e075dbe7cab279cc96c7066"

# --- CSS LUXURY STYLING ---
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 2px; border: 1px solid #333; background-color: #000; color: white; height: 3em; }
    .stButton>button:hover { border: 1px solid #fff; background-color: #111; }
    .stTextInput>div>div>input { background-color: #0a0a0a; color: white; border: 1px solid #1a1a1a; }
    .ticket-card { border: 1px solid #111; padding: 15px; border-radius: 5px; margin-bottom: 10px; background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def check_login(u, p):
    # For web, you can connect this to a real database later. 
    # For now, let's use a "Master Key" approach.
    hashed_p = hashlib.sha256(p.encode()).hexdigest()
    if u == "admin" and p == "edge2026": # Change these for your launch
        return True
    return False

# --- UI: LOGIN SCREEN ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.title("E D G E  A I")
        st.caption("SECURE WEB GATEWAY")
        user = st.text_input("Identity")
        pw = st.text_input("Access Key", type="password")
        if st.button("AUTHORIZE"):
            if check_login(user, pw):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.info("Contact @badglocky on Discord for Access Keys")
    st.stop()

# --- UI: MAIN DASHBOARD ---
st.sidebar.title("EDGE AI / 2026")
st.sidebar.markdown("---")

# Sidebar Controls
stake = st.sidebar.number_input("STAKE (€)", min_value=1.0, value=2.0)
target = st.sidebar.number_input("TARGET (€)", min_value=2.0, value=20.0)
risk = st.sidebar.select_slider("RISK STRATEGY", options=["SAFE", "BALANCED", "AGGRESSIVE"], value="BALANCED")

if st.sidebar.button("GENERATE PRECISION TICKET"):
    with st.spinner("Scanning Global Markets..."):
        # API Call
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        try:
            res = requests.get(url, headers={'x-apisports-key': API_KEY}).json().get('response', [])
            matches = [{"teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}", 
                        "quote": round(random.uniform(1.3, 3.5), 2), 
                        "conf": random.randint(70, 99)} for m in res]
            
            # Logic Engine
            req_odds = target / stake
            if risk == "SAFE": matches = [m for m in matches if m['quote'] < 1.8]
            elif risk == "AGGRESSIVE": matches = [m for m in matches if m['quote'] > 2.2]
            
            random.shuffle(matches)
            ticket = []
            current_odds = 1.0
            for m in sorted(matches, key=lambda x: x['conf'], reverse=True):
                if current_odds < req_odds:
                    ticket.append(m)
                    current_odds *= m['quote']
                else: break
            
            st.session_state.current_ticket = ticket
            st.session_state.final_odds = current_odds
        except:
            st.error("Market API Timeout")

# --- MAIN DISPLAY AREA ---
col_intel, col_ticket = st.columns([2, 1])

with col_intel:
    st.subheader("Market Intelligence")
    st.write("Live Data Feed Active ●")
    # Display mock live matches or real feed
    for i in range(5):
        st.markdown(f"<div class='ticket-card'>Live Match {i+1} | Analytics Pending...</div>", unsafe_allow_html=True)

with col_ticket:
    st.subheader("Active Ticket")
    if 'current_ticket' in st.session_state:
        for m in st.session_state.current_ticket:
            st.markdown(f"""
            <div style='border-left: 3px solid #00FF00; padding-left: 10px; margin-bottom: 15px;'>
                <b>{m['teams']}</b><br>
                <span style='color: #888;'>Odds: {m['quote']} | Confidence: {m['conf']}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        total_win = stake * st.session_state.final_odds
        st.markdown(f"### Total Odds: {st.session_state.final_odds:.2f}")
        st.success(f"Return: €{total_win:.2f}")
        
        # Share button for Mobile
        if st.button("📤 Copy Share Link"):
            st.toast("Link copied to clipboard!")
    else:
        st.info("Input stake & click Generate to begin.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: Admin")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()