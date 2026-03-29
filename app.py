import streamlit as st
import os

# --- CONFIGURAZIONE CORE ---
SAVE_FILE = "gold_storage.txt"
st.set_page_config(page_title="EDGE MOBILE", layout="wide")

# --- UI & STARS ENGINE (MOBILE OPTIMIZED) ---
st.markdown("""
    <canvas id="canvas"></canvas>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    #canvas {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: -1;
        background: #000;
    }

    /* Reset per Mobile */
    .main .block-container {
        padding: 10px !important;
        max-width: 100%;
    }

    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
        color: #FFFFFF !important;
    }

    /* Cards responsive */
    .match-card, .strategy-card {
        background: rgba(20, 20, 20, 0.8) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 18px;
        margin-bottom: 15px;
        width: 100%; /* Forza larghezza piena su mobile */
    }

    /* Bottoni giganti per dita */
    .stButton>button {
        background: #FFFFFF !important;
        color: #000 !important;
        border-radius: 10px !important;
        font-weight: 800 !important;
        height: 55px !important; /* Più alto per il touch */
        width: 100% !important;
        margin-top: 5px;
        border: none !important;
    }

    .gold-card {
        background: #FFF;
        color: #000;
        padding: 15px;
        border-radius: 12px;
        font-weight: 800;
        margin-bottom: 10px;
        text-align: center;
        border-left: 5px solid #888;
    }

    .how-to-play {
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-top: 10px;
        color: #CCC;
    }

    /* Sidebar più leggibile */
    section[data-testid="stSidebar"] {
        background-color: rgba(10,10,10,0.95) !important;
    }

    h1 { font-size: 1.8rem !important; letter-spacing: -1px; }
    h3 { font-size: 1.2rem !important; margin-top: 20px; }
    </style>

    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    let stars = [];
    for(let i=0; i<80; i++) { // Meno stelle per performance mobile
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 1.5,
            speed: Math.random() * 0.3 + 0.1
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "white";
        stars.forEach(s => {
            s.y += s.speed;
            if(s.y > canvas.height) s.y = 0;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.size, 0, Math.PI*2);
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
    </script>
    """, unsafe_allow_html=True)

# --- LOGICA DATI ---
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
    st.title("NEBULA_V28")
    bankroll = st.number_input("BANKROLL (€)", value=200.0)
    module = st.radio("ENGINE", ["SPORTS", "CASINO"])
    st.divider()
    if st.button("RESET"):
        st.session_state.clear()
        st.rerun()

# --- MAIN ENGINE (STACKED FOR MOBILE) ---
if module == "SPORTS":
    st.title("⚽ SPORTS_FEED")
    if st.session_state['gold_list']:
        for g in st.session_state['gold_list']:
            st.markdown(f"<div class='gold-card'>{g['Match']}<br>{g['Tip']} @{g['Odds']}</div>", unsafe_allow_html=True)
    st.info("Usa la sidebar per caricare i dati.")

else: # CASINO
    st.title("🎰 CASINO_ENGINE")
    
    # Lista strategie semplificata per scroll verticale
    st.subheader("🛡️ SAFE STRATEGIES")
    safe_data = {
        "SHIELD 1-2": "4u sull'1, 2u sul 2. Copre 66%. Se esce l'1 pareggi, sul 2 vinci.",
        "GRINDER": "5u sull'1 + 0.50u su ogni Bonus. L'1 finanzia i tentativi bonus.",
        "ANTI-VARIANCE": "80% sul 2, resto su Cash Hunt e Coin Flip. Bilanciato."
    }
    for name, how in safe_data.items():
        with st.container():
            st.markdown(f"""<div class='strategy-card'><b>{name}</b><div class='how-to-play'>{how}</div></div>""", unsafe_allow_html=True)
            if st.button(f"ATTIVA {name}"): st.toast(f"Stake: €{round(bankroll*0.05,2)}")

    st.subheader("🔥 RISKY STRATEGIES")
    risky_data = {
        "BONUS HUNTER": "Solo Bonus (1u ciascuno). Ignora i numeri, punta al moltiplicatore.",
        "CRAZY MAX": "Punta solo su Crazy Time e Pachinko. Alta volatilità.",
        "ULTRA DOUBLE": "Solo Bonus. Se perdi 10 giri, raddoppia. Estremamente rischioso."
    }
    for name, how in risky_data.items():
        with st.container():
            st.markdown(f"""<div class='strategy-card' style='border-left:4px solid #555;'><b>{name}</b><div class='how-to-play'>{how}</div></div>""", unsafe_allow_html=True)
            if st.button(f"ATTIVA {name}", key=name): st.toast(f"Stake: €{round(bankroll*0.02,2)}")
