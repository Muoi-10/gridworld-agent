"""Giao diện Tkinter cho gridworld trong agent.py.

Chạy:  python interface.py   (đặt cùng thư mục với agent.py)

- Chọn thuật toán, gamma, tỉ lệ đi đúng hướng rồi bấm "Train".
- Mỗi ô hiện V(s), mũi tên policy và reward R(s); màu càng đậm thì V càng cao.
- "Chạy" cho agent đi đúng số bước bạn nhập; "1 bước" đi từng bước một.
- Bấm vào một ô để chọn làm ô xuất phát và xem giá trị kỳ vọng của 4 hành động.

File này chỉ đọc agent.py, không sửa gì trong đó.
"""

import random
import time
import tkinter as tk
from tkinter import ttk

import agent as A

# True: hàng 0 nằm dưới cùng, hành động [1, 0] là đi lên.
ROW0_AT_BOTTOM = True

CELL = 120
MARGIN = 28
START = [0, 0]

COLOR_LOW = (241, 245, 249)
COLOR_HIGH = (29, 78, 216)
WALL_FILL = "#6b7280"
AGENT_FILL = "#f59e0b"
TRAIL_FILL = "#fcd34d"
BUMP_FLASH = "#ef4444"


def action_name(a):
    a = tuple(a)
    up = (1, 0) if ROW0_AT_BOTTOM else (-1, 0)
    down = (-1, 0) if ROW0_AT_BOTTOM else (1, 0)
    return {(0, 1): "phải", (0, -1): "trái", up: "lên", down: "xuống"}.get(a, "?")


def action_arrow(a):
    return {"phải": "→", "trái": "←", "lên": "↑", "xuống": "↓"}.get(action_name(a), "?")


def lerp_color(t):
    t = max(0.0, min(1.0, t))
    r, g, b = (round(lo + (hi - lo) * t) for lo, hi in zip(COLOR_LOW, COLOR_HIGH))
    return f"#{r:02x}{g:02x}{b:02x}"


