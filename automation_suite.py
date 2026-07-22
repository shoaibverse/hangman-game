import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
import os
import shutil
import re
import requests
from datetime import datetime
import threading


# ==================== THEME ====================
COLORS = {
    "bg": "#0A0E27",
    "card": "#141B3D",
    "card_light": "#1E2650",
    "primary": "#00D9FF",
    "primary_hover": "#40E5FF",
    "success": "#00FF88",
    "success_hover": "#33FFAA",
    "danger": "#FF3860",
    "danger_hover": "#FF5C7C",
    "warning": "#FFB800",
    "gold": "#FFD700",
    "text": "#FFFFFF",
    "text_dim": "#8A93B8",
    "accent": "#B026FF",
    "accent_hover": "#C455FF",
    "glow_cyan": "#00D9FF",
    "glow_pink": "#FF00E5",
    "glow_green": "#00FF88",
    "glow_orange": "#FF8C00"
}


# ==================== NEON BUTTON ====================
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, command, width=100, height=40,
                 bg_color=None, hover_color=None, glow_color=None,
                 text_color="white", font_size=11, rounded=12,
                 parent_bg=None, **kwargs):
        pb = parent_bg if parent_bg else parent["bg"]
        super().__init__(parent, width=width+16, height=height+16,
                         highlightthickness=0, bg=pb, **kwargs)
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.bg_color = bg_color or COLORS["primary"]
        self.hover_color = hover_color or COLORS["primary_hover"]
        self.glow_color = glow_color or self.bg_color
        self.current_color = self.bg_color
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
            glow_intensity = 3 if self.hovering else 2
            for i in range(glow_intensity, 0, -1):
                glow_hex = self.blend_color(self.glow_color, "#000000", i * 0.3)
                self.draw_rounded_rect(
                    8-i*2, 8-i*2, self.width+8+i*2, self.height+8+i*2,
                    self.rounded+i*2, glow_hex)
        if not self.pressed and self.enabled:
            self.draw_rounded_rect(10, 12, self.width+10, self.height+12,
                                    self.rounded, "#000000")
        self.draw_rounded_rect(8+offset, 8+offset,
                                self.width+8+offset, self.height+8+offset,
                                self.rounded, self.current_color)
        if self.enabled and not self.pressed:
            highlight = self.lighten_color(self.current_color, 40)
            self.create_oval(12+offset, 10+offset,
                             self.width+4+offset, self.height//2+6+offset,
                             fill=highlight, outline="")
        self.create_text(self.width//2 + 8 + offset,
                         self.height//2 + 8 + offset,
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


# ==================== MAIN APP ====================
class AutomationSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 AUTOMATION SUITE — PREMIUM")
        
        screen_h = self.root.winfo_screenheight()
        win_h = min(screen_h - 80, 780)
        self.root.geometry(f"900x{win_h}")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        
        self.current_task = 1
        self.setup_ui()
        self.animate_title()
        self.show_task(1)
    
    def setup_ui(self):
        # ========== HEADER ==========
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.pack(fill="x", pady=(15, 5))
        
        self.title_label = tk.Label(
            header, text="🤖 AUTOMATION SUITE",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg"], fg=COLORS["primary"]
        )
        self.title_label.pack()
        
        tk.Label(
            header, text="◆ Automate • Extract • Scrape ◆",
            font=("Segoe UI", 10, "italic"),
            bg=COLORS["bg"], fg=COLORS["text_dim"]
        ).pack()
        
        # ========== TASK TABS ==========
        tabs_frame = tk.Frame(self.root, bg=COLORS["bg"])
        tabs_frame.pack(pady=15)
        
        self.tab_buttons = []
        
        tab1 = NeonButton(
            tabs_frame, text="📁 FILE MOVER", command=lambda: self.show_task(1),
            width=180, height=42,
            bg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            glow_color=COLORS["glow_cyan"],
            font_size=11, rounded=14, parent_bg=COLORS["bg"]
        )
        tab1.pack(side="left", padx=8)
        self.tab_buttons.append(tab1)
        
        tab2 = NeonButton(
            tabs_frame, text="📧 EMAIL EXTRACTOR", command=lambda: self.show_task(2),
            width=200, height=42,
            bg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            glow_color=COLORS["glow_pink"],
            font_size=11, rounded=14, parent_bg=COLORS["bg"]
        )
        tab2.pack(side="left", padx=8)
        self.tab_buttons.append(tab2)
        
        tab3 = NeonButton(
            tabs_frame, text="🌐 WEB SCRAPER", command=lambda: self.show_task(3),
            width=180, height=42,
            bg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            glow_color=COLORS["glow_green"],
            font_size=11, rounded=14, parent_bg=COLORS["bg"]
        )
        tab3.pack(side="left", padx=8)
        self.tab_buttons.append(tab3)
        
        # ========== CONTENT AREA ==========
        self.content_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.content_frame.pack(pady=10, padx=25, fill="both", expand=True)
        
        # Create all task views
        self.create_task1_view()  # File Mover
        self.create_task2_view()  # Email Extractor
        self.create_task3_view()  # Web Scraper
        
        # ========== STATUS BAR ==========
        self.status_bar = tk.Frame(self.root, bg=COLORS["card"], height=35)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = tk.Label(
            self.status_bar, text="  ✨ Ready to automate...",
            font=("Segoe UI", 10, "italic"),
            bg=COLORS["card"], fg=COLORS["text_dim"]
        )
        self.status_label.pack(side="left", padx=15, pady=8)
    
    # ==================== TASK 1: FILE MOVER ====================
    def create_task1_view(self):
        self.task1_frame = tk.Frame(self.content_frame, bg=COLORS["card"])
        
        # Title
        tk.Label(self.task1_frame, text="📁  FILE MOVER — Organize Files by Type",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["gold"]).pack(pady=(15, 5))
        
        tk.Label(self.task1_frame, text="Move all files with a specific extension from source to destination",
                 font=("Segoe UI", 9, "italic"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(pady=(0, 15))
        
        # Source folder
        src_frame = tk.Frame(self.task1_frame, bg=COLORS["card"])
        src_frame.pack(pady=6, padx=25, fill="x")
        
        tk.Label(src_frame, text="📂 Source Folder:", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["primary"], width=15, anchor="w").pack(side="left", padx=5)
        
        self.src_entry = tk.Entry(src_frame, font=("Segoe UI", 10),
                                    bg=COLORS["card_light"], fg=COLORS["text"],
                                    insertbackground=COLORS["primary"], relief="flat")
        self.src_entry.pack(side="left", padx=5, ipady=6, fill="x", expand=True)
        
        NeonButton(src_frame, text="📁 Browse", command=self.browse_source,
                   width=90, height=32, bg_color=COLORS["primary"],
                   hover_color=COLORS["primary_hover"], glow_color=COLORS["glow_cyan"],
                   font_size=9, rounded=10, parent_bg=COLORS["card"]).pack(side="left", padx=5)
        
        # Destination folder
        dst_frame = tk.Frame(self.task1_frame, bg=COLORS["card"])
        dst_frame.pack(pady=6, padx=25, fill="x")
        
        tk.Label(dst_frame, text="📂 Destination:", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["primary"], width=15, anchor="w").pack(side="left", padx=5)
        
        self.dst_entry = tk.Entry(dst_frame, font=("Segoe UI", 10),
                                    bg=COLORS["card_light"], fg=COLORS["text"],
                                    insertbackground=COLORS["primary"], relief="flat")
        self.dst_entry.pack(side="left", padx=5, ipady=6, fill="x", expand=True)
        
        NeonButton(dst_frame, text="📁 Browse", command=self.browse_dest,
                   width=90, height=32, bg_color=COLORS["primary"],
                   hover_color=COLORS["primary_hover"], glow_color=COLORS["glow_cyan"],
                   font_size=9, rounded=10, parent_bg=COLORS["card"]).pack(side="left", padx=5)
        
        # Extension selector
        ext_frame = tk.Frame(self.task1_frame, bg=COLORS["card"])
        ext_frame.pack(pady=6, padx=25, fill="x")
        
        tk.Label(ext_frame, text="📎 File Type:", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["primary"], width=15, anchor="w").pack(side="left", padx=5)
        
        self.ext_var = tk.StringVar(value=".jpg")
        ext_combo = ttk.Combobox(ext_frame, textvariable=self.ext_var,
                                   values=[".jpg", ".png", ".pdf", ".txt", ".docx", ".mp3", ".mp4", ".zip"],
                                   font=("Segoe UI", 10, "bold"), width=15)
        ext_combo.pack(side="left", padx=5, ipady=4)
        
        # Action buttons
        btn_frame = tk.Frame(self.task1_frame, bg=COLORS["card"])
        btn_frame.pack(pady=15)
        
        NeonButton(btn_frame, text="🔍 PREVIEW", command=self.preview_files,
                   width=140, height=40, bg_color=COLORS["warning"],
                   hover_color="#FFCF33", glow_color=COLORS["glow_orange"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        NeonButton(btn_frame, text="⚡ MOVE FILES", command=self.move_files,
                   width=140, height=40, bg_color=COLORS["success"],
                   hover_color=COLORS["success_hover"], glow_color=COLORS["glow_green"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        # Output log
        log_label = tk.Label(self.task1_frame, text="📋 Activity Log:",
                              font=("Segoe UI", 10, "bold"),
                              bg=COLORS["card"], fg=COLORS["gold"])
        log_label.pack(pady=(5, 3), padx=25, anchor="w")
        
        self.task1_log = scrolledtext.ScrolledText(
            self.task1_frame, height=8, font=("Consolas", 9),
            bg=COLORS["card_light"], fg=COLORS["success"],
            insertbackground=COLORS["primary"], relief="flat", padx=10, pady=8
        )
        self.task1_log.pack(pady=(0, 15), padx=25, fill="both", expand=True)
    
    # ==================== TASK 2: EMAIL EXTRACTOR ====================
    def create_task2_view(self):
        self.task2_frame = tk.Frame(self.content_frame, bg=COLORS["card"])
        
        tk.Label(self.task2_frame, text="📧  EMAIL EXTRACTOR — Extract All Emails",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["gold"]).pack(pady=(15, 5))
        
        tk.Label(self.task2_frame, text="Extract all email addresses from a text file using regex",
                 font=("Segoe UI", 9, "italic"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(pady=(0, 15))
        
        # Input file
        input_frame = tk.Frame(self.task2_frame, bg=COLORS["card"])
        input_frame.pack(pady=6, padx=25, fill="x")
        
        tk.Label(input_frame, text="📄 Input File:", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["accent"], width=15, anchor="w").pack(side="left", padx=5)
        
        self.email_input_entry = tk.Entry(input_frame, font=("Segoe UI", 10),
                                            bg=COLORS["card_light"], fg=COLORS["text"],
                                            insertbackground=COLORS["accent"], relief="flat")
        self.email_input_entry.pack(side="left", padx=5, ipady=6, fill="x", expand=True)
        
        NeonButton(input_frame, text="📁 Browse", command=self.browse_email_input,
                   width=90, height=32, bg_color=COLORS["accent"],
                   hover_color=COLORS["accent_hover"], glow_color=COLORS["glow_pink"],
                   font_size=9, rounded=10, parent_bg=COLORS["card"]).pack(side="left", padx=5)
        
        # Or paste text
        tk.Label(self.task2_frame, text="OR paste text below:",
                 font=("Segoe UI", 9, "italic"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(pady=(10, 3), padx=25, anchor="w")
        
        self.email_text_input = scrolledtext.ScrolledText(
            self.task2_frame, height=5, font=("Consolas", 10),
            bg=COLORS["card_light"], fg=COLORS["text"],
            insertbackground=COLORS["accent"], relief="flat", padx=10, pady=8
        )
        self.email_text_input.pack(pady=5, padx=25, fill="x")
        
        # Buttons
        btn_frame = tk.Frame(self.task2_frame, bg=COLORS["card"])
        btn_frame.pack(pady=12)
        
        NeonButton(btn_frame, text="🔍 EXTRACT", command=self.extract_emails,
                   width=140, height=40, bg_color=COLORS["accent"],
                   hover_color=COLORS["accent_hover"], glow_color=COLORS["glow_pink"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        NeonButton(btn_frame, text="💾 SAVE RESULTS", command=self.save_emails,
                   width=160, height=40, bg_color=COLORS["success"],
                   hover_color=COLORS["success_hover"], glow_color=COLORS["glow_green"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        NeonButton(btn_frame, text="🗑️ CLEAR", command=self.clear_emails,
                   width=100, height=40, bg_color=COLORS["danger"],
                   hover_color=COLORS["danger_hover"], glow_color=COLORS["danger"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        # Results
        result_frame = tk.Frame(self.task2_frame, bg=COLORS["card"])
        result_frame.pack(pady=5, padx=25, fill="x")
        
        tk.Label(result_frame, text="✅ Emails Found:",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["gold"]).pack(side="left")
        
        self.email_count_label = tk.Label(result_frame, text="0",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["success"])
        self.email_count_label.pack(side="left", padx=8)
        
        self.email_results = scrolledtext.ScrolledText(
            self.task2_frame, height=7, font=("Consolas", 10),
            bg=COLORS["card_light"], fg=COLORS["success"],
            insertbackground=COLORS["primary"], relief="flat", padx=10, pady=8
        )
        self.email_results.pack(pady=(3, 15), padx=25, fill="both", expand=True)
        
        self.extracted_emails = []
    
    # ==================== TASK 3: WEB SCRAPER ====================
    def create_task3_view(self):
        self.task3_frame = tk.Frame(self.content_frame, bg=COLORS["card"])
        
        tk.Label(self.task3_frame, text="🌐  WEB SCRAPER — Get Webpage Title",
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["card"], fg=COLORS["gold"]).pack(pady=(15, 5))
        
        tk.Label(self.task3_frame, text="Fetch and extract the title and metadata from any webpage",
                 font=("Segoe UI", 9, "italic"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(pady=(0, 15))
        
        # URL input
        url_frame = tk.Frame(self.task3_frame, bg=COLORS["card"])
        url_frame.pack(pady=8, padx=25, fill="x")
        
        tk.Label(url_frame, text="🔗 URL:", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["success"], width=8, anchor="w").pack(side="left", padx=5)
        
        self.url_entry = tk.Entry(url_frame, font=("Segoe UI", 11),
                                    bg=COLORS["card_light"], fg=COLORS["text"],
                                    insertbackground=COLORS["success"], relief="flat")
        self.url_entry.insert(0, "https://www.python.org")
        self.url_entry.pack(side="left", padx=5, ipady=8, fill="x", expand=True)
        
        # Quick URLs
        quick_frame = tk.Frame(self.task3_frame, bg=COLORS["card"])
        quick_frame.pack(pady=8)
        
        tk.Label(quick_frame, text="⚡ Quick Links:",
                 font=("Segoe UI", 9, "bold"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).pack(side="left", padx=5)
        
        quick_urls = [
            ("Python", "https://www.python.org"),
            ("GitHub", "https://github.com"),
            ("Wikipedia", "https://www.wikipedia.org"),
            ("Google", "https://www.google.com"),
        ]
        
        for name, url in quick_urls:
            btn = tk.Button(quick_frame, text=name, font=("Segoe UI", 9, "bold"),
                            bg=COLORS["card_light"], fg=COLORS["primary"],
                            relief="flat", padx=10, pady=3, cursor="hand2",
                            activebackground=COLORS["primary"], activeforeground="white",
                            command=lambda u=url: self.set_url(u))
            btn.pack(side="left", padx=3)
        
        # Action buttons
        btn_frame = tk.Frame(self.task3_frame, bg=COLORS["card"])
        btn_frame.pack(pady=15)
        
        NeonButton(btn_frame, text="🚀 SCRAPE", command=self.scrape_website,
                   width=140, height=42, bg_color=COLORS["success"],
                   hover_color=COLORS["success_hover"], glow_color=COLORS["glow_green"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        NeonButton(btn_frame, text="💾 SAVE RESULT", command=self.save_scrape,
                   width=160, height=42, bg_color=COLORS["primary"],
                   hover_color=COLORS["primary_hover"], glow_color=COLORS["glow_cyan"],
                   font_size=11, rounded=12, parent_bg=COLORS["card"]).pack(side="left", padx=8)
        
        # Results
        tk.Label(self.task3_frame, text="📄 Results:",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["gold"]).pack(pady=(5, 3), padx=25, anchor="w")
        
        self.scrape_results = scrolledtext.ScrolledText(
            self.task3_frame, height=10, font=("Consolas", 10),
            bg=COLORS["card_light"], fg=COLORS["success"],
            insertbackground=COLORS["primary"], relief="flat", padx=12, pady=10
        )
        self.scrape_results.pack(pady=(0, 15), padx=25, fill="both", expand=True)
        
        self.last_scrape_data = None
    
    # ==================== NAVIGATION ====================
    def show_task(self, task_num):
        self.current_task = task_num
        self.task1_frame.pack_forget()
        self.task2_frame.pack_forget()
        self.task3_frame.pack_forget()
        
        if task_num == 1:
            self.task1_frame.pack(fill="both", expand=True)
            self.update_status("📁 File Mover ready")
        elif task_num == 2:
            self.task2_frame.pack(fill="both", expand=True)
            self.update_status("📧 Email Extractor ready")
        elif task_num == 3:
            self.task3_frame.pack(fill="both", expand=True)
            self.update_status("🌐 Web Scraper ready")
    
    # ==================== ANIMATIONS ====================
    def animate_title(self):
        colors_cycle = [COLORS["primary"], COLORS["accent"],
                        COLORS["success"], COLORS["primary_hover"]]
        current = getattr(self, "_title_idx", 0)
        self.title_label.config(fg=colors_cycle[current % len(colors_cycle)])
        self._title_idx = current + 1
        self.root.after(900, self.animate_title)
    
    def update_status(self, message):
        self.status_label.config(text=f"  {message}")
    
    # ==================== TASK 1: FILE MOVER LOGIC ====================
    def browse_source(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.src_entry.delete(0, tk.END)
            self.src_entry.insert(0, folder)
    
    def browse_dest(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dst_entry.delete(0, tk.END)
            self.dst_entry.insert(0, folder)
    
    def log_task1(self, message, color=None):
        self.task1_log.insert(tk.END, message + "\n")
        self.task1_log.see(tk.END)
        self.task1_log.update()
    
    def preview_files(self):
        src = self.src_entry.get().strip()
        ext = self.ext_var.get().strip()
        
        if not src or not os.path.isdir(src):
            messagebox.showerror("❌ Error", "Select a valid source folder!")
            return
        
        try:
            files = [f for f in os.listdir(src) if f.lower().endswith(ext.lower())]
            self.task1_log.delete(1.0, tk.END)
            self.log_task1(f"🔍 PREVIEW: Found {len(files)} '{ext}' files in:")
            self.log_task1(f"   {src}\n")
            for i, f in enumerate(files, 1):
                self.log_task1(f"   {i}. {f}")
            
            if not files:
                self.log_task1("   ⚠️ No files found with this extension.")
            
            self.update_status(f"🔍 Found {len(files)} files")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def move_files(self):
        src = self.src_entry.get().strip()
        dst = self.dst_entry.get().strip()
        ext = self.ext_var.get().strip()
        
        if not src or not os.path.isdir(src):
            messagebox.showerror("❌ Error", "Select a valid source folder!")
            return
        if not dst:
            messagebox.showerror("❌ Error", "Select a destination folder!")
            return
        
        try:
            os.makedirs(dst, exist_ok=True)
            files = [f for f in os.listdir(src) if f.lower().endswith(ext.lower())]
            
            if not files:
                messagebox.showinfo("ℹ️ No Files", f"No '{ext}' files found in source!")
                return
            
            if not messagebox.askyesno("⚠️ Confirm", f"Move {len(files)} files?"):
                return
            
            self.task1_log.delete(1.0, tk.END)
            self.log_task1(f"⚡ Moving {len(files)} '{ext}' files...\n")
            
            moved = 0
            for f in files:
                src_path = os.path.join(src, f)
                dst_path = os.path.join(dst, f)
                try:
                    shutil.move(src_path, dst_path)
                    self.log_task1(f"   ✅ {f}")
                    moved += 1
                except Exception as e:
                    self.log_task1(f"   ❌ {f} → {e}")
            
            self.log_task1(f"\n🎉 DONE! Moved {moved}/{len(files)} files.")
            self.update_status(f"✅ Moved {moved} files successfully!")
            messagebox.showinfo("✅ Success", f"Moved {moved} files!")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    # ==================== TASK 2: EMAIL EXTRACTOR LOGIC ====================
    def browse_email_input(self):
        file = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.email_input_entry.delete(0, tk.END)
            self.email_input_entry.insert(0, file)
    
    def extract_emails(self):
        text = ""
        file_path = self.email_input_entry.get().strip()
        
        if file_path and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Cannot read file: {e}")
                return
        else:
            text = self.email_text_input.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("⚠️ No Input", "Provide a file or paste text!")
            return
        
        # Extract emails using regex
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        unique_emails = sorted(set(emails))
        
        self.extracted_emails = unique_emails
        self.email_results.delete(1.0, tk.END)
        
        if not unique_emails:
            self.email_results.insert(tk.END, "❌ No emails found!\n")
            self.email_count_label.config(text="0")
            self.update_status("⚠️ No emails found")
            return
        
        for i, email in enumerate(unique_emails, 1):
            self.email_results.insert(tk.END, f"{i:>3}. {email}\n")
        
        self.email_count_label.config(text=str(len(unique_emails)))
        self.update_status(f"✅ Extracted {len(unique_emails)} unique emails")
        messagebox.showinfo("✅ Success", f"Found {len(unique_emails)} unique emails!")
    
    def save_emails(self):
        if not self.extracted_emails:
            messagebox.showwarning("⚠️ Empty", "Extract emails first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")]
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Extracted Emails\n")
                f.write(f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total: {len(self.extracted_emails)}\n\n")
                for email in self.extracted_emails:
                    f.write(email + "\n")
            
            messagebox.showinfo("✅ Saved!", f"Saved to:\n{os.path.basename(file_path)}")
            self.update_status(f"💾 Saved {len(self.extracted_emails)} emails")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def clear_emails(self):
        self.email_input_entry.delete(0, tk.END)
        self.email_text_input.delete(1.0, tk.END)
        self.email_results.delete(1.0, tk.END)
        self.email_count_label.config(text="0")
        self.extracted_emails = []
        self.update_status("🗑️ Cleared")
    
    # ==================== TASK 3: WEB SCRAPER LOGIC ====================
    def set_url(self, url):
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url)
    
    def scrape_website(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("❌ Error", "Enter a URL!")
            return
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        self.scrape_results.delete(1.0, tk.END)
        self.scrape_results.insert(tk.END, f"⏳ Fetching: {url}\n\n")
        self.scrape_results.update()
        self.update_status("🌐 Scraping...")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(target=self._do_scrape, args=(url,), daemon=True)
        thread.start()
    
    def _do_scrape(self, url):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text
            
            # Extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "No title found"
            
            # Extract meta description
            desc_match = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']',
                html, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else "No description"
            
            # Extract keywords
            keywords_match = re.search(
                r'<meta\s+name=["\']keywords["\']\s+content=["\']([^"\']+)["\']',
                html, re.IGNORECASE)
            keywords = keywords_match.group(1).strip() if keywords_match else "None"
            
            # Count links
            links = re.findall(r'<a\s+[^>]*href=["\']([^"\']+)["\']', html)
            
            # Count images
            images = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)["\']', html)
            
            self.last_scrape_data = {
                "url": url,
                "title": title,
                "description": description,
                "keywords": keywords,
                "status": response.status_code,
                "size_kb": len(html) / 1024,
                "links": len(links),
                "images": len(images),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.scrape_results.delete(1.0, tk.END)
            self.scrape_results.insert(tk.END, "=" * 60 + "\n")
            self.scrape_results.insert(tk.END, "🌐 WEB SCRAPING RESULTS\n")
            self.scrape_results.insert(tk.END, "=" * 60 + "\n\n")
            self.scrape_results.insert(tk.END, f"🔗 URL:           {url}\n")
            self.scrape_results.insert(tk.END, f"📊 Status:        {response.status_code} OK\n")
            self.scrape_results.insert(tk.END, f"📦 Page Size:     {len(html)/1024:.2f} KB\n")
            self.scrape_results.insert(tk.END, f"⏰ Time:          {datetime.now().strftime('%H:%M:%S')}\n\n")
            self.scrape_results.insert(tk.END, "-" * 60 + "\n")
            self.scrape_results.insert(tk.END, f"📌 TITLE:\n   {title}\n\n")
            self.scrape_results.insert(tk.END, f"📝 DESCRIPTION:\n   {description[:200]}{'...' if len(description) > 200 else ''}\n\n")
            self.scrape_results.insert(tk.END, f"🏷️  KEYWORDS:\n   {keywords[:200]}{'...' if len(keywords) > 200 else ''}\n\n")
            self.scrape_results.insert(tk.END, "-" * 60 + "\n")
            self.scrape_results.insert(tk.END, f"🔗 Total Links:   {len(links)}\n")
            self.scrape_results.insert(tk.END, f"🖼️  Total Images: {len(images)}\n")
            self.scrape_results.insert(tk.END, "=" * 60 + "\n")
            
            self.update_status(f"✅ Scraped: {title[:40]}...")
        except requests.exceptions.RequestException as e:
            self.scrape_results.delete(1.0, tk.END)
            self.scrape_results.insert(tk.END, f"❌ ERROR: {e}\n")
            self.update_status("❌ Scraping failed")
        except Exception as e:
            self.scrape_results.insert(tk.END, f"❌ ERROR: {e}\n")
            self.update_status("❌ Error occurred")
    
    def save_scrape(self):
        if not self.last_scrape_data:
            messagebox.showwarning("⚠️ Empty", "Scrape a website first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                d = self.last_scrape_data
                f.write("=" * 60 + "\n")
                f.write("WEB SCRAPING REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"URL:         {d['url']}\n")
                f.write(f"Timestamp:   {d['timestamp']}\n")
                f.write(f"Status:      {d['status']}\n")
                f.write(f"Page Size:   {d['size_kb']:.2f} KB\n\n")
                f.write(f"TITLE:\n{d['title']}\n\n")
                f.write(f"DESCRIPTION:\n{d['description']}\n\n")
                f.write(f"KEYWORDS:\n{d['keywords']}\n\n")
                f.write(f"Total Links:  {d['links']}\n")
                f.write(f"Total Images: {d['images']}\n")
                f.write("=" * 60 + "\n")
            
            messagebox.showinfo("✅ Saved!", f"Saved to:\n{os.path.basename(file_path)}")
            self.update_status("💾 Scrape result saved")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationSuite(root)
    root.mainloop()