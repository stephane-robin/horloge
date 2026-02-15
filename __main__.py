import turtle
import datetime
import tkinter as tk
from tkinter import ttk
import sys
import os
import pygame

pygame.mixer.init()

def resource_path(relative_path):
    """Renvoie le chemin absolu. Fonctionne en dev et pour pyinstaller."""
    try:
        # PyInstaller cree un dossier temporaire et enregistre le chemin dans in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # en prod le code va utiliser le dossier courant
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

image_path = resource_path("al3.png")
sound_path = resource_path("reveil.mp3")
bg_path = resource_path("bg.png")


class Alarm:
    """Gere la mise en place d'une alarme. L'attribut active 
    definit si l'alarme a ete activee ou non. L'attribut trigerred 
    definit si l'alarme s'est declenchee ou non."""
    def __init__(self, heure, minute):
        self.heure = int(heure)
        self.minute = int(minute)
        self.active = False
        self.triggered = False

    def toggle(self):
        """Inverse le caractere actif d'une alarme. Definit triggered 
        comme etant non declenchee."""
        self.active = not self.active
        self.triggered = False
        return self.active
    
    def snooze(self):
        """Snooze l'alarme une fois dans 5 minutes."""
        now = datetime.datetime.now()
        new_time = now + datetime.timedelta(minutes=5)
        self.heure = new_time.hour
        self.minute = new_time.minute
        self.triggered = False
        self.active = True

    def check(self, h, m):
        """Verifie que l'heure actuelle est l'heure enregistree 
        dans l'alarme et declenche l'alarme si c'est le cas."""
        if self.active and not self.triggered:
            if self.heure == h and self.minute == m:
                self.triggered = True
                return True 
        return False


