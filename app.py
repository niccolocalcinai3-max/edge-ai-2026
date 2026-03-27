import streamlit as st
import google.generativeai as genai

# La tua chiave API
GOOGLE_API_KEY = "AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM"
genai.configure(api_key=GOOGLE_API_KEY)

st.title("⚽ EDGE AI - GENERATORE SCHEDINE")
st.write("L'IA analizzerà le partite di oggi basandosi sulle statistiche storiche globali.")

if st.button("🚀 GENERA SCHEDINA"):
    with st.spinner("L'intelligenza artificiale sta studiando i match di oggi..."):
        # USIAMO IL MODELLO AGGIORNATO 2.5
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = (
                "Agisci come un esperto di scommesse sportive. "
                "Trova 4 partite di calcio importanti previste per oggi o domani (27-28 Marzo 2026). "
                "Per ogni partita, crea una schedina con: 1. Squadre, 2. Pronostico (1X2 o Under/Over), "
                "3. Una breve analisi tecnica basata sulle vecchie statistiche e forma recente. "
                "Formatta tutto in una tabella chiara."
            )
            
            response = model.generate_content(prompt)
            
            st.success("✅ Schedina Generata con Successo!")
            st.markdown(response.text)
            
        except Exception as e:
            # Se il 2.5 non è ancora attivo sul tuo account, proviamo il 2.0
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except:
                st.error(f"Errore di connessione: {e}. Assicurati che la chiave API sia attiva in Google AI Studio.")

st.info("Nota: Questa IA analizza i trend storici e le notizie in tempo reale.")
