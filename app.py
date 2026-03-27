import google.generativeai as genai

genai.configure(api_key="AIzaSyCqe9yWNbVl47zbXgmo2dyMsmagCeZlEFM")
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Ciao, rispondi con la parola FUNZIONA")
    print(response.text)
except Exception as e:
    print(f"ERRORE REALE: {e}")
