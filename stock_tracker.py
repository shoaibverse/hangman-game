import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import json
import os
from datetime import datetime


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
    "glow_green": "#00FF88"
}


# ==================== HARDCODED STOCK PRICES ====================
STOCK_PRICES = {
    "AAPL": 180.50,   # Apple
    "TSLA": 250.75,   # Tesla
    "MSFT": 380.20,   # Microsoft
    "GOOGL": 140.30,  # Google
    "AMZN": 175.80,   # Amazon
    "NVDA": 495.60,   # NVIDIA
    "META": 355.40,   # Meta
    "NFLX": 445.90,   # Netflix
    "AMD": 145.25,    # AMD
    "INTC": 43.50,    # Intel
    "IBM": 165.75,    # IBM
    "ORCL": 115.30,   # Oracle
    "DIS": 92.40,     # Disney
    "PYPL": 62.80,    # PayPal
    "UBER": 55.20,    # Uber
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
class StockPortfolioTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("📈 STOCK PORTFOLIO TRACKER — PREMIUM")
        
        # Auto-fit screen
        screen_h = self.root.winfo_screenheight()
        win_h = min(screen_h - 80, 750)
        self.root.geometry(f"850x{win_h}")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)
        
        self.portfolio = {}  # {symbol: quantity}
        
        self.setup_ui()
        self.animate_title()
    
    def setup_ui(self):
        # ========== HEADER ==========
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.pack(fill="x", pady=(15, 5))
        
        self.title_label = tk.Label(
            header, text="📈 STOCK PORTFOLIO TRACKER",
            font=("Segoe UI", 22, "bold"),
            bg=COLORS["bg"], fg=COLORS["primary"]
        )
        self.title_label.pack()
        
        tk.Label(
            header, text="◆ Track • Analyze • Invest ◆",
            font=("Segoe UI", 10, "italic"),
            bg=COLORS["bg"], fg=COLORS["text_dim"]
        ).pack()
        
        # ========== INPUT CARD ==========
        input_card = tk.Frame(self.root, bg=COLORS["card"])
        input_card.pack(pady=10, padx=25, fill="x")
        
        input_title = tk.Label(
            input_card, text="💼  ADD STOCK TO PORTFOLIO",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["card"], fg=COLORS["gold"]
        )
        input_title.pack(pady=(12, 8))
        
        input_frame = tk.Frame(input_card, bg=COLORS["card"])
        input_frame.pack(pady=(0, 12))
        
        # Stock Symbol
        tk.Label(input_frame, text="📊 Symbol", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).grid(row=0, column=0, padx=8, sticky="w")
        
        self.symbol_var = tk.StringVar()
        self.symbol_combo = ttk.Combobox(
            input_frame, textvariable=self.symbol_var,
            values=list(STOCK_PRICES.keys()),
            font=("Segoe UI", 11, "bold"), width=12, state="readonly"
        )
        self.symbol_combo.grid(row=1, column=0, padx=8, pady=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.update_price_preview)
        
        # Quantity
        tk.Label(input_frame, text="🔢 Quantity", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).grid(row=0, column=1, padx=8, sticky="w")
        
        self.qty_entry = tk.Entry(
            input_frame, font=("Segoe UI", 11, "bold"),
            bg=COLORS["card_light"], fg=COLORS["text"],
            insertbackground=COLORS["primary"], relief="flat",
            width=12, justify="center"
        )
        self.qty_entry.grid(row=1, column=1, padx=8, pady=5, ipady=5)
        
        # Price Preview
        tk.Label(input_frame, text="💰 Price/Share", font=("Segoe UI", 10, "bold"),
                 bg=COLORS["card"], fg=COLORS["text_dim"]).grid(row=0, column=2, padx=8, sticky="w")
        
        self.price_label = tk.Label(
            input_frame, text="$0.00", font=("Segoe UI", 12, "bold"),
            bg=COLORS["card_light"], fg=COLORS["success"],
            width=12, pady=5
        )
        self.price_label.grid(row=1, column=2, padx=8, pady=5)
        
        # ADD BUTTON
        self.add_btn = NeonButton(
            input_frame, text="➕ ADD", command=self.add_stock,
            width=100, height=38,
            bg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            glow_color=COLORS["glow_green"],
            font_size=11, rounded=12, parent_bg=COLORS["card"]
        )
        self.add_btn.grid(row=1, column=3, padx=8)
        
        # ========== PORTFOLIO TABLE CARD ==========
        table_card = tk.Frame(self.root, bg=COLORS["card"])
        table_card.pack(pady=10, padx=25, fill="both", expand=True)
        
        table_title = tk.Label(
            table_card, text="📊  YOUR PORTFOLIO",
            font=("Segoe UI", 11, "bold"),
            bg=COLORS["card"], fg=COLORS["gold"]
        )
        table_title.pack(pady=(12, 5))
        
        # Table headers
        headers_frame = tk.Frame(table_card, bg=COLORS["card_light"])
        headers_frame.pack(padx=15, pady=(5, 0), fill="x")
        
        headers = [("SYMBOL", 100), ("QTY", 80), ("PRICE", 100), ("VALUE", 140), ("ACTION", 80)]
        for i, (h, w) in enumerate(headers):
            tk.Label(headers_frame, text=h, font=("Segoe UI", 10, "bold"),
                     bg=COLORS["card_light"], fg=COLORS["primary"],
                     width=w//10, pady=8).grid(row=0, column=i, padx=2)
        
        # Scrollable list
        list_container = tk.Frame(table_card, bg=COLORS["card"])
        list_container.pack(padx=15, pady=(0, 10), fill="both", expand=True)
        
        self.canvas_scroll = tk.Canvas(list_container, bg=COLORS["card"], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas_scroll.yview)
        self.list_frame = tk.Frame(self.canvas_scroll, bg=COLORS["card"])
        
        self.list_frame.bind("<Configure>",
                             lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")))
        self.canvas_scroll.create_window((0, 0), window=self.list_frame, anchor="nw", width=750)
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)
        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Empty message
        self.empty_label = tk.Label(
            self.list_frame,
            text="🌟 No stocks yet — Add some to get started! 🌟",
            font=("Segoe UI", 11, "italic"),
            bg=COLORS["card"], fg=COLORS["text_dim"], pady=40
        )
        self.empty_label.pack()
        
        # ========== TOTAL DISPLAY ==========
        total_card = tk.Frame(self.root, bg=COLORS["card"])
        total_card.pack(pady=8, padx=25, fill="x")
        
        total_inner = tk.Frame(total_card, bg=COLORS["card"])
        total_inner.pack(pady=12)
        
        tk.Label(total_inner, text="💎 TOTAL INVESTMENT",
                 font=("Segoe UI", 12, "bold"),
                 bg=COLORS["card"], fg=COLORS["accent"]).pack(side="left", padx=15)
        
        self.total_label = tk.Label(
            total_inner, text="$0.00",
            font=("Consolas", 22, "bold"),
            bg=COLORS["card"], fg=COLORS["gold"]
        )
        self.total_label.pack(side="left", padx=15)
        
        self.stocks_count = tk.Label(
            total_inner, text="0 stocks",
            font=("Segoe UI", 10),
            bg=COLORS["card"], fg=COLORS["text_dim"]
        )
        self.stocks_count.pack(side="left", padx=10)
        
        # ========== ACTION BUTTONS ==========
        action_frame = tk.Frame(self.root, bg=COLORS["bg"])
        action_frame.pack(pady=10)
        
        NeonButton(
            action_frame, text="💾 SAVE TXT", command=lambda: self.save_file("txt"),
            width=130, height=38,
            bg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            glow_color=COLORS["glow_cyan"],
            font_size=10, rounded=12, parent_bg=COLORS["bg"]
        ).pack(side="left", padx=6)
        
        NeonButton(
            action_frame, text="📊 SAVE CSV", command=lambda: self.save_file("csv"),
            width=130, height=38,
            bg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            glow_color=COLORS["glow_pink"],
            font_size=10, rounded=12, parent_bg=COLORS["bg"]
        ).pack(side="left", padx=6)
        
        NeonButton(
            action_frame, text="🗑️ CLEAR ALL", command=self.clear_all,
            width=130, height=38,
            bg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            glow_color=COLORS["danger"],
            font_size=10, rounded=12, parent_bg=COLORS["bg"]
        ).pack(side="left", padx=6)
    
    # ==================== ANIMATIONS ====================
    def animate_title(self):
        """Neon glow pulse animation on title."""
        colors_cycle = [COLORS["primary"], COLORS["primary_hover"],
                        COLORS["accent"], COLORS["primary_hover"]]
        current = getattr(self, "_title_idx", 0)
        self.title_label.config(fg=colors_cycle[current % len(colors_cycle)])
        self._title_idx = current + 1
        self.root.after(800, self.animate_title)
    
    def flash_total(self):
        """Flash total when updated."""
        original = self.total_label.cget("fg")
        self.total_label.config(fg=COLORS["success"])
        self.root.after(300, lambda: self.total_label.config(fg=original))
    
    # ==================== LOGIC ====================
    def update_price_preview(self, event=None):
        symbol = self.symbol_var.get()
        if symbol in STOCK_PRICES:
            self.price_label.config(text=f"${STOCK_PRICES[symbol]:.2f}")
    
    def add_stock(self):
        symbol = self.symbol_var.get().strip().upper()
        qty_str = self.qty_entry.get().strip()
        
        if not symbol:
            messagebox.showwarning("⚠️ Missing Info", "Please select a stock symbol!")
            return
        
        if symbol not in STOCK_PRICES:
            messagebox.showerror("❌ Invalid Stock", f"'{symbol}' not in database!")
            return
        
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("❌ Invalid Quantity", "Enter a positive whole number!")
            return
        
        # Add or update portfolio
        if symbol in self.portfolio:
            self.portfolio[symbol] += qty
        else:
            self.portfolio[symbol] = qty
        
        # Reset inputs
        self.symbol_var.set("")
        self.qty_entry.delete(0, tk.END)
        self.price_label.config(text="$0.00")
        
        self.refresh_list()
        self.flash_total()
    
    def remove_stock(self, symbol):
        if messagebox.askyesno("🗑️ Remove Stock", f"Remove {symbol} from portfolio?"):
            del self.portfolio[symbol]
            self.refresh_list()
            self.flash_total()
    
    def refresh_list(self):
        # Clear existing rows
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not self.portfolio:
            self.empty_label = tk.Label(
                self.list_frame,
                text="🌟 No stocks yet — Add some to get started! 🌟",
                font=("Segoe UI", 11, "italic"),
                bg=COLORS["card"], fg=COLORS["text_dim"], pady=40
            )
            self.empty_label.pack()
            self.total_label.config(text="$0.00")
            self.stocks_count.config(text="0 stocks")
            return
        
        total = 0.0
        for symbol, qty in self.portfolio.items():
            price = STOCK_PRICES[symbol]
            value = price * qty
            total += value
            
            row = tk.Frame(self.list_frame, bg=COLORS["card_light"], pady=8)
            row.pack(fill="x", pady=3, padx=5)
            
            # Symbol
            tk.Label(row, text=symbol, font=("Segoe UI", 12, "bold"),
                     bg=COLORS["card_light"], fg=COLORS["primary"],
                     width=10).grid(row=0, column=0, padx=2)
            
            # Quantity
            tk.Label(row, text=str(qty), font=("Segoe UI", 11),
                     bg=COLORS["card_light"], fg=COLORS["text"],
                     width=8).grid(row=0, column=1, padx=2)
            
            # Price
            tk.Label(row, text=f"${price:.2f}", font=("Segoe UI", 11),
                     bg=COLORS["card_light"], fg=COLORS["warning"],
                     width=10).grid(row=0, column=2, padx=2)
            
            # Value
            tk.Label(row, text=f"${value:,.2f}", font=("Segoe UI", 12, "bold"),
                     bg=COLORS["card_light"], fg=COLORS["success"],
                     width=14).grid(row=0, column=3, padx=2)
            
            # Remove button
            NeonButton(
                row, text="✕", command=lambda s=symbol: self.remove_stock(s),
                width=32, height=28,
                bg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                glow_color=COLORS["danger"],
                font_size=10, rounded=8, parent_bg=COLORS["card_light"]
            ).grid(row=0, column=4, padx=5)
        
        # Update total
        self.total_label.config(text=f"${total:,.2f}")
        self.stocks_count.config(text=f"{len(self.portfolio)} stocks")
    
    def clear_all(self):
        if not self.portfolio:
            messagebox.showinfo("ℹ️ Empty", "Portfolio is already empty!")
            return
        if messagebox.askyesno("⚠️ Clear All", "Remove all stocks from portfolio?"):
            self.portfolio.clear()
            self.refresh_list()
            self.flash_total()
    
    def save_file(self, file_type):
        if not self.portfolio:
            messagebox.showwarning("⚠️ Empty", "No stocks to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"portfolio_{timestamp}"
        
        if file_type == "txt":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"{default_name}.txt",
                filetypes=[("Text files", "*.txt")]
            )
            if not file_path:
                return
            
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=" * 50 + "\n")
                    f.write("STOCK PORTFOLIO REPORT\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"{'SYMBOL':<10}{'QTY':<8}{'PRICE':<12}{'VALUE':<15}\n")
                    f.write("-" * 50 + "\n")
                    
                    total = 0
                    for symbol, qty in self.portfolio.items():
                        price = STOCK_PRICES[symbol]
                        value = price * qty
                        total += value
                        f.write(f"{symbol:<10}{qty:<8}${price:<11.2f}${value:<14,.2f}\n")
                    
                    f.write("-" * 50 + "\n")
                    f.write(f"{'TOTAL INVESTMENT:':<30}${total:,.2f}\n")
                    f.write("=" * 50 + "\n")
                
                messagebox.showinfo("✅ Saved!", f"Portfolio saved as:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to save:\n{e}")
        
        elif file_type == "csv":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile=f"{default_name}.csv",
                filetypes=[("CSV files", "*.csv")]
            )
            if not file_path:
                return
            
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Symbol", "Quantity", "Price/Share", "Total Value"])
                    
                    total = 0
                    for symbol, qty in self.portfolio.items():
                        price = STOCK_PRICES[symbol]
                        value = price * qty
                        total += value
                        writer.writerow([symbol, qty, f"{price:.2f}", f"{value:.2f}"])
                    
                    writer.writerow([])
                    writer.writerow(["", "", "TOTAL", f"{total:.2f}"])
                
                messagebox.showinfo("✅ Saved!", f"Portfolio saved as:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Failed to save:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StockPortfolioTracker(root)
    root.mainloop()