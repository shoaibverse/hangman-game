import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os
import threading
import time

try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


THEMES = {
    "Dark": {
        "bg": "#0F0E17", "card": "#1A1A2E", "card_light": "#252542",
        "primary": "#6C5CE7", "primary_hover": "#A29BFE",
        "success": "#00B894", "success_hover": "#00CEC9",
        "danger": "#FF6B6B", "danger_hover": "#FF8787",
        "text": "#FFFFFE", "text_dim": "#A7A9BE",
        "gold": "#FFD93D", "accent": "#FF006E",
        "glow": "#6C5CE7", "shadow": "#000000"
    },
    "Light": {
        "bg": "#F5F5F7", "card": "#FFFFFF", "card_light": "#EAEAEC",
        "primary": "#5E60CE", "primary_hover": "#7B7EDB",
        "success": "#06A77D", "success_hover": "#0AC48C",
        "danger": "#E63946", "danger_hover": "#F26571",
        "text": "#1D1D1F", "text_dim": "#6E6E73",
        "gold": "#F4A261", "accent": "#E91E63",
        "glow": "#5E60CE", "shadow": "#BFBFBF"
    },
    "Neon": {
        "bg": "#0A0A0A", "card": "#151515", "card_light": "#1F1F1F",
        "primary": "#00FFFF", "primary_hover": "#00E5E5",
        "success": "#39FF14", "success_hover": "#66FF33",
        "danger": "#FF073A", "danger_hover": "#FF3355",
        "text": "#FFFFFF", "text_dim": "#B0B0B0",
        "gold": "#FFFF00", "accent": "#FF00FF",
        "glow": "#00FFFF", "shadow": "#000000"
    },
    "Retro": {
        "bg": "#2B2B2B", "card": "#3E2723", "card_light": "#5D4037",
        "primary": "#FF7043", "primary_hover": "#FF8A65",
        "success": "#8BC34A", "success_hover": "#AED581",
        "danger": "#D84315", "danger_hover": "#F4511E",
        "text": "#FFF3E0", "text_dim": "#BCAAA4",
        "gold": "#FFB300", "accent": "#EF5350",
        "glow": "#FF7043", "shadow": "#1B1B1B"
    }
}


ACHIEVEMENTS = {
    "first_win":      {"name": "First Victory",    "desc": "Win your first game",           "emoji": "🎉", "req": lambda s: s["wins"] >= 1},
    "streak_3":       {"name": "On Fire!",         "desc": "Win 3 in a row",                "emoji": "🔥", "req": lambda s: s["best_streak"] >= 3},
    "streak_5":       {"name": "Unstoppable",      "desc": "Win 5 in a row",                "emoji": "⚡", "req": lambda s: s["best_streak"] >= 5},
    "streak_10":      {"name": "Legendary",        "desc": "Win 10 in a row",               "emoji": "👑", "req": lambda s: s["best_streak"] >= 10},
    "wins_10":        {"name": "Word Master",      "desc": "Win 10 total games",            "emoji": "📚", "req": lambda s: s["wins"] >= 10},
    "wins_25":        {"name": "Vocabulary King",  "desc": "Win 25 total games",            "emoji": "🎓", "req": lambda s: s["wins"] >= 25},
    "wins_50":        {"name": "Hangman Hero",     "desc": "Win 50 total games",            "emoji": "🦸", "req": lambda s: s["wins"] >= 50},
    "survivor":       {"name": "Survivor",         "desc": "Play 10 games total",           "emoji": "🎯", "req": lambda s: (s["wins"] + s["losses"]) >= 10},
    "perfectionist":  {"name": "Perfectionist",    "desc": "Win a Hard difficulty game",    "emoji": "💎", "req": lambda s: s.get("hard_wins", 0) >= 1},
    "veteran":        {"name": "Veteran",          "desc": "Play 50 games total",           "emoji": "🎖️", "req": lambda s: (s["wins"] + s["losses"]) >= 50},
}


