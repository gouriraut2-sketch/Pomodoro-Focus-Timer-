import tkinter as tk
import threading
import time
import winsound  # remove if on Mac/Linux and use os.system("afplay ...") instead

BG = "#f5ede3"
CARD = "#eeddd0"
ACCENT = "#c9a98a"
BTN = "#d4b49a"
BTN_HOVER = "#c9a98a"
TEXT = "#6b4c35"
TEXT_LIGHT = "#9c7355"
WHITE_CARD = "#fdf6f0"

def beep_start():
    threading.Thread(target=lambda: winsound.Beep(660, 300), daemon=True).start()

def beep_end():
    def _beep():
        for _ in range(6):
            winsound.Beep(880, 250)
            time.sleep(0.25)
    threading.Thread(target=_beep, daemon=True).start()

def make_btn(parent, text, command, big=False):
    size = 13 if big else 11
    b = tk.Button(parent, text=text, command=command,
                  bg=BTN, fg=TEXT, font=("Helvetica", size),
                  relief="flat", bd=0, padx=24, pady=10 if big else 8,
                  activebackground=BTN_HOVER, activeforeground=TEXT, cursor="hand2")
    b.bind("<Enter>", lambda e: b.config(bg=BTN_HOVER))
    b.bind("<Leave>", lambda e: b.config(bg=BTN))
    return b

