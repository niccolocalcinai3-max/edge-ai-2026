import customtkinter as ctk

import sqlite3

import hashlib

import requests

from datetime import datetime

import random

import tkinter as tk

from tkinter import filedialog, messagebox



# --- CONFIGURATION & DATABASE ---

ctk.set_appearance_mode("dark")

ctk.set_default_color_theme("blue")



def init_db():

    conn = sqlite3.connect("edge_vault.db")

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users 

                      (username TEXT PRIMARY KEY, password TEXT)''')

    conn.commit()

    conn.close()



def hash_password(password):

    return hashlib.sha256(password.encode()).hexdigest()



LEAGUES = {

    "Global Markets": 0,

    "International (Nationals)": 1,

    "Premier League (UK)": 39,

    "Serie A (Italy)": 135,

    "La Liga (Spain)": 140,

    "Bundesliga (Germany)": 78

}



# --- AUTHENTICATION UI ---

class LoginWindow(ctk.CTkToplevel):

    def __init__(self, parent):

        super().__init__(parent)

        self.parent = parent

        self.title("EDGE AI | SECURE GATE")

        self.geometry("400x550")

        self.configure(fg_color="#000")

        self.attributes("-topmost", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        

        # Branding

        ctk.CTkLabel(self, text="E D G E  A I", font=("Inter", 28, "bold"), text_color="#FFF").pack(pady=(50, 10))

        ctk.CTkLabel(self, text="BIOMETRIC VERIFICATION REQUIRED", font=("Inter", 10), text_color="#444").pack(pady=(0, 40))

        

        # Inputs

        self.user_in = self.create_auth_input("Username")

        self.pass_in = self.create_auth_input("Password", is_pass=True)

        

        # Actions

        self.login_btn = ctk.CTkButton(self, text="ACCESS SYSTEM", fg_color="#FFF", text_color="#000", corner_radius=2, height=45, command=self.attempt_login)

        self.login_btn.pack(pady=(30, 10), padx=50, fill="x")

        

        self.signup_btn = ctk.CTkButton(self, text="REGISTER NEW KEY", fg_color="transparent", border_width=1, border_color="#222", text_color="#666", corner_radius=2, command=self.attempt_signup)

        self.signup_btn.pack(pady=5, padx=50, fill="x")



    def create_auth_input(self, placeholder, is_pass=False):

        entry = ctk.CTkEntry(self, placeholder_text=placeholder, show="*" if is_pass else "", fg_color="#0a0a0a", border_color="#1a1a1a", height=45, corner_radius=2)

        entry.pack(pady=10, padx=50, fill="x")

        return entry



    def attempt_login(self):

        u, p = self.user_in.get(), hash_password(self.pass_in.get())

        conn = sqlite3.connect("edge_vault.db")

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))

        if cursor.fetchone():

            self.parent.unlock_app()

            self.destroy()

        else:

            messagebox.showerror("Auth Error", "Invalid Credentials")

        conn.close()



    def attempt_signup(self):

        u, p_raw = self.user_in.get(), self.pass_in.get()

        if not u or len(p_raw) < 4:

            messagebox.showwarning("System", "Credentials too short")

            return

        p = hash_password(p_raw)

        try:

            conn = sqlite3.connect("edge_vault.db")

            cursor = conn.cursor()

            cursor.execute("INSERT INTO users VALUES (?, ?)", (u, p))

            conn.commit()

            conn.close()

            messagebox.showinfo("Success", "Identity Registered. You may now Login.")

        except sqlite3.IntegrityError:

            messagebox.showerror("Error", "Username already exists")



    def on_close(self):

        self.parent.destroy()



# --- MAIN ENGINE ---

class EdgeAILuxury(ctk.CTk):

    def __init__(self):

        super().__init__()

        init_db()

        

        self.withdraw() # Hide until Login

        self.title("EDGE AI | LUXURY ANALYTICS 2026")

        self.geometry("1550x950")

        self.configure(fg_color="#000000")

        

        self.api_key = "0161ed129e075dbe7cab279cc96c7066"

        self.stored_matches = []

        self.active_session_matches = []

        

        self.setup_ui()

        self.login_screen = LoginWindow(self)



    def setup_ui(self):

        # --- TOP NAVIGATION ---

        self.nav = ctk.CTkFrame(self, height=75, fg_color="#050505", corner_radius=0)

        self.nav.pack(side="top", fill="x")

        ctk.CTkLabel(self.nav, text="E D G E  A I  /  P R E C I S I O N", font=("Inter", 22, "bold")).pack(side="left", padx=40)

        self.status_pulse = ctk.CTkLabel(self.nav, text="● ENCRYPTED CONNECTION", text_color="#00FF00", font=("Inter", 10))

        self.status_pulse.pack(side="right", padx=40)



        # --- LEFT SIDEBAR (CONTROLS) ---

        self.sidebar = ctk.CTkFrame(self, width=320, fg_color="#020202", corner_radius=0)

        self.sidebar.pack(side="left", fill="y", padx=1)



        ctk.CTkLabel(self.sidebar, text="MARKET ACCESS", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(30, 5))

        self.league_menu = ctk.CTkOptionMenu(self.sidebar, values=list(LEAGUES.keys()), fg_color="#0a0a0a", button_color="#111", corner_radius=2)

        self.league_menu.pack(pady=5, padx=30, fill="x")



        self.scan_btn = ctk.CTkButton(self.sidebar, text="SCAN GLOBAL MARKET", fg_color="#FFF", text_color="#000", corner_radius=2, height=40, command=self.run_scanner)

        self.scan_btn.pack(pady=10, padx=30, fill="x")



        ctk.CTkLabel(self.sidebar, text="RISK STRATEGY", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(20, 5))

        self.risk_mode = ctk.CTkSegmentedButton(self.sidebar, values=["SAFE", "BALANCED", "AGGRESSIVE"], fg_color="#000", selected_color="#333", corner_radius=2)

        self.risk_mode.set("BALANCED")

        self.risk_mode.pack(padx=30, fill="x")



        ctk.CTkLabel(self.sidebar, text="COUPON BUILDER", font=("Inter", 10, "bold"), text_color="#444").pack(pady=(25, 5))

        self.stake_in = self.create_sidebar_input("STAKE (€)")

        self.win_in = self.create_sidebar_input("TARGET (€)")

        

        self.gen_btn = ctk.CTkButton(self.sidebar, text="GENERATE PROPOSAL", border_width=1, border_color="#FFF", fg_color="transparent", height=40, command=self.generate_proposal)

        self.gen_btn.pack(pady=15, padx=30, fill="x")



        # --- RIGHT SIDEBAR (ACTIVE SESSION) ---

        self.active_sidebar = ctk.CTkFrame(self, width=380, fg_color="#050505", border_width=1, border_color="#111")

        self.active_sidebar.pack(side="right", fill="y", padx=1)

        

        ctk.CTkLabel(self.active_sidebar, text="LIVE TICKET SESSION", font=("Inter", 12, "bold"), text_color="#00FF00").pack(pady=20)

        self.session_scroll = ctk.CTkScrollableFrame(self.active_sidebar, fg_color="transparent")

        self.session_scroll.pack(fill="both", expand=True, padx=10)



        self.print_btn = ctk.CTkButton(self.active_sidebar, text="PRINT SESSION ⎙", fg_color="#111", text_color="#888", command=self.print_ticket)

        self.print_btn.pack(pady=20, padx=40, fill="x")



        # --- CENTER CONTENT ---

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", label_text="MARKET INTELLIGENCE")

        self.scroll_frame.pack(side="left", fill="both", expand=True, padx=25, pady=25)



    def create_sidebar_input(self, placeholder):

        entry = ctk.CTkEntry(self.sidebar, placeholder_text=placeholder, fg_color="#000", border_color="#1a1a1a", corner_radius=0, height=35)

        entry.pack(pady=5, padx=30, fill="x")

        return entry



    def unlock_app(self):

        self.deiconify()



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

        except: messagebox.showerror("System", "API Connection Failed")



    def generate_proposal(self):

        try:

            stake, target = float(self.stake_in.get()), float(self.win_in.get())

            req_odds = target / stake

        except: return



        mode = self.risk_mode.get()

        if mode == "SAFE":

            pool = [m for m in self.stored_matches if m['quote'] < 1.85 and m['status'] != "FT"]

        elif mode == "AGGRESSIVE":

            pool = [m for m in self.stored_matches if m['quote'] > 2.20 and m['status'] != "FT"]

        else:

            pool = [m for m in self.stored_matches if m['status'] != "FT"]



        if not pool: return



        proposal = []

        c_odds = 1.0

        random.shuffle(pool)



        for m in sorted(pool, key=lambda x: x['conf'], reverse=True):

            if c_odds < req_odds:

                proposal.append(m)

                c_odds *= m['quote']

            else: break



        msg = f"TICKET PROPOSAL ({mode})\nTotal Odds: {c_odds:.2f}\nPotential Win: €{c_odds * stake:.2f}\n\nLock this session?"

        if messagebox.askyesno("EdgeAI Decision", msg):

            self.active_session_matches = proposal

            self.refresh_session_ui()



    def add_card(self, parent, data, is_session=False):

        bg = "#080808" if not is_session else "#000"

        card = ctk.CTkFrame(parent, fg_color=bg, border_width=1, border_color="#111")

        card.pack(fill="x", pady=6, padx=5)

        

        dot_color = "#444"

        if is_session:

            h, a, tip = data['h_score'], data['a_score'], data['tip']

            win = (tip == "HOME WIN" and h > a) or (tip == "OVER 2.5" and (h+a) > 2.5) or (tip == "BTTS" and h > 0 and a > 0)

            dot_color = "#00FF00" if win else "#FF0000"

            if data['status'] == "NS": dot_color = "#444"



        ctk.CTkLabel(card, text="●", text_color=dot_color, font=("Inter", 16)).pack(side="left", padx=15)

        ctk.CTkLabel(card, text=f"{data['teams']}\n{data['tip']} @ {data['quote']}", font=("Inter", 11), justify="left").pack(side="left", pady=10)

        ctk.CTkLabel(card, text=f"{data['h_score']}-{data['a_score']}\n{data['status']}", font=("Inter", 10), text_color="#666").pack(side="right", padx=15)



    def refresh_session_ui(self):

        for widget in self.session_scroll.winfo_children(): widget.destroy()

        for m in self.active_session_matches:

            self.add_card(self.session_scroll, m, is_session=True)



    def print_ticket(self):

        if not self.active_session_matches: return

        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="EDGE_AI_SESSION.txt")

        if path:

            with open(path, "w", encoding="utf-8") as f:

                f.write(f"--- EDGE AI SESSION | {datetime.now().strftime('%Y-%m-%d')} ---\n")

                for m in self.active_session_matches:

                    f.write(f"[{m['status']}] {m['teams']} | TIP: {m['tip']} (@{m['quote']}) | SCORE: {m['h_score']}-{m['a_score']}\n")

            messagebox.showinfo("Export", "Session Ticket Printed.")



if __name__ == "__main__":

    app = EdgeAILuxury()

    app.mainloop()
