import customtkinter as ctk
import requests
from datetime import datetime
import random
import tkinter as tk
from tkinter import filedialog, messagebox

# --- PREMIUM UI CONFIG ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

LEAGUES = {
    "Global Markets": 0,
    "International (Nationals)": 1,
    "Premier League": 39,
    "Serie A": 135,
    "La Liga": 140
}

class EdgeAILuxury(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EDGE AI | RISK-STRATEGY SESSION 2026")
        self.geometry("1550x950")
        self.configure(fg_color="#000000")
        
        self.api_key = "0161ed129e075dbe7cab279cc96c7066"
        self.stored_matches = []
        self.active_session_matches = [] 

        # --- NAVIGATION ---
        self.nav = ctk.CTkFrame(self, height=70, fg_color="#050505", corner_radius=0)
        self.nav.pack(side="top", fill="x")
        ctk.CTkLabel(self.nav, text="E D G E  A I  /  P R E C I S I O N", font=("Inter", 22, "bold")).pack(side="left", padx=30)

        # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=320, fg_color="#020202", corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=1)

        # Market Access
        ctk.CTkLabel(self.sidebar, text="MARKET ACCESS", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(20, 5))
        self.league_menu = ctk.CTkOptionMenu(self.sidebar, values=list(LEAGUES.keys()), fg_color="#0a0a0a", button_color="#111")
        self.league_menu.pack(pady=5, padx=25, fill="x")

        self.scan_btn = ctk.CTkButton(self.sidebar, text="SCAN MARKET", fg_color="#FFFFFF", text_color="#000", corner_radius=2, command=self.run_scanner)
        self.scan_btn.pack(pady=10, padx=25, fill="x")

        # RISK STRATEGY TOGGLE
        ctk.CTkLabel(self.sidebar, text="RISK STRATEGY", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(20, 5))
        self.risk_mode = ctk.CTkSegmentedButton(self.sidebar, values=["SAFE", "BALANCED", "AGGRESSIVE"], 
                                               fg_color="#000", selected_color="#333", corner_radius=2)
        self.risk_mode.set("BALANCED")
        self.risk_mode.pack(padx=25, fill="x")

        # Coupon Builder
        ctk.CTkLabel(self.sidebar, text="FINANCIAL TARGETS", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(25, 5))
        self.stake_in = self.create_input("STAKE (€)")
        self.win_in = self.create_input("TARGET (€)")
        
        self.gen_btn = ctk.CTkButton(self.sidebar, text="GENERATE PROPOSAL", border_width=1, border_color="#FFF", fg_color="transparent", command=self.generate_proposal)
        self.gen_btn.pack(pady=15, padx=25, fill="x")

        # --- RIGHT SIDEBAR (ACTIVE SESSION) ---
        self.active_sidebar = ctk.CTkFrame(self, width=380, fg_color="#050505", border_width=1, border_color="#111")
        self.active_sidebar.pack(side="right", fill="y", padx=1)
        
        ctk.CTkLabel(self.active_sidebar, text="LIVE TICKET SESSION", font=("Inter", 12, "bold"), text_color="#00FF00").pack(pady=20)
        self.session_scroll = ctk.CTkScrollableFrame(self.active_sidebar, fg_color="transparent")
        self.session_scroll.pack(fill="both", expand=True, padx=10)

        self.print_btn = ctk.CTkButton(self.active_sidebar, text="PRINT SESSION ⎙", fg_color="#111", text_color="#888", command=self.print_ticket)
        self.print_btn.pack(pady=20, padx=30, fill="x")

        # --- CENTER DISPLAY ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="GLOBAL MARKET INTEL")
        self.scroll_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder, fg_color="#000", border_color="#1a1a1a", corner_radius=0, height=35)
        entry.pack(pady=5, padx=25, fill="x")
        return entry

    def run_scanner(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.stored_matches = []
        l_id = LEAGUES[self.league_menu.get()]
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}"
        if l_id != 0: url += f"&league={l_id}&season=2026"
            
        try:
            res = requests.get(url, headers={'x-apisports-key': self.api_key}).json().get('response', [])
            for m in res:
                data = {
                    "id": m['fixture']['id'],
                    "teams": f"{m['teams']['home']['name']} vs {m['teams']['away']['name']}",
                    "tip": random.choice(["HOME WIN", "OVER 2.5", "BTTS"]),
                    "quote": round(random.uniform(1.3, 3.5), 2),
                    "h_score": m['goals']['home'] if m['goals']['home'] is not None else 0,
                    "a_score": m['goals']['away'] if m['goals']['away'] is not None else 0,
                    "status": m['fixture']['status']['short'],
                    "conf": random.randint(70, 99)
                }
                self.stored_matches.append(data)
                self.add_card(self.scroll_frame, data)
        except: pass

    def generate_proposal(self):
        """Precision Engine with Risk Filtering."""
        try:
            stake = float(self.stake_in.get())
            target = float(self.win_in.get())
            req_odds = target / stake
        except: return

        # Apply Risk Filtering
        mode = self.risk_mode.get()
        if mode == "SAFE":
            pool = [m for m in self.stored_matches if m['quote'] < 1.85]
        elif mode == "AGGRESSIVE":
            pool = [m for m in self.stored_matches if m['quote'] > 2.20]
        else: # Balanced
            pool = self.stored_matches

        if not pool:
            messagebox.showwarning("Risk Error", f"No {mode} matches found in the current scan.")
            return

        proposal = []
        c_odds = 1.0
        random.shuffle(pool)

        for m in sorted(pool, key=lambda x: x['conf'], reverse=True):
            if c_odds < req_odds:
                proposal.append(m)
                c_odds *= m['quote']
            else: break

        msg = f"TICKET PROPOSAL ({mode})\n" + "-"*20 + "\n"
        msg += f"Total Odds: {c_odds:.2f}\n"
        msg += f"Potential Win: €{c_odds * stake:.2f}\n\n"
        msg += "Keep this session?"
        
        if messagebox.askyesno("EdgeAI Decision", msg):
            self.active_session_matches = proposal
            self.refresh_session_ui()

    def add_card(self, parent, data, is_session=False):
        bg = "#080808" if not is_session else "#000"
        card = ctk.CTkFrame(parent, fg_color=bg, border_width=1, border_color="#111")
        card.pack(fill="x", pady=5, padx=5)
        
        dot_color = "#444"
        if is_session:
            h, a = data['h_score'], data['a_score']
            win = (data['tip'] == "HOME WIN" and h > a) or (data['tip'] == "OVER 2.5" and (h+a) > 2.5)
            dot_color = "#00FF00" if win else "#FF0000"
            if data['status'] == "NS": dot_color = "#444"

        ctk.CTkLabel(card, text="●", text_color=dot_color).pack(side="left", padx=10)
        ctk.CTkLabel(card, text=f"{data['teams']}\n{data['tip']} @ {data['quote']}", font=("Inter", 11), justify="left").pack(side="left", pady=10)
        ctk.CTkLabel(card, text=f"{data['h_score']}-{data['a_score']}\n{data['status']}", font=("Inter", 10), text_color="#666").pack(side="right", padx=10)

    def refresh_session_ui(self):
        for widget in self.session_scroll.winfo_children(): widget.destroy()
        for m in self.active_session_matches:
            self.add_card(self.session_scroll, m, is_session=True)

    def print_ticket(self):
        if not self.active_session_matches: return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f:
                f.write("EDGE AI ACTIVE SESSION\n" + "-"*30 + "\n")
                for m in self.active_session_matches:
                    f.write(f"{m['teams']} | {m['tip']} | {m['h_score']}-{m['a_score']}\n")
            messagebox.showinfo("Export", "Saved.")

if __name__ == "__main__":
    app = EdgeAILuxury()
    app.mainloop()
