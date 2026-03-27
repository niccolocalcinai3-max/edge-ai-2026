import customtkinter as ctk
import requests
from datetime import datetime
import google.generativeai as genai  # <--- Nuova Integrazione
import json
import threading

# --- CONFIGURAZIONE AI ---
# Inserisci qui la tua chiave API di Google
genai.configure(api_key="TUA_CHIAVE_GOOGLE_GEMINI")
ai_model = genai.GenerativeModel('gemini-1.5-flash')

class EdgeAILuxury(ctk.CTk):
    # ... (manteniamo la __init__ e la UI identica alla tua) ...

    def run_scanner(self):
        """Scansiona i match e chiede all'IA di analizzarli uno per uno."""
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.stored_matches = []
        
        l_id = LEAGUES[self.league_menu.get()]
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        if l_id != 0: url += f"&league={l_id}&season=2026"
            
        try:
            res = requests.get(url, headers={'x-apisports-key': self.api_key}).json().get('response', [])
            
            # Usiamo un thread per non bloccare la UI mentre l'IA ragiona
            threading.Thread(target=self.process_matches_with_ai, args=(res,)).start()
        except Exception as e:
            print(f"Errore API: {e}")

    def process_matches_with_ai(self, fixtures):
        """Invia i dati alla AI per un'analisi reale."""
        for m in fixtures[:15]: # Limitiamo a 15 per velocità
            home = m['teams']['home']['name']
            away = m['teams']['away']['name']
            league = m['league']['name']
            
            # Il Prompt per l'IA
            prompt = f"""
            Analizza il match di {league}: {home} vs {away}.
            Basandoti sulla tua conoscenza storica, fornisci:
            1. Un consiglio (HOME WIN, AWAY WIN, OVER 2.5, o BTTS)
            2. Una percentuale di confidenza (70-99)
            Rispondi solo in formato JSON: {{"tip": "...", "conf": 00}}
            """
            
            try:
                response = ai_model.generate_content(prompt)
                # Pulizia della risposta per estrarre il JSON
                ai_data = json.loads(response.text.replace("```json", "").replace("```", ""))
                
                data = {
                    "id": m['fixture']['id'],
                    "teams": f"{home} vs {away}",
                    "tip": ai_data['tip'],
                    "quote": round(2.0, 2), # Qui potresti integrare le quote reali dell'API
                    "h_score": m['goals']['home'] if m['goals']['home'] is not None else 0,
                    "a_score": m['goals']['away'] if m['goals']['away'] is not None else 0,
                    "status": m['fixture']['status']['short'],
                    "conf": ai_data['conf']
                }
                self.stored_matches.append(data)
                # Aggiorna la UI in modo sicuro
                self.after(0, lambda d=data: self.add_card(self.scroll_frame, d))
            except:
                continue

    def generate_proposal(self):
        """Usa l'IA per comporre la schedina perfetta basata sul budget."""
        try:
            stake = float(self.stake_in.get())
            target = float(self.win_in.get())
            mode = self.risk_mode.get()
        except: 
            messagebox.showerror("Error", "Inserisci Stake e Target validi")
            return

        if not self.stored_matches:
            messagebox.showwarning("Analisi", "Esegui prima uno SCAN MARKET")
            return

        # Passiamo la lista dei match scansionati all'IA per scegliere i migliori
        matches_str = json.dumps(self.stored_matches)
        
        prompt = f"""
        Ho questi match: {matches_str}
        Il mio budget è {stake}€ e voglio vincere {target}€. Strategia: {mode}.
        Scegli i match migliori per raggiungere l'obiettivo in modo intelligente.
        Restituisci solo gli ID dei match scelti separati da virgola.
        """

        try:
            response = ai_model.generate_content(prompt)
            chosen_ids = [id.strip() for id in response.text.split(",")]
            
            proposal = [m for m in self.stored_matches if str(m['id']) in chosen_ids]
            
            if proposal:
                self.active_session_matches = proposal
                self.refresh_session_ui()
                messagebox.showinfo("Edge AI", "Schedina ottimizzata generata dall'Intelligenza Artificiale.")
        except Exception as e:
            messagebox.showerror("AI Error", f"L'IA non è riuscita a compilare la schedina: {e}")

# ... (il resto della classe rimane uguale)