class LockInArc:
    def __init__(self, root):
        self.root = root
        self.root.title("Lock In Arc")
        self.root.geometry("420x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.running = False
        self.paused = False
        self.thread = None
        self.show_home()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ── HOME PAGE ──────────────────────────────────────────────
    def show_home(self):
        self.running = False
        self.paused = False
        self.clear()

        tk.Label(self.root, text="", bg=BG).pack(pady=30)
        tk.Label(self.root, text="Lock In Arc", font=("Helvetica", 30, "bold"),
                 bg=BG, fg=TEXT).pack()
        tk.Label(self.root, text="your focus companion", font=("Helvetica", 12),
                 bg=BG, fg=TEXT_LIGHT).pack(pady=(4, 40))

        card = tk.Frame(self.root, bg=CARD)
        card.pack(padx=50, fill="x")

        tk.Label(card, text="choose a mode", font=("Helvetica", 11),
                 bg=CARD, fg=TEXT_LIGHT).pack(pady=(20, 14))

        make_btn(card, "Pomodoro  (25 min focus / 5 min break)",
                 lambda: self.show_cycles("pomodoro")).pack(fill="x", padx=20, pady=6)
        make_btn(card, "Custom timer",
                 self.show_custom).pack(fill="x", padx=20, pady=(6, 20))

    # ── CYCLE PICKER ───────────────────────────────────────────
    def show_cycles(self, mode, raw_focus=None, raw_break=None):
        self.clear()

        tk.Label(self.root, text="", bg=BG).pack(pady=20)
        tk.Label(self.root, text="How many cycles?", font=("Helvetica", 22, "bold"),
                 bg=BG, fg=TEXT).pack()
        tk.Label(self.root, text="one cycle = focus + break",
                 font=("Helvetica", 11), bg=BG, fg=TEXT_LIGHT).pack(pady=(4, 30))

        card = tk.Frame(self.root, bg=CARD)
        card.pack(padx=60, fill="x")

        tk.Label(card, text="", bg=CARD).pack(pady=8)

        row = tk.Frame(card, bg=CARD)
        row.pack()

        def change(delta):
            v = max(1, min(20, int(cycle_var.get()) + delta))
            cycle_var.set(str(v))

        tk.Button(row, text="-", font=("Helvetica", 16), bg=BTN, fg=TEXT,
                  relief="flat", width=3, command=lambda: change(-1),
                  activebackground=BTN_HOVER, cursor="hand2").pack(side="left", padx=8)

        cycle_var = tk.StringVar(value="1")
        tk.Entry(row, textvariable=cycle_var, width=4, font=("Helvetica", 20),
                 bg=WHITE_CARD, fg=TEXT, relief="flat", justify="center",
                 insertbackground=TEXT).pack(side="left")

        tk.Button(row, text="+", font=("Helvetica", 16), bg=BTN, fg=TEXT,
                  relief="flat", width=3, command=lambda: change(1),
                  activebackground=BTN_HOVER, cursor="hand2").pack(side="left", padx=8)

        tk.Label(card, text="cycles  (max 20)", font=("Helvetica", 10),
                 bg=CARD, fg=TEXT_LIGHT).pack(pady=(6, 16))

        def start():
            try:
                n = max(1, min(20, int(cycle_var.get())))
            except ValueError:
                n = 1
            if mode == "pomodoro":
                self.show_timer(25, 5, cycles=n)
            else:
                self.show_timer(0, 0, raw_focus=raw_focus,
                                raw_break=raw_break, cycles=n)

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.pack(pady=16)
        make_btn(btn_row, "Start", start, big=True).pack(side="left", padx=8)
        make_btn(btn_row, "Back",
                 self.show_home if mode == "pomodoro"
                 else self.show_custom).pack(side="left", padx=8)

    # ── CUSTOM PAGE ────────────────────────────────────────────
    def show_custom(self):
        self.clear()

        tk.Label(self.root, text="", bg=BG).pack(pady=20)
        tk.Label(self.root, text="Custom timer", font=("Helvetica", 22, "bold"),
                 bg=BG, fg=TEXT).pack()
        tk.Label(self.root, text="set your focus and break durations",
                 font=("Helvetica", 11), bg=BG, fg=TEXT_LIGHT).pack(pady=(4, 30))

        card = tk.Frame(self.root, bg=CARD)
        card.pack(padx=40, fill="x")

        def spin_group(parent, label, row, default_m="25"):
            tk.Label(parent, text=label, font=("Helvetica", 11),
                     bg=CARD, fg=TEXT_LIGHT).grid(row=row, column=0,
                     sticky="w", padx=20, pady=8)
            frame = tk.Frame(parent, bg=CARD)
            frame.grid(row=row, column=1, padx=20, pady=8)
            vars_ = []
            defaults = ["00", default_m, "00"]
            for i, unit in enumerate(["h", "m", "s"]):
                v = tk.StringVar(value=defaults[i])
                e = tk.Entry(frame, textvariable=v, width=3,
                             font=("Helvetica", 14), bg=WHITE_CARD, fg=TEXT,
                             relief="flat", justify="center",
                             insertbackground=TEXT)
                e.grid(row=0, column=i*2)
                tk.Label(frame, text=unit, font=("Helvetica", 11),
                         bg=CARD, fg=TEXT_LIGHT).grid(row=0, column=i*2+1, padx=(2, 8))
                vars_.append(v)
            return vars_

        card.columnconfigure(1, weight=1)
        self.focus_vars = spin_group(card, "Focus", 0, "25")
        self.break_vars = spin_group(card, "Break", 1, "05")

        tk.Frame(card, bg=ACCENT, height=1).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=4)

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.grid(row=3, column=0, columnspan=2, pady=16)

        make_btn(btn_row, "Next", self._go_to_cycles, big=True).pack(side="left", padx=8)
        make_btn(btn_row, "Back", self.show_home).pack(side="left", padx=8)

    def _go_to_cycles(self):
        def to_secs(vars_):
            try:
                h = int(vars_[0].get() or 0)
                m = int(vars_[1].get() or 0)
                s = int(vars_[2].get() or 0)
                return h*3600 + m*60 + s
            except ValueError:
                return 0
        f = to_secs(self.focus_vars) or 25*60
        b = to_secs(self.break_vars) or 5*60
        self.show_cycles("custom", raw_focus=f, raw_break=b)

    # ── TIMER PAGE ─────────────────────────────────────────────
    def show_timer(self, focus_min, break_min, raw_focus=None,
                   raw_break=None, cycles=1):
        self.clear()
        self.running = False
        self.paused = False

        self._focus_secs = raw_focus if raw_focus is not None else focus_min * 60
        self._break_secs = raw_break if raw_break is not None else break_min * 60
        self._total_cycles = cycles
        self._current_cycle = 0

        tk.Label(self.root, text="", bg=BG).pack(pady=12)
        tk.Label(self.root, text="Lock In Arc", font=("Helvetica", 18, "bold"),
                 bg=BG, fg=TEXT).pack()

        self.phase_lbl = tk.Label(self.root, text="Ready",
                                  font=("Helvetica", 12), bg=BG, fg=TEXT_LIGHT)
        self.phase_lbl.pack(pady=(12, 2))

        self.cycle_lbl = tk.Label(self.root,
                                  text=f"Cycle 0 of {cycles}",
                                  font=("Helvetica", 10), bg=BG, fg=TEXT_LIGHT)
        self.cycle_lbl.pack(pady=(0, 4))

        self.time_lbl = tk.Label(self.root, text=self._fmt(self._focus_secs),
                                 font=("Helvetica", 58, "bold"), bg=BG, fg=TEXT)
        self.time_lbl.pack()

        self.canvas = tk.Canvas(self.root, width=320, height=8,
                                bg=CARD, highlightthickness=0)
        self.canvas.pack(pady=12)
        self.bar = self.canvas.create_rectangle(0, 0, 320, 8, fill=ACCENT, width=0)

        self.status_lbl = tk.Label(self.root, text="press start when ready",
                                   font=("Helvetica", 11), bg=BG, fg=TEXT_LIGHT)
        self.status_lbl.pack(pady=4)

        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(pady=14)

        self.start_btn = make_btn(btn_row, "Start", self._start, big=True)
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = make_btn(btn_row, "Pause", self._pause)
        self.pause_btn.config(state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=6)

        make_btn(btn_row, "Reset",
                 lambda: self.show_timer(focus_min, break_min,
                                         raw_focus, raw_break, cycles)
                 ).grid(row=0, column=2, padx=6)

        make_btn(btn_row, "Home", self.show_home).grid(row=0, column=3, padx=6)

    def _fmt(self, s):
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{h:02}:{m:02}:{sec:02}" if h else f"{m:02}:{sec:02}"

    def _update(self, remaining, total, phase):
        self.time_lbl.config(text=self._fmt(remaining))
        self.phase_lbl.config(text=phase)
        pct = remaining / total if total > 0 else 0
        self.canvas.coords(self.bar, 0, 0, int(320 * pct), 8)

    def _set_cycle(self, n):
        self.cycle_lbl.config(text=f"Cycle {n} of {self._total_cycles}")

    def _start(self):
        if self.paused:
            self.paused = False
            self.running = True
            self.start_btn.config(text="Start", state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            beep_start()
            return
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _pause(self):
        self.paused = True
        self.running = False
        self.start_btn.config(text="Resume", state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)

    def _countdown(self, total, phase):
        for remaining in range(total, -1, -1):
            while self.paused:
                time.sleep(0.2)
            if not self.running:
                return False
            self.root.after(0, self._update, remaining, total, phase)
            if remaining > 0:
                time.sleep(1)
        return True

    def _run(self):
        beep_start()
        for cycle in range(1, self._total_cycles + 1):
            if not self.running:
                break

            self.root.after(0, self._set_cycle, cycle)
            self.root.after(0, self.status_lbl.config, {"text": "focus!"})

            done = self._countdown(self._focus_secs, f"Focus  —  cycle {cycle}")
            if not done:
                break

            beep_end()
            self.root.after(0, self.status_lbl.config,
                            {"text": "Time's up! Take a break."})

            done = self._countdown(self._break_secs, f"Break  —  cycle {cycle}")
            if not done:
                break

            if cycle < self._total_cycles:
                beep_start()
                self.root.after(0, self.status_lbl.config,
                                {"text": f"Break's over! Starting cycle {cycle + 1}."})

        if self.running:
            beep_end()
            self.root.after(0, self.status_lbl.config,
                            {"text": "All cycles complete! Great work."})

        self.running = False
        self.root.after(0, self.start_btn.config,
                        {"text": "Start", "state": tk.NORMAL})
        self.root.after(0, self.pause_btn.config, {"state": tk.DISABLED})


if __name__ == "__main__":
    root = tk.Tk()
    app = LockInArc(root)
    root.mainloop()