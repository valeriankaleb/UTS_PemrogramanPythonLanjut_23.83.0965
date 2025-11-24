# Updated zigzag_tk.py with trail removed and dark mode UI
import tkinter as tk
from tkinter import ttk
import math
import time

# --- Configuration ---
WIDTH = 60
MAX_INDENT = 20
FPS_DEFAULT = 12

# Utility
def lerp(a, b, t):
    return int(a + (b - a) * t)

def rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

class ZigZagGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Zigzag - Dark Mode")
        self.configure(padx=8, pady=8, bg="#1e1e1e")

        self.indent = 0
        self.indent_increasing = True
        self.frame = 0
        self.running = False
        self.fps = FPS_DEFAULT

        self.style = ttk.Style(self)
        self.enable_dark_mode()

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.render_once()

    def enable_dark_mode(self):
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        self.style.configure("TButton", background="#333333", foreground="#ffffff")
        self.style.configure("TScale", background="#1e1e1e")

    def create_widgets(self):
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            text_frame,
            width=WIDTH,
            height=12,
            wrap="none",
            font=("Courier New", 12),
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff"
        )
        self.text.pack(side="left", fill="both", expand=True)
        self.text.configure(state="disabled")

        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        vsb.pack(side="right", fill="y")
        self.text.configure(yscrollcommand=vsb.set)

        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", pady=(8,0))

        self.start_btn = ttk.Button(ctrl, text="Start", command=self.start)
        self.start_btn.pack(side="left")

        self.stop_btn = ttk.Button(ctrl, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left", padx=(6,0))

        ttk.Label(ctrl, text="Speed:").pack(side="left", padx=(12,4))
        self.speed_var = tk.DoubleVar(value=self.fps)
        self.speed_slider = ttk.Scale(ctrl, from_=2, to=60, variable=self.speed_var, command=self.on_speed_change)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=(0,8))

    def on_speed_change(self, _=None):
        self.fps = max(1, int(self.speed_var.get()))

    def start(self):
        if not self.running:
            self.running = True
            self.start_btn.state(["disabled"])
            self.stop_btn.state(["!disabled"])
            self.loop()

    def stop(self):
        if self.running:
            self.running = False
            self.start_btn.state(["!disabled"])
            self.stop_btn.state(["disabled"])

    def on_close(self):
        self.running = False
        self.destroy()

    def render_once(self):
        t = self.indent / MAX_INDENT
        cold = (0, 220, 255)
        normal = (255, 255, 0)
        hot  = (255, 30, 0)

        # Interpolasi dua tahap: Cold → Normal → Hot
        if t < 0.5:
            # Dari Cold ke Normal
            tt = t / 0.5
            R = lerp(cold[0], normal[0], tt)
            G = lerp(cold[1], normal[1], tt)
            B = lerp(cold[2], normal[2], tt)
        else:
            # Dari Normal ke Hot
            tt = (t - 0.5) / 0.5
            R = lerp(normal[0], hot[0], tt)
            G = lerp(normal[1], hot[1], tt)
            B = lerp(normal[2], hot[2], tt)

        glow = (math.sin(self.frame / 4) + 1) / 2
        brightness = lerp(120, 255, glow)

        final_R = lerp(R, brightness, 0.4)
        final_G = lerp(G, brightness, 0.4)
        final_B = lerp(B, brightness, 0.4)

        main_color = rgb_to_hex(final_R, final_G, final_B)

        line = " " * self.indent + "********"

        self.text.configure(state="normal")
        tag = f"c{main_color}"
        if tag not in self.text.tag_names():
            self.text.tag_config(tag, foreground=main_color)

        self.text.insert("end", line + "\n", tag)
        self.text.configure(state="disabled")
        self.text.see("end")

    def update_logic(self):
        if self.indent_increasing:
            self.indent += 1
            if self.indent >= MAX_INDENT:
                self.indent_increasing = False
        else:
            self.indent -= 1
            if self.indent <= 0:
                self.indent_increasing = True

        self.frame += 1

    def loop(self):
        if not self.running:
            return

        start = time.time()

        self.update_logic()
        self.render_once()

        delay = int(1000 / max(1, self.fps))
        elapsed = (time.time() - start) * 1000
        to_wait = max(1, delay - int(elapsed))
        self.after(to_wait, self.loop)


if __name__ == "__main__":
    app = ZigZagGUI()
    app.stop_btn.state(["disabled"])
    app.mainloop()