class App:
    def __init__(self, root):
        self.root = root
        root.title("Gridworld · value / policy iteration")
        self.grid = A.create_grid(A.WIDTH, A.HEIGHT, A.WALLS)
        self.agent = None
        self.start = list(START)
        self.state = list(self.start)
        self.trail = []
        self.step_count = 0
        self.target_steps = 0
        self.total_reward = 0.0
        self.bumps = 0
        self.running = False
        self.after_id = None

        self._build_ui()
        self.reset_play()

    # ---------- giao diện ----------
    def _build_ui(self):
        w = A.WIDTH * CELL + 2 * MARGIN
        h = A.HEIGHT * CELL + 2 * MARGIN
        main = ttk.Frame(self.root, padding=10)
        main.grid(sticky="nsew")

        self.canvas = tk.Canvas(main, width=w, height=h, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="n")
        self.canvas.bind("<Button-1>", self.on_click)

        side = ttk.Frame(main, padding=(14, 0, 0, 0))
        side.grid(row=0, column=1, sticky="n")

        train_box = ttk.LabelFrame(side, text="Huấn luyện", padding=8)
        train_box.grid(row=0, column=0, sticky="ew")
        self.method = tk.StringVar(value="value")
        ttk.Radiobutton(train_box, text="Value iteration", variable=self.method,
                        value="value").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Radiobutton(train_box, text="Policy iteration", variable=self.method,
                        value="policy").grid(row=1, column=0, columnspan=2, sticky="w")
        ttk.Label(train_box, text="γ (gamma)").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.gamma_var = tk.StringVar(value=str(A.GAMMA))
        ttk.Entry(train_box, textvariable=self.gamma_var, width=8).grid(row=2, column=1, sticky="e", pady=(6, 0))
        ttk.Label(train_box, text="Tỉ lệ đi đúng hướng").grid(row=3, column=0, sticky="w")
        self.rate_var = tk.StringVar(value=str(A.RATE))
        ttk.Entry(train_box, textvariable=self.rate_var, width=8).grid(row=3, column=1, sticky="e")
        ttk.Label(train_box, text="Seed (để trống = ngẫu nhiên)").grid(row=4, column=0, sticky="w")
        self.seed_var = tk.StringVar(value="")
        ttk.Entry(train_box, textvariable=self.seed_var, width=8).grid(row=4, column=1, sticky="e")
        ttk.Button(train_box, text="Train", command=self.train).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.train_status = ttk.Label(train_box, text="Chưa train.", wraplength=230, foreground="#475569")
        self.train_status.grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

        play_box = ttk.LabelFrame(side, text="Cho agent chạy", padding=8)
        play_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(play_box, text="Số bước").grid(row=0, column=0, sticky="w")
        self.steps_var = tk.StringVar(value="30")
        ttk.Spinbox(play_box, from_=1, to=100000, textvariable=self.steps_var, width=8).grid(row=0, column=1, sticky="e")
        ttk.Label(play_box, text="Tốc độ (ms/bước)").grid(row=1, column=0, sticky="w")
        self.speed = tk.IntVar(value=250)
        ttk.Scale(play_box, from_=20, to=1000, variable=self.speed, orient="horizontal").grid(row=1, column=1, sticky="ew")
        btns = ttk.Frame(play_box)
        btns.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.run_btn = ttk.Button(btns, text="Chạy", command=self.toggle_run)
        self.run_btn.grid(row=0, column=0, padx=(0, 4))
        ttk.Button(btns, text="1 bước", command=self.single_step).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Về ô xuất phát", command=self.reset_play).grid(row=0, column=2, padx=(4, 0))

        self.stats = ttk.Label(play_box, text="", justify="left")
        self.stats.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.info = ttk.Label(side, text="Bấm vào một ô để chọn ô xuất phát\nvà xem giá trị của 4 hành động.",
                              justify="left", foreground="#475569")
        self.info.grid(row=2, column=0, sticky="w", pady=(10, 0))

        log_box = ttk.LabelFrame(main, text="Nhật ký từng bước", padding=6)
        log_box.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        self.log = tk.Listbox(log_box, height=9, font=("Consolas", 10), activestyle="none")
        sb = ttk.Scrollbar(log_box, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        log_box.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    # ---------- toạ độ ----------
    def cell_box(self, row, col):
        r = (A.HEIGHT - 1 - row) if ROW0_AT_BOTTOM else row
        x0 = MARGIN + col * CELL
        y0 = MARGIN + r * CELL
        return x0, y0, x0 + CELL, y0 + CELL

    def cell_at(self, x, y):
        col = int((x - MARGIN) // CELL)
        r = int((y - MARGIN) // CELL)
        if not (0 <= col < A.WIDTH and 0 <= r < A.HEIGHT):
            return None
        row = (A.HEIGHT - 1 - r) if ROW0_AT_BOTTOM else r
        return [row, col]

    # ---------- dữ liệu từ agent.py ----------
    def values(self):
        if self.agent is None:
            return None
        return [float(v) for v in self.agent.value]

    def q_values(self, state):
        V = self.values()
        n = A.WIDTH * A.HEIGHT
        return {action_name(a): sum(A.prob(self.grid, state, a, A.RATE)[s] * V[s] for s in range(n))
                for a in A.ACTIONS}

    def reward(self, state):
        r = A.get_reward(list(state), self.grid)
        return 0.0 if r is None else float(r)

    # ---------- huấn luyện ----------
    def train(self):
        try:
            gamma = float(self.gamma_var.get().replace(",", "."))
            rate = float(self.rate_var.get().replace(",", "."))
        except ValueError:
            self.train_status.configure(text="γ và tỉ lệ phải là số.", foreground="#b91c1c")
            return
        if not 0 < gamma < 1:
            self.train_status.configure(
                text="Cần 0 < γ < 1. Với map này agent nhận reward mãi mãi, γ ≥ 1 làm V không hội tụ.",
                foreground="#b91c1c")
            return
        if not 0 <= rate <= 1:
            self.train_status.configure(text="Tỉ lệ đi đúng hướng phải nằm trong [0, 1].", foreground="#b91c1c")
            return
        self.stop()
        seed = self.seed_var.get().strip()
        if seed:
            random.seed(seed)
        A.GAMMA, A.RATE = gamma, rate
        self.train_status.configure(text="Đang train…", foreground="#475569")
        self.root.update_idletasks()
        self.root.after(20, self._do_train)

    def _do_train(self):
        method = self.method.get()
        t0 = time.perf_counter()
        agent = A.Agent(method)
        agent.train(self.grid)
        dt = time.perf_counter() - t0
        self.agent = agent
        name = "value iteration" if method == "value" else "policy iteration"
        self.train_status.configure(text=f"Đã train bằng {name} (γ = {A.GAMMA}, tỉ lệ = {A.RATE}) trong {dt:.2f} s.",
                                    foreground="#15803d")
        self.reset_play()

    # ---------- chạy agent ----------
    def reset_play(self):
        self.stop()
        self.state = list(self.start)
        self.trail = [list(self.state)]
        self.step_count = 0
        self.total_reward = 0.0
        self.bumps = 0
        self.log.delete(0, "end")
        self.draw()
        self.update_stats()

    def toggle_run(self):
        if self.running:
            self.stop()
            return
        if self.agent is None:
            self.train_status.configure(text="Hãy bấm Train trước.", foreground="#b91c1c")
            return
        try:
            n = int(self.steps_var.get())
        except ValueError:
            self.info.configure(text="Số bước phải là số nguyên dương.")
            return
        if n < 1:
            self.info.configure(text="Số bước phải là số nguyên dương.")
            return
        seed = self.seed_var.get().strip()
        if seed and self.step_count == 0:
            random.seed(seed)
        self.target_steps = self.step_count + n
        self.running = True
        self.run_btn.configure(text="Dừng")
        self.tick()

    def stop(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        if hasattr(self, "run_btn"):
            self.run_btn.configure(text="Chạy")

    def tick(self):
        if not self.running:
            return
        if self.step_count >= self.target_steps:
            self.stop()
            return
        self.do_step()
        self.after_id = self.root.after(int(self.speed.get()), self.tick)

    def single_step(self):
        if self.agent is None:
            self.train_status.configure(text="Hãy bấm Train trước.", foreground="#b91c1c")
            return
        self.stop()
        self.do_step()

    def do_step(self):
        state = list(self.state)
        a = list(self.agent.pick(state, self.grid))
        intended = [state[0] + a[0], state[1] + a[1]]
        new = list(A.take_action(self.grid, state, a, A.RATE))
        if new == state:
            self.bumps += 1
            kind = "cố ý đâm tường" if A.is_wall(self.grid, intended) else "trượt vào tường"
        elif new == intended:
            kind = "đi đúng hướng"
        else:
            kind = "trượt sang bên"
        self.step_count += 1
        r = self.reward(new)
        self.total_reward += r
        self.state = new
        self.trail.append(list(new))
        self.trail = self.trail[-8:]
        self.log.insert("end", f"{self.step_count:>5}  {str(state):<7} {action_arrow(a)} {action_name(a):<6}"
                               f" → {str(new):<7} {kind:<16} R = {r:+.2f}")
        self.log.see("end")
        self.draw(flash=(new == state))
        self.update_stats()

    def update_stats(self):
        tgt = f" / {self.target_steps}" if self.running else ""
        self.stats.configure(text=f"Bước: {self.step_count}{tgt}\nVị trí: {self.state}\n"
                                  f"Tổng reward: {self.total_reward:+.2f}\nSố lần đứng yên vì tường: {self.bumps}")

    def on_click(self, event):
        cell = self.cell_at(event.x, event.y)
        if cell is None or A.is_wall(self.grid, cell):
            return
        self.start = cell
        self.reset_play()
        if self.agent is None:
            self.info.configure(text=f"Ô xuất phát: {cell}. Train để xem giá trị hành động.")
            return
        q = self.q_values(cell)
        best = action_name(self.agent.pick(cell, self.grid))
        lines = [f"Ô {cell}  ·  V = {self.values()[A.state_to_num(cell)]:.3f}  ·  R = {self.reward(cell):+.2f}",
                 "Tổng Σ P·V theo từng hành động:"]
        for name, v in sorted(q.items(), key=lambda kv: -kv[1]):
            mark = "  ← agent chọn" if name == best else ""
            lines.append(f"  {name:<6} {v:.3f}{mark}")
        self.info.configure(text="\n".join(lines))

    # ---------- vẽ ----------
    def draw(self, flash=False):
        c = self.canvas
        c.delete("all")
        V = self.values()
        open_cells = [[r, col] for r in range(A.HEIGHT) for col in range(A.WIDTH)
                      if not A.is_wall(self.grid, [r, col])]
        if V is not None:
            vals = [V[A.state_to_num(s)] for s in open_cells]
            lo, hi = min(vals), max(vals)
        for r in range(A.HEIGHT):
            for col in range(A.WIDTH):
                x0, y0, x1, y1 = self.cell_box(r, col)
                if A.is_wall(self.grid, [r, col]):
                    c.create_rectangle(x0, y0, x1, y1, fill=WALL_FILL, outline="white", width=2)
                    c.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="tường", fill="white", font=("Segoe UI", 11))
                    continue
                t = 0.0
                if V is not None:
                    t = 0.5 if hi == lo else (V[A.state_to_num([r, col])] - lo) / (hi - lo)
                fill = lerp_color(t)
                txt = "#0f172a" if t < 0.55 else "white"
                c.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#cbd5e1", width=1)
                R = self.reward([r, col])
                c.create_text(x0 + 8, y0 + 8, text=f"R {R:+g}", anchor="nw", fill=txt, font=("Segoe UI", 9))
                c.create_text(x1 - 8, y0 + 8, text=f"[{r},{col}]", anchor="ne", fill=txt, font=("Segoe UI", 9))
                if [r, col] == self.start:
                    c.create_text(x0 + 8, y0 + 26, text="xuất phát", anchor="nw", fill=txt, font=("Segoe UI", 9))
                if V is not None:
                    c.create_text((x0 + x1) / 2, y1 - 22, text=f"{V[A.state_to_num([r, col])]:.3f}",
                                  fill=txt, font=("Segoe UI", 12, "bold"))
                    a = self.agent.pick([r, col], self.grid)
                    c.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 2, text=action_arrow(a),
                                  fill=txt, font=("Segoe UI", 26))
        for i, s in enumerate(self.trail[:-1]):
            x0, y0, x1, y1 = self.cell_box(*s)
            rad = 3 + i
            cx, cy = x0 + CELL * 0.83, y0 + CELL * 0.45
            c.create_oval(cx - rad, cy - rad, cx + rad, cy + rad, fill=TRAIL_FILL, outline="")
        x0, y0, x1, y1 = self.cell_box(*self.state)
        cx, cy = x0 + CELL * 0.83, y0 + CELL * 0.45
        c.create_oval(cx - 13, cy - 13, cx + 13, cy + 13, fill=AGENT_FILL, outline="#92400e", width=2)
        if flash:
            c.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, outline=BUMP_FLASH, width=4)


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