class MusicPlayer:
    def __init__(self):
        self.playing = False
        self.thread = None
        self.melody = [
            (523, 200), (659, 200), (784, 200), (659, 200),
            (523, 200), (784, 400), (659, 400),
        ]
    
    def start(self):
        if not SOUND_AVAILABLE or self.playing:
            return
        self.playing = True
        self.thread = threading.Thread(target=self._play_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.playing = False
    
    def _play_loop(self):
        while self.playing:
            for freq, duration in self.melody:
                if not self.playing:
                    break
                try:
                    winsound.Beep(freq, duration)
                    time.sleep(0.05)
                except Exception:
                    pass
            time.sleep(1.5)


class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command, width=60, height=60,
                 bg_color="#6C5CE7", hover_color="#A29BFE",
                 glow_color=None, text_color="white", font_size=14,
                 rounded=15, parent_bg=None, **kwargs):
        pb = parent_bg if parent_bg else parent["bg"]
        super().__init__(parent, width=width+12, height=height+12,
                         highlightthickness=0, bg=pb, **kwargs)
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.glow_color = glow_color if glow_color else bg_color
        self.current_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.rounded = rounded
        self.enabled = True
        self.pressed = False
        self.hovering = False
        self.draw_button()
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def draw_rounded_rect(self, x1, y1, x2, y2, radius, color):
        self.create_oval(x1, y1, x1+radius*2, y1+radius*2, fill=color, outline="")
        self.create_oval(x2-radius*2, y1, x2, y1+radius*2, fill=color, outline="")
        self.create_oval(x1, y2-radius*2, x1+radius*2, y2, fill=color, outline="")
        self.create_oval(x2-radius*2, y2-radius*2, x2, y2, fill=color, outline="")
        self.create_rectangle(x1+radius, y1, x2-radius, y2, fill=color, outline="")
        self.create_rectangle(x1, y1+radius, x2, y2-radius, fill=color, outline="")
    
    def draw_button(self):
        self.delete("all")
        offset = 1 if self.pressed else 0
        if self.enabled:
            glow_intensity = 2 if self.hovering else 1
            for i in range(glow_intensity, 0, -1):
                glow_hex = self.blend_color(self.glow_color, "#000000", i * 0.3)
                self.draw_rounded_rect(
                    6-i*2, 6-i*2, self.width+6+i*2, self.height+6+i*2,
                    self.rounded+i*2, glow_hex)
        if not self.pressed and self.enabled:
            self.draw_rounded_rect(7, 9, self.width+7, self.height+9,
                                    self.rounded, "#000000")
        self.draw_rounded_rect(6+offset, 6+offset,
                                self.width+6+offset, self.height+6+offset,
                                self.rounded, self.current_color)
        if self.enabled and not self.pressed:
            highlight = self.lighten_color(self.current_color, 40)
            self.create_oval(9+offset, 8+offset,
                             self.width+3+offset, self.height//2+4+offset,
                             fill=highlight, outline="")
        self.create_text(self.width//2 + 6 + offset,
                         self.height//2 + 6 + offset,
                         text=self.text, fill=self.text_color,
                         font=("Segoe UI", self.font_size, "bold"))
    
    def blend_color(self, c1, c2, ratio):
        c1 = c1.lstrip('#'); c2 = c2.lstrip('#')
        r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
        r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
        r = int(r1 * (1-ratio) + r2 * ratio)
        g = int(g1 * (1-ratio) + g2 * ratio)
        b = int(b1 * (1-ratio) + b2 * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def lighten_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, c + amount) for c in rgb)
        return '#%02x%02x%02x' % rgb
    
    def on_hover(self, event):
        if self.enabled:
            self.hovering = True
            self.current_color = self.hover_color
            self.draw_button()
            self.config(cursor="hand2")
    
    def on_leave(self, event):
        if self.enabled:
            self.hovering = False
            self.current_color = self.bg_color
            self.pressed = False
            self.draw_button()
    
    def on_press(self, event):
        if self.enabled:
            self.pressed = True
            self.draw_button()
    
    def on_release(self, event):
        if self.enabled:
            self.pressed = False
            self.draw_button()
            if self.command:
                self.command()
    
    def disable(self, new_color=None):
        self.enabled = False
        if new_color:
            self.bg_color = new_color
            self.hover_color = new_color
            self.glow_color = new_color
            self.current_color = new_color
        self.config(cursor="")
        self.draw_button()
    
    def enable(self, bg=None, hover=None, glow=None):
        self.enabled = True
        if bg: self.bg_color = bg; self.current_color = bg
        if hover: self.hover_color = hover
        if glow: self.glow_color = glow
        self.draw_button()
    
    def update_colors(self, bg, hover, glow):
        self.bg_color = bg; self.hover_color = hover; self.glow_color = glow
        self.current_color = bg; self.draw_button()
    
    def update_bg(self, new_bg):
        self.config(bg=new_bg)


