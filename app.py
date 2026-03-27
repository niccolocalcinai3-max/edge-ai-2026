import streamlit as st
import google.generativeai as genai

# Use the key you provided
GOOGLE_API_KEY = "AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM"
genai.configure(api_key=GOOGLE_API_KEY)

def get_ai_reasoning(home, away, h_stats, a_stats):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We provide the AI with the actual numbers from your CSVs
    prompt = (
        f"Context: Data from European Leagues 2026.\n"
        f"Match: {home} vs {away}.\n"
        f"{home} Form (Last 5): {h_stats['Form_Pts']} pts, {h_stats['Avg_GS']} goals/match.\n"
        f"{away} Form (Last 5): {a_stats['Form_Pts']} pts, {a_stats['Avg_GS']} goals/match.\n"
        f"Task: Provide a 2-sentence professional betting tip. "
        f"Be decisive. Use a 'Sharp Bettor' tone."
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # This will show you the REAL error in the app so we can fix it
        return f"❌ AI Error: {str(e)}"
