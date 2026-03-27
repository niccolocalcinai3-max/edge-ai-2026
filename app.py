import streamlit as st
import google.generativeai as genai

# Inserisci qui la tua chiave che mi hai dato
genai.configure(api_key="AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM")

st.title("🤖 EDGE AI - SCHEDINA AUTOMATICA")
st.write("Clicca il bottone per far analizzare all'AI le partite di oggi nel mondo.")

if st.button("🚀 GENERA SCHEDINA DEL GIORNO"):
    with st.spinner("L'intelligenza artificiale sta cercando le partite e analizzando le statistiche..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Chiediamo all'AI di usare la sua conoscenza aggiornata
        prompt = (
            "Analizza le partite di calcio dei principali campionati europei previste per oggi 27 marzo 2026 e domani. "
            "Crea una schedina di 4 partite con Segno e Motivazione tecnica basata sulla forma recente. "
            "Usa un tono da esperto scommettitore."
        )
        
        try:
            response = model.generate_content(prompt)
            st.success("✅ Schedina Pronta!")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")

st.info("Nota: Questa analisi non usa i file CSV caricati, ma l'intelligenza artificiale in tempo reale.")