class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 HANGMAN ULTIMATE")
        
        # ✅ AUTO-FIT: Screen ke according size set karo
        screen_h = self.root.winfo_screenheight()
        screen_w = self.root.winfo_screenwidth()
        win_h = min(screen_h - 80, 680)
        win_w = min(screen_w - 50, 720)
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.resizable(True, True)
        
        self.current_theme = "Dark"
        self.colors = THEMES[self.current_theme]
        self.root.configure(bg=self.colors["bg"])
        
        self.word_bank = {
            "Easy":   ["cat", "dog", "sun", "book", "tree", "fish", "star", "moon", "cake", "bird"],
            "Medium": ["python", "hangman", "guitar", "planet", "rocket", "orange", "school", "castle", "dragon"],
            "Hard":   ["programming", "javascript", "encyclopedia", "algorithm", "developer", "artificial", "philosophy"]
        }
        
        self.score_file = "hangman_scores.json"
        self.scores = self.load_scores()
        self.unlocked_achievements = set(self.scores.get("achievements", []))
        
        self.current_difficulty = "Medium"
        self.sound_on = True
        self.music_on = False
        self.music_player = MusicPlayer()
        
        self.setup_ui()
        self.new_game()
        self.check_achievements()
    
    def setup_ui(self):
        # ========== HEADER (compact) ==========
        self.header_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.header_frame.pack(fill="x", pady=(4, 1))
        
        self.title = tk.Label(
            self.header_frame, text="🎮 HANGMAN ULTIMATE",
            font=("Segoe UI", 16, "bold"),
            bg=self.colors["bg"], fg=self.colors["gold"]
        )
        self.title.pack()
        
        # ========== CONTROL BAR ==========
        self.control_card = tk.Frame(self.root, bg=self.colors["card"])
        self.control_card.pack(pady=2, padx=15, fill="x")
        
        self.control_inner = tk.Frame(self.control_card, bg=self.colors["card"])
        self.control_inner.pack(pady=4, padx=8)
        
        self.theme_lbl = tk.Label(self.control_inner, text="🎨", font=("Segoe UI", 10),
                                   bg=self.colors["card"], fg=self.colors["text_dim"])
        self.theme_lbl.pack(side="left", padx=(0, 2))
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_menu = ttk.Combobox(
            self.control_inner, textvariable=self.theme_var,
            values=list(THEMES.keys()), state="readonly",
            width=7, font=("Segoe UI", 8, "bold")
        )
        self.theme_menu.pack(side="left", padx=2)
        self.theme_menu.bind("<<ComboboxSelected>>", self.change_theme)
        
        self.diff_lbl = tk.Label(self.control_inner, text=" 🎚️", font=("Segoe UI", 10),
                                  bg=self.colors["card"], fg=self.colors["text_dim"])
        self.diff_lbl.pack(side="left", padx=(6, 2))
        
        self.difficulty_var = tk.StringVar(value=self.current_difficulty)
        self.difficulty_menu = ttk.Combobox(
            self.control_inner, textvariable=self.difficulty_var,
            values=["Easy", "Medium", "Hard"], state="readonly",
            width=7, font=("Segoe UI", 8, "bold")
        )
        self.difficulty_menu.pack(side="left", padx=2)
        self.difficulty_menu.bind("<<ComboboxSelected>>", self.change_difficulty)
        
        self.sound_btn = NeonButton(
            self.control_inner, text="🔊", command=self.toggle_sound,
            width=32, height=24, bg_color=self.colors["success"],
            hover_color=self.colors["success_hover"], glow_color=self.colors["success"],
            font_size=10, rounded=6, parent_bg=self.colors["card"]
        )
        self.sound_btn.pack(side="left", padx=(8, 2))
        
        self.music_btn = NeonButton(
            self.control_inner, text="🎵", command=self.toggle_music,
            width=32, height=24, bg_color="#636E72",
            hover_color="#B2BEC3", glow_color="#636E72",
            font_size=10, rounded=6, parent_bg=self.colors["card"]
        )
        self.music_btn.pack(side="left", padx=2)
        
        self.achievement_btn = NeonButton(
            self.control_inner, text="🏅", command=self.show_achievements,
            width=32, height=24, bg_color=self.colors["gold"],
            hover_color=self.colors["primary_hover"], glow_color=self.colors["gold"],
            font_size=10, rounded=6, parent_bg=self.colors["card"]
        )
        self.achievement_btn.pack(side="left", padx=2)
        
        # ========== STATS ==========
        self.score_card = tk.Frame(self.root, bg=self.colors["card"])
        self.score_card.pack(pady=2, padx=15, fill="x")
        
        self.stats_frame = tk.Frame(self.score_card, bg=self.colors["card"])
        self.stats_frame.pack(pady=4, padx=8)
        
        self.stat_labels = {}
        self.stat_boxes = []
        self.stat_emojis = {}
        self.stat_desc = {}
        
        stats = [
            ("wins", "🏆", "Wins", "success"),
            ("losses", "💀", "Loss", "danger"),
            ("streak", "🔥", "Streak", "accent"),
            ("best_streak", "⭐", "Best", "gold"),
            ("winrate", "📊", "Win%", "primary_hover"),
            ("badges", "🏅", "Badge", "gold")
        ]
        
        for i, (key, emoji, label, color_key) in enumerate(stats):
            box = tk.Frame(self.stats_frame, bg=self.colors["card_light"], padx=6, pady=2)
            box.grid(row=0, column=i, padx=2)
            self.stat_boxes.append((box, color_key))
            
            em_lbl = tk.Label(box, text=emoji, font=("Segoe UI", 10),
                     bg=self.colors["card_light"], fg=self.colors[color_key])
            em_lbl.pack()
            self.stat_emojis[key] = em_lbl
            
            value_label = tk.Label(box, text="0", font=("Segoe UI", 10, "bold"),
                                    bg=self.colors["card_light"], fg=self.colors[color_key])
            value_label.pack()
            
            desc_lbl = tk.Label(box, text=label, font=("Segoe UI", 7),
                     bg=self.colors["card_light"], fg=self.colors["text_dim"])
            desc_lbl.pack()
            self.stat_desc[key] = desc_lbl
            
            self.stat_labels[key] = value_label
        
        # ========== CANVAS (CHHOTA) ==========
        self.canvas_frame = tk.Frame(self.root, bg=self.colors["card"])
        self.canvas_frame.pack(pady=2)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, width=240, height=140,
            bg=self.colors["card_light"], highlightthickness=2,
            highlightbackground=self.colors["glow"]
        )
        self.canvas.pack(padx=2, pady=2)
        
        # ========== WORD DISPLAY ==========
        self.word_card = tk.Frame(self.root, bg=self.colors["card"])
        self.word_card.pack(pady=2, padx=15, fill="x")
        
        self.word_label = tk.Label(
            self.word_card, text="", font=("Consolas", 20, "bold"),
            bg=self.colors["card"], fg=self.colors["gold"], pady=4
        )
        self.word_label.pack()
        
        # ========== INFO BAR ==========
        self.info_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.info_frame.pack(pady=1)
        
        self.lives_label = tk.Label(
            self.info_frame, text="", font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"], fg=self.colors["danger"]
        )
        self.lives_label.pack(side="left", padx=8)
        
        self.difficulty_label = tk.Label(
            self.info_frame, text="", font=("Segoe UI", 10, "bold"),
            bg=self.colors["bg"], fg=self.colors["primary_hover"]
        )
        self.difficulty_label.pack(side="left", padx=8)
        
        # ========== KEYBOARD (CHHOTE BUTTONS) ==========
        self.keyboard_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.keyboard_frame.pack(pady=2)
        self.create_keyboard()
        
        # ========== ACTION BUTTONS ==========
        self.action_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.action_frame.pack(pady=3)
        
        self.new_game_btn = NeonButton(
            self.action_frame, text="🎮 NEW", command=self.new_game,
            width=100, height=32, bg_color=self.colors["success"],
            hover_color=self.colors["success_hover"], glow_color=self.colors["success"],
            font_size=10, rounded=10, parent_bg=self.colors["bg"]
        )
        self.new_game_btn.pack(side="left", padx=5)
        
        self.reset_btn = NeonButton(
            self.action_frame, text="🗑️ RESET", command=self.reset_scores,
            width=100, height=32, bg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"], glow_color=self.colors["danger"],
            font_size=10, rounded=10, parent_bg=self.colors["bg"]
        )
        self.reset_btn.pack(side="left", padx=5)
        
        self.update_score_display()
    
    def create_keyboard(self):
        self.buttons = {}
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        
        for row in rows:
            frame = tk.Frame(self.keyboard_frame, bg=self.colors["bg"])
            frame.pack(pady=0)
            for letter in row:
                btn = NeonButton(
                    frame, text=letter,
                    command=lambda l=letter: self.guess_letter(l.lower()),
                    width=30, height=30,
                    bg_color=self.colors["primary"],
                    hover_color=self.colors["primary_hover"],
                    glow_color=self.colors["glow"],
                    font_size=10, rounded=6, parent_bg=self.colors["bg"]
                )
                btn.pack(side="left", padx=1)
                self.buttons[letter.lower()] = btn
    
    def change_theme(self, event=None):
        self.current_theme = self.theme_var.get()
        self.colors = THEMES[self.current_theme]
        self.apply_theme()
    
    def apply_theme(self):
        c = self.colors
        self.root.configure(bg=c["bg"])
        
        self.header_frame.configure(bg=c["bg"])
        self.control_card.configure(bg=c["card"])
        self.control_inner.configure(bg=c["card"])
        self.score_card.configure(bg=c["card"])
        self.stats_frame.configure(bg=c["card"])
        self.canvas_frame.configure(bg=c["card"])
        self.word_card.configure(bg=c["card"])
        self.info_frame.configure(bg=c["bg"])
        self.keyboard_frame.configure(bg=c["bg"])
        self.action_frame.configure(bg=c["bg"])
        
        self.title.configure(bg=c["bg"], fg=c["gold"])
        self.theme_lbl.configure(bg=c["card"], fg=c["text_dim"])
        self.diff_lbl.configure(bg=c["card"], fg=c["text_dim"])
        self.word_label.configure(bg=c["card"], fg=c["gold"])
        self.lives_label.configure(bg=c["bg"], fg=c["danger"])
        self.difficulty_label.configure(bg=c["bg"], fg=c["primary_hover"])
        
        for i, (box, color_key) in enumerate(self.stat_boxes):
            box.configure(bg=c["card_light"])
            for child in box.winfo_children():
                child.configure(bg=c["card_light"])
        
        for key, lbl in self.stat_labels.items():
            for i, (box, color_key) in enumerate(self.stat_boxes):
                if lbl.master == box:
                    lbl.configure(fg=c[color_key])
                    self.stat_emojis[key].configure(fg=c[color_key])
                    self.stat_desc[key].configure(fg=c["text_dim"])
                    break
        
        self.canvas.configure(bg=c["card_light"], highlightbackground=c["glow"])
        
        for btn in self.buttons.values():
            btn.update_bg(c["bg"])
            btn.update_colors(c["primary"], c["primary_hover"], c["glow"])
        
        self.new_game_btn.update_bg(c["bg"])
        self.new_game_btn.update_colors(c["success"], c["success_hover"], c["success"])
        self.reset_btn.update_bg(c["bg"])
        self.reset_btn.update_colors(c["danger"], c["danger_hover"], c["danger"])
        
        self.sound_btn.update_bg(c["card"])
        if self.sound_on:
            self.sound_btn.update_colors(c["success"], c["success_hover"], c["success"])
        else:
            self.sound_btn.update_colors("#636E72", "#B2BEC3", "#636E72")
        
        self.music_btn.update_bg(c["card"])
        if self.music_on:
            self.music_btn.update_colors(c["accent"], c["primary_hover"], c["accent"])
        else:
            self.music_btn.update_colors("#636E72", "#B2BEC3", "#636E72")
        
        self.achievement_btn.update_bg(c["card"])
        self.achievement_btn.update_colors(c["gold"], c["primary_hover"], c["gold"])
        
        self.canvas.delete("all")
        self.draw_gallows()
        temp = self.incorrect_guesses
        for i in range(1, temp + 1):
            self.incorrect_guesses = i
            self.draw_hangman()
        self.incorrect_guesses = temp
    
    def play_sound(self, sound_type):
        if not self.sound_on or not SOUND_AVAILABLE:
            return
        try:
            if sound_type == "correct":
                winsound.Beep(880, 100)
            elif sound_type == "wrong":
                winsound.Beep(220, 200)
            elif sound_type == "win":
                for freq in [523, 659, 784, 1046]:
                    winsound.Beep(freq, 80)
            elif sound_type == "lose":
                for freq in [400, 350, 300, 200]:
                    winsound.Beep(freq, 150)
            elif sound_type == "achievement":
                for freq in [800, 1000, 1200, 1500]:
                    winsound.Beep(freq, 70)
        except Exception:
            pass
    
    def toggle_sound(self):
        self.sound_on = not self.sound_on
        c = self.colors
        if self.sound_on:
            self.sound_btn.text = "🔊"
            self.sound_btn.update_colors(c["success"], c["success_hover"], c["success"])
        else:
            self.sound_btn.text = "🔇"
            self.sound_btn.update_colors("#636E72", "#B2BEC3", "#636E72")
    
    def toggle_music(self):
        self.music_on = not self.music_on
        c = self.colors
        if self.music_on:
            self.music_btn.text = "🎶"
            self.music_btn.update_colors(c["accent"], c["primary_hover"], c["accent"])
            self.music_player.start()
        else:
            self.music_btn.text = "🎵"
            self.music_btn.update_colors("#636E72", "#B2BEC3", "#636E72")
            self.music_player.stop()
    
    def load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0,
                "hard_wins": 0, "achievements": []}
    
    def save_scores(self):
        try:
            self.scores["achievements"] = list(self.unlocked_achievements)
            with open(self.score_file, "w") as f:
                json.dump(self.scores, f)
        except Exception:
            pass
    
    def update_score_display(self):
        total = self.scores["wins"] + self.scores["losses"]
        winrate = (self.scores["wins"] / total * 100) if total > 0 else 0
        self.stat_labels["wins"].config(text=str(self.scores["wins"]))
        self.stat_labels["losses"].config(text=str(self.scores["losses"]))
        self.stat_labels["streak"].config(text=str(self.scores["streak"]))
        self.stat_labels["best_streak"].config(text=str(self.scores["best_streak"]))
        self.stat_labels["winrate"].config(text=f"{winrate:.0f}%")
        self.stat_labels["badges"].config(text=f"{len(self.unlocked_achievements)}/{len(ACHIEVEMENTS)}")
    
    def reset_scores(self):
        if messagebox.askyesno("⚠️ Reset", "Erase ALL stats & achievements?"):
            self.scores = {"wins": 0, "losses": 0, "streak": 0, "best_streak": 0,
                           "hard_wins": 0, "achievements": []}
            self.unlocked_achievements = set()
            self.save_scores()
            self.update_score_display()
    
    def check_achievements(self):
        newly_unlocked = []
        for key, ach in ACHIEVEMENTS.items():
            if key not in self.unlocked_achievements and ach["req"](self.scores):
                self.unlocked_achievements.add(key)
                newly_unlocked.append(ach)
        if newly_unlocked:
            self.save_scores()
            self.update_score_display()
            for ach in newly_unlocked:
                self.show_achievement_popup(ach)
    
    def show_achievement_popup(self, ach):
        self.play_sound("achievement")
        popup = tk.Toplevel(self.root)
        popup.title("Achievement!")
        popup.geometry("320x130")
        popup.configure(bg=self.colors["card"])
        popup.resizable(False, False)
        popup.transient(self.root)
        
        tk.Label(popup, text="🎊 UNLOCKED 🎊",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["gold"]).pack(pady=(8, 2))
        tk.Label(popup, text=ach["emoji"], font=("Segoe UI", 24),
                 bg=self.colors["card"]).pack()
        tk.Label(popup, text=ach["name"], font=("Segoe UI", 11, "bold"),
                 bg=self.colors["card"], fg=self.colors["primary_hover"]).pack()
        tk.Label(popup, text=ach["desc"], font=("Segoe UI", 8),
                 bg=self.colors["card"], fg=self.colors["text_dim"]).pack(pady=(0, 3))
        popup.after(3000, popup.destroy)
    
    def show_achievements(self):
        popup = tk.Toplevel(self.root)
        popup.title("🏅 Achievements")
        popup.geometry("420x450")
        popup.configure(bg=self.colors["bg"])
        popup.transient(self.root)
        
        tk.Label(popup, text="🏅 ACHIEVEMENTS 🏅",
                 font=("Segoe UI", 14, "bold"),
                 bg=self.colors["bg"], fg=self.colors["gold"]).pack(pady=8)
        tk.Label(popup, text=f"Unlocked: {len(self.unlocked_achievements)}/{len(ACHIEVEMENTS)}",
                 font=("Segoe UI", 9),
                 bg=self.colors["bg"], fg=self.colors["text_dim"]).pack()
        
        canvas = tk.Canvas(popup, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=400)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=8, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        for key, ach in ACHIEVEMENTS.items():
            unlocked = key in self.unlocked_achievements
            bg = self.colors["card"] if unlocked else self.colors["card_light"]
            fg = self.colors["gold"] if unlocked else self.colors["text_dim"]
            row = tk.Frame(scroll_frame, bg=bg, pady=4, padx=8)
            row.pack(fill="x", pady=2, padx=3)
            emoji = ach["emoji"] if unlocked else "🔒"
            tk.Label(row, text=emoji, font=("Segoe UI", 16), bg=bg).pack(side="left", padx=(0, 6))
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=ach["name"], font=("Segoe UI", 10, "bold"), bg=bg, fg=fg, anchor="w").pack(fill="x")
            tk.Label(info, text=ach["desc"], font=("Segoe UI", 8), bg=bg, fg=self.colors["text_dim"], anchor="w").pack(fill="x")
    
    def change_difficulty(self, event=None):
        self.current_difficulty = self.difficulty_var.get()
        self.new_game()
    
    def new_game(self):
        self.secret_word = random.choice(self.word_bank[self.current_difficulty])
        self.guessed_letters = []
        self.incorrect_guesses = 0
        self.max_incorrect = {"Easy": 8, "Medium": 6, "Hard": 5}[self.current_difficulty]
        self.game_over = False
        
        c = self.colors
        for btn in self.buttons.values():
            btn.enable(bg=c["primary"], hover=c["primary_hover"], glow=c["glow"])
        
        self.canvas.delete("all")
        self.draw_gallows()
        self.update_display()
    
    def guess_letter(self, letter):
        if self.game_over or letter in self.guessed_letters:
            return
        self.guessed_letters.append(letter)
        btn = self.buttons[letter]
        
        if letter in self.secret_word:
            btn.disable(new_color=self.colors["success"])
            self.play_sound("correct")
        else:
            btn.disable(new_color=self.colors["danger"])
            self.incorrect_guesses += 1
            self.play_sound("wrong")
            self.draw_hangman()
        
        self.update_display()
        self.check_game_status()
    
    def update_display(self):
        display = "  ".join(
            [l.upper() if l in self.guessed_letters else "•" for l in self.secret_word]
        )
        self.word_label.config(text=display)
        
        lives = self.max_incorrect - self.incorrect_guesses
        hearts = "❤️" * lives + "🖤" * self.incorrect_guesses
        self.lives_label.config(text=hearts)
        
        diff_emoji = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}[self.current_difficulty]
        self.difficulty_label.config(text=f"{diff_emoji} {self.current_difficulty}")
    
    def check_game_status(self):
        if all(l in self.guessed_letters for l in self.secret_word):
            self.game_over = True
            self.scores["wins"] += 1
            self.scores["streak"] += 1
            if self.current_difficulty == "Hard":
                self.scores["hard_wins"] = self.scores.get("hard_wins", 0) + 1
            if self.scores["streak"] > self.scores["best_streak"]:
                self.scores["best_streak"] = self.scores["streak"]
            self.save_scores()
            self.update_score_display()
            self.play_sound("win")
            self.check_achievements()
            self.root.after(400, lambda: messagebox.showinfo(
                "🎉 VICTORY!",
                f"🏆 Champion! 🏆\n\nWord: {self.secret_word.upper()}\n"
                f"🔥 Streak: {self.scores['streak']}\n⭐ Best: {self.scores['best_streak']}"))
        elif self.incorrect_guesses >= self.max_incorrect:
            self.game_over = True
            self.scores["losses"] += 1
            self.scores["streak"] = 0
            self.save_scores()
            self.update_score_display()
            self.play_sound("lose")
            self.check_achievements()
            self.root.after(400, lambda: messagebox.showerror(
                "💀 GAME OVER",
                f"Better luck next time!\n\nThe word was: {self.secret_word.upper()}"))
    
    def draw_gallows(self):
        c = self.canvas
        col = self.colors
        c.create_rectangle(0, 125, 240, 140, fill="#3D3D5C", outline="")
        c.create_line(0, 125, 240, 125, fill=col["gold"], width=2)
        c.create_rectangle(25, 118, 115, 125, fill="#8B4513", outline="#654321", width=2)
        c.create_rectangle(50, 15, 60, 118, fill="#A0522D", outline="#654321", width=2)
        c.create_rectangle(50, 15, 145, 25, fill="#A0522D", outline="#654321", width=2)
        c.create_line(60, 35, 85, 15, fill="#654321", width=3)
        c.create_line(140, 25, 140, 42, fill="#D4A574", width=3)
        c.create_oval(137, 40, 143, 46, fill="#8B4513", outline="")
    
    def draw_hangman(self):
        c = self.canvas
        parts = self.incorrect_guesses
        skin = "#FFDBAC"
        clothes = self.colors["primary"]
        
        if parts == 1:
            c.create_oval(125, 45, 155, 75, fill=skin, outline="#2C3E50", width=2)
            c.create_oval(131, 55, 136, 60, fill="white", outline="black")
            c.create_oval(144, 55, 149, 60, fill="white", outline="black")
            c.create_oval(133, 57, 134, 58, fill="black")
            c.create_oval(146, 57, 147, 58, fill="black")
            c.create_line(136, 68, 144, 68, fill="black", width=2)
        elif parts == 2:
            c.create_rectangle(136, 75, 144, 110, fill=clothes, outline="#2C3E50", width=2)
        elif parts == 3:
            c.create_line(140, 82, 120, 102, fill=clothes, width=4, capstyle="round")
            c.create_oval(116, 99, 125, 108, fill=skin, outline="#2C3E50", width=1)
        elif parts == 4:
            c.create_line(140, 82, 160, 102, fill=clothes, width=4, capstyle="round")
            c.create_oval(157, 99, 166, 108, fill=skin, outline="#2C3E50", width=1)
        elif parts == 5:
            c.create_line(138, 110, 125, 123, fill="#2D3436", width=4, capstyle="round")
            c.create_oval(120, 120, 130, 128, fill="#000", outline="#2C3E50", width=1)
        elif parts == 6:
            c.create_line(142, 110, 155, 123, fill="#2D3436", width=4, capstyle="round")
            c.create_oval(152, 120, 162, 128, fill="#000", outline="#2C3E50", width=1)
            c.create_line(131, 55, 136, 60, fill="red", width=2)
            c.create_line(136, 55, 131, 60, fill="red", width=2)
            c.create_line(144, 55, 149, 60, fill="red", width=2)
            c.create_line(149, 55, 144, 60, fill="red", width=2)
            c.create_arc(134, 63, 146, 71, start=0, extent=180, style="arc", outline="black", width=2)


if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()