class ClockApp:
    """Gere la construction de l'horloge."""
   
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("horloge myToketa")
        self.largeur, self.hauteur = 494, 394
        self.root.geometry(f"{self.largeur}x{self.hauteur}")
        self.root.resizable(False, False)

        self.bg_match = "#d8e9eb"
        self.color_btn = "#756454"
        self.hover_color = "#8a7a6a"
        self.heure, self.minute, self.seconde = 0, 0, 0
        self.ringing = False
        try:
            self.alarm_icon = tk.PhotoImage(file=image_path)
            self.bg_image = tk.PhotoImage(file=bg_path)
        except:
            self.alarm_icon = None
            self.bg_image = None
        self.root.iconphoto(False, self.alarm_icon)
        self.heure_choisie = tk.StringVar(value="00")
        self.minute_choisie = tk.StringVar(value="00")
        self.alarm = Alarm(self.heure_choisie.get(), self.minute_choisie.get())

        self.canvas = tk.Canvas(
            self.root,
            width=self.largeur,
            height=self.hauteur,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgpic(bg_path)  
        self.screen.tracer(0)

        self.t = turtle.RawTurtle(self.screen)
        self.t.hideturtle()
        self.t.speed(0)
        self.t.color("black")
        self.t.pensize(5)

        self.t_date = turtle.RawTurtle(self.screen)
        self.t_date.hideturtle()
        self.t_date.speed(0)
        self.t_date.penup()

        self.ui_frame = tk.Frame(self.root, bg=self.bg_match)
        self.ui_frame.place(x=self.largeur//2, y=275, anchor="center")

        self.controls = tk.Frame(self.ui_frame, bg=self.bg_match)
        self.controls.pack(side="left", padx=0)

        self.container_combo = tk.Frame(self.controls, bg=self.bg_match)
        self.container_combo.pack()

        hours = [f"{i:02d}" for i in range(24)]
        self.menu_heures = ttk.Combobox(
            self.container_combo,
            textvariable=self.heure_choisie,
            values=hours,
            width=3,
            state="readonly"
        )
        self.menu_heures.pack(side="left", padx=0)

        tk.Label(self.container_combo, text="h", bg=self.bg_match).pack(side="left")

        minutes = [f"{i:02d}" for i in range(60)]
        self.menu_minutes = ttk.Combobox(
            self.container_combo,
            textvariable=self.minute_choisie,
            values=minutes,
            width=3,
            state="readonly"
        )
        self.menu_minutes.pack(side="left", padx=0)

        self.btn = tk.Canvas(
            self.controls,
            width=160,
            height=35,
            highlightthickness=0,
            bg=self.bg_match
        )
        self.btn.pack(pady=5)
        self.dessiner_btn(self.btn, "Activer l'alarme", self.color_btn)
        self.setup_hover(self.btn)
        self.btn.bind("<Button-1>", lambda e: self.declencher_alarme())
        self.snooze_btn = tk.Canvas(self.controls, width=160, height=35, highlightthickness=0, bg=self.bg_match)
        self.setup_hover(self.snooze_btn)
        self.snooze_btn.bind("<Button-1>", lambda e: self.action_snooze())

        self.label_alarm = tk.Label(
            self.ui_frame,
            font=("Arial", 12, "bold"),
            compound="left", # important pour garder l'affichage du reveil
            bg=self.bg_match
        )
        self.label_alarm.pack(side="left", padx=0)

    def dessiner_btn(self, canvas_target, message, color):
        """Dessine un bouton rond integre dans un panneau canvas."""
        canvas_target.delete("all")
        w, h = 155, 34 
        r = h - 2       
        canvas_target.create_oval((2, 2, r, h), fill=color, outline=color)
        canvas_target.create_oval((w-r, 2, w, h), fill=color, outline=color)
        canvas_target.create_rectangle((2 + r/2, 2, w - r/2, h), fill=color, outline=color)
        canvas_target.current_msg = message
        canvas_target.create_text(w/2, h/2, text=message, fill="white", font=("Arial", 12, "bold"))

    def setup_hover(self, canvas_target):
        """Ajoute l'effet hover aux boutons."""
        
        def on_enter(e):
            self.dessiner_btn(canvas_target, canvas_target.current_msg, color=self.hover_color)
            
        def on_leave(e):
            self.dessiner_btn(canvas_target, canvas_target.current_msg, color=self.color_btn)
            
        canvas_target.bind("<Enter>", on_enter)
        canvas_target.bind("<Leave>", on_leave)    

    def declencher_alarme(self):
        """Active ou desactive le bouton d'alarme."""
        if not self.alarm.active:
            self.alarm.heure = int(self.heure_choisie.get())
            self.alarm.minute = int(self.minute_choisie.get())
            self.alarm.toggle()
            self.dessiner_btn(self.btn, "Désactiver", self.color_btn)
            self.snooze_btn.pack(pady=2)
            self.dessiner_btn(self.snooze_btn, "Snooze", self.color_btn)
            self.menu_heures.config(state="disabled")
            self.menu_minutes.config(state="disabled")            
            self.label_alarm.config(text=f"{self.alarm.heure:02d}:{self.alarm.minute:02d} activée.", image=self.alarm_icon)
        else:
            self.alarm.toggle()
            pygame.mixer.music.stop()
            self.ringing = False            
            self.dessiner_btn(self.btn, "Activer l'alarme", self.color_btn)
            self.snooze_btn.pack_forget()
            self.menu_heures.config(state="readonly")
            self.menu_minutes.config(state="readonly")
            self.label_alarm.config(text="", image="")

    def action_snooze(self):
        pygame.mixer.music.stop()
        self.ringing = False
        self.alarm.snooze()
        self.label_alarm.config(text=f"Snooze: {self.alarm.heure:02d}:{self.alarm.minute:02d}")

    def affiche_heure(self):
        """Affiche l'heure dans une fenetre""" 

        def extraire_unite(temps):
            """Extrait le 1er et le 2eme chiffre d'un nombre pouvant 
            representer les secondes, les minutes ou les heures. Pour 
            les nombres inferieurs a 10, rajoute un 0 pour le 1er 
            chiffre."""
            return (0, temps) if temps < 10 else (temps // 10, temps % 10)

        def construire2points(x):
            """Construit deux points verticaux pour separer les heures des 
            minutes ou les minutes des secondes. L'abscisse est representee 
            par x"""
            for i in range(2):
                self.t.penup()
                self.t.goto(x, 60 - i * 30)
                self.t.pendown()
                self.t.circle(1)
                self.t.penup()

        def construire_nombre(nmr, x):
            """Construit un nombre represente par nmr, place a 
            l'abscisse x."""

            def dessiner_barre(barre):
                """Dessine une barre faisant partie de l'affichage d'un 
                nombre. L'argument barre est un tuple contenant l'abscisse, 
                l'ordonnee et la direction du trace."""
                self.t.penup()
                self.t.goto(barre[0], barre[1]+60)
                self.t.setheading(barre[2])
                self.t.pendown()
                self.t.forward(20)
                self.t.penup()
                self.t.setheading(0)

            composantes = (
                (-140 + x, 15, 0), 
                (-115 + x, 10, -90), 
                (-115 + x, -20, -90), 
                (-120 + x, -45, -180), 
                (-145 + x, -40, 90), 
                (-145 + x, -10, 90), 
                (-140 + x, -15, 0)
            )
            chiffres = [
                (True, True, True, True, True, True, False),
                (False, True, True, False, False, False, False),
                (True, True, False, True, True, False, True),
                (True, True, True, True, False, False, True),
                (False, True, True, False, False, True, True),
                (True, False, True, True, False, True, True),
                (True, False, True, True, True, True, True),
                (True, True, True, False, False, False, False),
                (True, True, True, True, True, True, True),
                (True, True, True, True, False, True, True),
            ]
            for i, draw in enumerate(chiffres[nmr]):
                if draw:
                    dessiner_barre(composantes[i])

        now = datetime.datetime.now()
        current_date = now.date()
        if getattr(self, "last_date", None) != current_date:
            self.last_date = current_date
            self.t_date.clear()
            self.t_date.goto(0, 120)
            self.t_date.write(
                now.strftime("%a. %Y.%m.%d"),
                align="center",
                font=("Arial", 12, "bold")
            )
        self.t.clear()
        self.heure, self.minute, self.seconde = now.hour, now.minute, now.second
        construire_nombre(extraire_unite(self.heure)[0], 0)
        construire_nombre(extraire_unite(self.heure)[1], 45)
        construire2points(-55)
        construire_nombre(extraire_unite(self.minute)[0], 110)
        construire_nombre(extraire_unite(self.minute)[1], 155)
        construire2points(55)
        construire_nombre(extraire_unite(self.seconde)[0], 215)
        construire_nombre(extraire_unite(self.seconde)[1], 260)
        if self.alarm.check(self.heure, self.minute):
            if not self.ringing:
                self.ringing = True
                try:
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play(2)
                except: self.root.bell()
        self.screen.update()
        self.root.after(1000, self.affiche_heure)
        
app = ClockApp()
app.affiche_heure()
app.root.mainloop()

