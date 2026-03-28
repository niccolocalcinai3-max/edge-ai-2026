import streamlit as st
import os

# --- CONFIGURAZIONE CORE ---
SAVE_FILE = "gold_storage.txt"
st.set_page_config(page_title="EDGE PRO CELESTIAL", layout="wide")

# --- BACKGROUND ANIMATO (STELLE BIANCHE) ---
st.markdown("""
    <canvas id="canvas"></canvas>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    #canvas {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1;
        background: #020202;
    }

    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
        color: #FFFFFF !important; 
    }

    /* Glass Cards Premium */
    .match-card, .strategy-card {
        background: rgba(10, 10, 10, 0.7) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 25px;
        margin-bottom: 15px;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    .match-card:hover, .strategy-card:hover {
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        background: rgba(20, 20, 20, 0.8) !important;
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.05);
    }

    .stButton>button {
        background: #FFFFFF !important;
        color: #000 !important;
        border-radius: 5px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 40px;
        transition: 0.3s !important;
    }

    .stButton>button:hover {
        letter-spacing: 1px;
        box-shadow: 0 0 15px #FFF;
    }

    .gold-card {
        background: #FFF;
        color: #000;
        padding: 15px;
        border-radius: 8px;
        font-weight: 800;
        margin-bottom: 15px;
    }

    .how-to-play {
        font-size: 0.8rem;
        color: #AAA;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }

    .sub-text { color: #555; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
    </style>

    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    let stars = [];
    class Star {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2;
            this.speed = Math.random() * 0.5 + 0.1;
        }
        update() {
            this.y += this.speed;
            if (this.y > canvas.height) { this.y = 0; this.x = Math.random() * canvas.width; }
        }
        draw() {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
        }
    }
    function init() { for (let i = 0; i < 150; i++) { stars.push(new Star()); } }
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(s => { s.update(); s.draw(); });
        requestAnimationFrame(animate);
    }
    init(); animate();
    </script>
    """, unsafe_allow_html=True)

# --- DATABASE CASINO (10 STRATEGIE CON SPIEGAZIONE) ---
STRATEGIES_CASINO = {
    "SAFE": {
        "SHIELD 1-2": {
            "desc": "Stabilità estrema contro perdite repentine.",
            "how": "Metti 4 unità sull'1 e 2 unità sul 2. Copri il 66% della ruota. Se esce l'1 pareggi, se esce il 2 guadagni."
        },
        "VOLATILITY MIX": {
            "desc": "Bilanciamento tra numeri bassi e medi.",
            "how": "3 unità sull'1, 2 unità sul 2, 1 unità sul 5. Obiettivo: incassi frequenti per durare ore."
        },
        "THE GRINDER": {
            "desc": "Protezione con paracadute sui Bonus.",
            "how": "5 unità sull'1 e 0.50 unità su ogni Bonus. L'1 paga le giocate dei bonus finché non colpisci il moltiplicatore."
        },
        "ANTI-VARIANCE": {
            "desc": "Sfrutta il segmento più frequente dopo l'1.",
            "how": "Punta forte sul 2 (80% stake) e dividi il resto sui bonus Cash Hunt e Coin Flip."
        },
        "THE TOWER": {
            "desc": "Copertura alta su numeri rari.",
            "how": "Dividi lo stake equamente tra 5 e 10. Se esce uno dei due, hai profitto per i successivi 5 giri di bonus."
        }
    },
    "RISKY": {
        "BONUS HUNTER": {
            "desc": "Caccia pura ai giochi Bonus.",
            "how": "Ignora i numeri. Punta 1 unità su Coin Flip, Pachinko, Cash Hunt e Crazy Time. Accetta i giri vuoti."
        },
        "CRAZY MAX": {
            "desc": "Punta tutto sul colpo grosso.",
            "how": "Punta solo su Crazy Time e Pachinko. Strategia aggressiva per chi cerca moltiplicatori sopra il 100x."
        },
        "TOP SLOT SNIPER": {
            "desc": "Scommessa sui segmenti a vincita alta.",
            "how": "Punta solo sul 10 e Cash Hunt. Questa combinazione beneficia spesso dei boost della Top Slot."
        },
        "COIN FLIP RUSH": {
            "desc": "Sfrutta il bonus più frequente.",
            "how": "Punta pesante sul Coin Flip (4 segmenti) e proteggi con una piccola scommessa sul 2."
        },
        "ULTRA DOUBLE": {
            "desc": "Puntata secca sui 4 Bonus Game.",
            "how": "Stake alto solo sui bonus. Se non esce un bonus entro 10 giri, raddoppia (Attenzione: Molto rischioso)."
        }
    }
}

# --- LOGICA PERSISTENZA ---
def load_gold():
    lst = []
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3: lst.append({"Match": parts[0], "Tip": parts[1], "Odds": float(parts[2])})
    return lst

if 'gold_list' not in st.session_state: st.session_state['gold_list'] = load_gold()

# --- SIDEBAR ---
with st.sidebar:
    st.title("EDGE_V27")
    bankroll = st.number_input("BANKROLL (€)", value=200.0)
    module = st.radio("SELECT ENGINE", ["SPORTS_BETTING", "CASINO_STRATEGIES"])
    st.divider()
    if st.button("RESET ALL"):
        st.session_state.clear()
        st.rerun()

# --- MAIN ENGINE ---
col_main, col_ticket = st.columns([2, 1], gap="large")

if module == "SPORTS_BETTING":
    with col_main:
        st.title("/ SPORTS_ANALYSIS")
        if st.session_state['gold_list']:
            for g in st.session_state['gold_list']:
                st.markdown(f"<div class='gold-card'>{g['Match']} // {g['Tip']} @{g['Odds']}</div>", unsafe_allow_html=True)
        st.info("Load expert strategies or add Gold Tips to see analysis.")

else: # MODULO CASINO
    with col_main:
        st.title("/ CASINO_ENGINE")
        st.markdown("<p class='sub-text'>Crazy Time Mathematical Distribution</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🛡️ SAFE MODES")
            for name, data in STRATEGIES_CASINO["SAFE"].items():
                st.markdown(f"""
                    <div class='strategy-card'>
                        <b style='font-size:1.1rem;'>{name}</b><br>
                        <span style='color:#FFF; opacity:0.8;'>{data['desc']}</span>
                        <div class='how-to-play'><b>COME GIOCARE:</b><br>{data['how']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"SELECT {name}"): st.toast(f"Stake suggerito: €{round(bankroll*0.05,2)}")

        with c2:
            st.markdown("### 🔥 RISKY MODES")
            for name, data in STRATEGIES_CASINO["RISKY"].items():
                st.markdown(f"""
                    <div class='strategy-card'>
                        <b style='font-size:1.1rem;'>{name}</b><br>
                        <span style='color:#FFF; opacity:0.8;'>{data['desc']}</span>
                        <div class='how-to-play'><b>COME GIOCARE:</b><br>{data['how']}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"SELECT {name}", key=name+"_btn"): st.toast(f"Stake suggerito: €{round(bankroll*0.02,2)}")
