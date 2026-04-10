import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="AI Bet Predictor", layout="wide")

st.title("🤖 AI Bet Predictor - Schedine del Giorno")
st.markdown("Analisi basata su dati statistici avanzati e Machine Learning.")

# Sidebar per navigazione e link affiliazione
st.sidebar.header("Bonus Benvenuto")
st.sidebar.info("Registrati su [Nome Bookmaker] con il link dell'IA per sbloccare il Bonus!")
st.sidebar.button("Vai al Gruppo Telegram 🚀")

# Sezione Schedine
col1, col2 = st.columns(2)

with col1:
    st.header("🛡️ Schedina Safe")
    st.table(pd.DataFrame({
        'Partita': ['Real Madrid - Girona', 'Marsiglia - Metz'],
        'Pronostico': ['1', '1 + Over 1.5'],
        'Quota': [1.35, 1.60]
    }))
    st.success("Quota Totale: 2.16")

with col2:
    st.header("🚀 Schedina Risky")
    st.table(pd.DataFrame({
        'Partita': ['West Ham - Wolves', 'Roma - Pisa'],
        'Pronostico': ['X', 'Risultato Esatto 2-0'],
        'Quota': [3.40, 7.50]
    }))
    st.error("Quota Totale: 25.50")

# Sezione "L'angolo dell'Algoritmo"
st.divider()
st.subheader("📊 Perché l'IA ha scelto queste giocate?")
st.write("L'algoritmo ha rilevato una probabilità di vittoria del Real Madrid pari al 78%...")
