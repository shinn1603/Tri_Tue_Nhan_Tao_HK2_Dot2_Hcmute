# -*- coding: utf-8 -*-
"""
base_gui.py
Lớp giao diện cơ sở (Base UI) cho tất cả các thuật toán giải Sudoku.
Được thiết kế lại theo phong cách Dark/Cyberpunk với các tính năng:
- Chọn độ khó
- Tự nhập đề (Edit Mode)
- Tua lại quá trình giải (Scrubbing)
- Log hệ thống chi tiết
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading
import copy

from sudoku_utils import generate_puzzle, SIZE, BOX, is_valid

# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              
CARD = "#141630"            
CARD_H = "#1E203E"          
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_EMPTY_BG = "#1A1C38"
COLOR_CLUE_BG = "#2A2D54"
COLOR_CLUE_TEXT = "#A0A5D0"

COLOR_TRY_BG = "#FFF3B0"    
COLOR_TRY_TEXT = "#946800"
COLOR_BACKTRACK_BG = "#FF325A" 
COLOR_BACKTRACK_TEXT = "#FFFFFF"

COLOR_SOLVED_BG = "#00E473"    
COLOR_SOLVED_TEXT = "#000000"
COLOR_NEW_ITER_FLASH = "#00B9FF"

COLOR_SELECTED_BG = "#2c3e50"

# Fonts
FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LOG = ("Consolas", 10)


class BaseSudokuApp:
    def __init__(self, root, title, subtitle, algo_name, solver_class, num_clues=35):
        self.root = root
        self.root.title(title)
        self.root.configure(bg=BG)
        self.root.geometry("1100x800")
        self.root.minsize(1050, 750)

        self.title_text = title
        self.subtitle_text = subtitle
        self.algo_name = algo_name
        self.solver_class = solver_class
        
        # State variables
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.is_paused = False
        self.current_step_index = -1
        self.play_speed_ms = 40
        
        self.edit_mode = False
        self.selected_cell = None

        self._build_ui()
        
        # Init first puzzle
        self._set_difficulty()
        
        # Key bindings
        self.root.bind("<Key>", self.on_key_press)

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=BG)
        header_frame.pack(fill=tk.X, pady=(15, 5))
        
        lbl_title = tk.Label(header_frame, text=self.title_text, font=FONT_TITLE, bg=BG, fg=ACCENT)
        lbl_title.pack()
        
        lbl_sub = tk.Label(header_frame, text=self.subtitle_text, font=FONT_LABEL, bg=BG, fg=TXT_D)
        lbl_sub.pack()

        # Body
        body_frame = tk.Frame(self.root, bg=BG)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Trái: Grid
        left_frame = tk.Frame(body_frame, bg=CARD, bd=0, relief="flat", highlightbackground=ACCENT, highlightthickness=1)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        grid_container = tk.Frame(left_frame, bg=CARD)
        grid_container.pack(padx=15, pady=15)

        grid_frame = tk.Frame(grid_container, bg="#2A2D54", bd=2)
        grid_frame.pack()

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pad_top = 3 if r % BOX == 0 else 1
                pad_left = 3 if c % BOX == 0 else 1
                pad_bottom = 3 if r == SIZE - 1 else 1
                pad_right = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_EMPTY_BG, fg=TXT_B,
                    relief="flat", borderwidth=0, cursor="hand2"
                )
                cell.grid(row=r, column=c, padx=(pad_left, pad_right), pady=(pad_top, pad_bottom), sticky="nsew")
                cell.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))
                self.cell_labels[r][c] = cell

        # Phải: Controls + Logs
        right_frame = tk.Frame(body_frame, bg=BG)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = tk.Frame(right_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        btn_style = {"font": FONT_LABEL, "relief": "flat", "padx": 4, "pady": 5, "cursor": "hand2", "disabledforeground": "#A9B1D6"}

        # Hàng 1: Đề bài
        row1_frame = tk.Frame(control_frame, bg=CARD)
        row1_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(row1_frame, text="Độ khó:", font=FONT_LABEL, bg=CARD, fg=TXT_B).pack(side=tk.LEFT, padx=(0,5))
        
        self.diff_var = tk.StringVar(value="Trung bình")
        combo_diff = ttk.Combobox(row1_frame, textvariable=self.diff_var, values=["Dễ", "Trung bình", "Khó", "Cực Khó"], state="readonly", width=12)
        combo_diff.pack(side=tk.LEFT, padx=5)
        combo_diff.bind("<<ComboboxSelected>>", lambda e: self._set_difficulty())
        
        self.btn_new = tk.Button(row1_frame, text="↻ Sinh Đề Mới", command=self._set_difficulty, bg="#FFBE00", fg="black", activebackground="#D9A200", **btn_style)
        self.btn_new.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(row1_frame, text="Tự nhập đề", command=self.toggle_edit_mode, bg="#9D4EDD", fg=TXT_B, activebackground="#7B2CBF", **btn_style)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        # Hàng 2: Playback
        row2_frame = tk.Frame(control_frame, bg=CARD)
        row2_frame.pack(fill=tk.X, pady=5, padx=10)

        self.btn_solve = tk.Button(row2_frame, text=f"▶ Giải", command=self.on_solve_click, bg="#0066FF", fg=TXT_B, activebackground="#0052CC", **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=(0,5))

        self.btn_stop = tk.Button(row2_frame, text="⏹ Dừng", state="disabled", command=self.on_stop_click, bg="#FF325A", fg=TXT_B, activebackground="#CC2848", **btn_style)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.btn_play = tk.Button(row2_frame, text="⏵ Phát lại", state="disabled", command=self.on_play_click, bg="#00E473", fg="black", activebackground="#00C463", **btn_style)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = tk.Button(row2_frame, text="⏸ Tạm dừng", state="disabled", command=self.on_pause_click, bg=TXT_D, fg=TXT_B, **btn_style)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_skip = tk.Button(row2_frame, text="⏭ Bỏ qua", state="disabled", command=self.on_skip_click, bg=TXT_D, fg=TXT_B, **btn_style)
        self.btn_skip.pack(side=tk.LEFT, padx=5)

        # Hàng 3: Tua lại (Scrubbing)
        row3_frame = tk.Frame(control_frame, bg=CARD)
        row3_frame.pack(fill=tk.X, pady=5, padx=10)
        
        tk.Label(row3_frame, text="Tiến độ giải:", font=FONT_LABEL, bg=CARD, fg=TXT_B, width=10, anchor="w").pack(side=tk.LEFT)
        
        self.btn_step_back = tk.Button(row3_frame, text="◄", command=self.on_step_back_click, bg=CARD_H, fg=TXT_B, font=("Segoe UI", 10, "bold"), relief="flat", padx=5)
        self.btn_step_back.pack(side=tk.LEFT, padx=2)
        
        self.progress_scale = tk.Scale(row3_frame, from_=0, to=0, orient="horizontal", bg=CARD, fg=TXT_B, troughcolor=BG, highlightthickness=0, command=self._on_progress_drag)
        self.progress_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.btn_step_forward = tk.Button(row3_frame, text="►", command=self.on_step_forward_click, bg=CARD_H, fg=TXT_B, font=("Segoe UI", 10, "bold"), relief="flat", padx=5)
        self.btn_step_forward.pack(side=tk.LEFT, padx=2)
        
        # Hàng 4: Tốc độ
        row4_frame = tk.Frame(control_frame, bg=CARD)
        row4_frame.pack(fill=tk.X, pady=(5,10), padx=10)
        
        tk.Label(row4_frame, text="Tốc độ:", font=FONT_LABEL, bg=CARD, fg=TXT_B, width=10, anchor="w").pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(row4_frame, from_=1, to=300, orient="horizontal", bg=CARD, fg=TXT_B, troughcolor=BG, highlightthickness=0, command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Trạng thái
        self.info_label = tk.Label(right_frame, text="Sẵn sàng.", font=FONT_LABEL, bg=BG, fg=ACCENT, justify="left")
        self.info_label.pack(anchor="w", pady=(0, 5))

        # Tabs for Logs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=CARD, foreground=TXT_B, padding=[10, 5], relief="flat")
        style.map('TNotebook.Tab', background=[('selected', ACCENT)], foreground=[('selected', 'black')])

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Tab 1: Nhật ký hệ thống
        tab1 = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab1, text="Nhật ký hệ thống")

        self.log_text = tk.Text(tab1, font=FONT_LOG, bg=BG, fg=TXT, state=tk.DISABLED, wrap=tk.WORD, bd=0)
        scroll1 = tk.Scrollbar(tab1, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll1.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll1.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=5)

        # Tab 2: Vết chạy tay
        tab2 = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab2, text="Vết chạy tay (Trace)")

        self.trace_text = tk.Text(tab2, font=FONT_LOG, bg=BG, fg=TXT, state=tk.DISABLED, wrap=tk.WORD, bd=0)
        scroll2 = tk.Scrollbar(tab2, command=self.trace_text.yview)
        self.trace_text.configure(yscrollcommand=scroll2.set)
        self.trace_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scroll2.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=5)

        # Colors for Logs
        for t in (self.log_text, self.trace_text):
            t.tag_configure("info", foreground=TXT_D)
            t.tag_configure("try", foreground=COLOR_TRY_BG)
            t.tag_configure("backtrack", foreground=COLOR_BACKTRACK_BG)
            t.tag_configure("success", foreground=COLOR_SOLVED_BG)
            t.tag_configure("error", foreground="#FF325A")
            t.tag_configure("system", foreground=ACCENT)

    # ================= UI LOGIC =================
    
    def _set_difficulty(self):
        if self.is_solving or self.is_playing: return
        diff_map = {"Dễ": 45, "Trung bình": 35, "Khó": 25, "Cực Khó": 17}
        num = diff_map.get(self.diff_var.get(), 35)
        
        self.puzzle, _ = generate_puzzle(num_clues=num)
        self.solver = self.solver_class(self.puzzle)
        self._reset_state()
        self._render_board(self.puzzle)
        self._clear_log()
        self._log(f"Đã tạo đề mới (Độ khó: {self.diff_var.get()}, {num} manh mối)", "system")

    def toggle_edit_mode(self):
        if self.is_solving or self.is_playing: return
        
        if not self.edit_mode:
            # Bật Edit Mode
            self.edit_mode = True
            self.btn_edit.config(text="✓ Xác nhận đề", bg="#00E473", fg="black")
            self.btn_solve.config(state="disabled")
            self.btn_new.config(state="disabled")
            
            # Xóa sạch bảng
            self.puzzle = [[0]*SIZE for _ in range(SIZE)]
            self.selected_cell = None
            self._render_board(self.puzzle)
            self._clear_log()
            self._log("--- CHẾ ĐỘ NHẬP ĐỀ TAY ---", "system")
            self._log("Click vào các ô và gõ phím số (1-9). Nhấn Backspace để xóa.", "info")
            self.info_label.config(text="Đang nhập đề. Vui lòng bấm 'Xác nhận đề' sau khi hoàn tất.")
        else:
            # Tắt Edit Mode, kiểm tra tính hợp lệ
            self.edit_mode = False
            self.selected_cell = None
            
            self.solver = self.solver_class(self.puzzle)
            self._reset_state()
            self._render_board(self.puzzle)
            
            self.btn_edit.config(text="Tự nhập đề", bg="#9D4EDD", fg=TXT_B)
            self.btn_solve.config(state="normal")
            self.btn_new.config(state="normal")
            self._log("Đã khóa đề và sẵn sàng giải.", "success")
            self.info_label.config(text="Đề đã được xác nhận. Nhấn Giải để bắt đầu.")

    def on_cell_click(self, r, c):
        if not self.edit_mode: return
        self.selected_cell = (r, c)
        self._render_board(self.puzzle)

    def on_key_press(self, event):
        if not self.edit_mode or not self.selected_cell: return
        r, c = self.selected_cell
        
        if event.char in "123456789":
            self.puzzle[r][c] = int(event.char)
            self._render_board(self.puzzle)
        elif event.keysym in ("BackSpace", "Delete", "0"):
            self.puzzle[r][c] = 0
            self._render_board(self.puzzle)

    def _reset_state(self):
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self.btn_stop.config(state="disabled")
        self.progress_scale.config(to=100, state="disabled")
        self.progress_scale.set(0)

    # ================= CORE LOGIC =================
    
    def on_solve_click(self):
        if self.is_solving: return
        self.is_solving = True
        self._reset_state()
        self._clear_log()
        self._log(f"Bắt đầu giải bằng {self.algo_name}...", "system")
        self.btn_solve.config(state="disabled", text="⏳ Đang giải...")
        self.btn_edit.config(state="disabled")
        self.btn_new.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.info_label.config(text=f"Đang chạy thuật toán {self.algo_name}...")

        def run_solver():
            t0 = time.time()
            try:
                solution, steps, stats = self.solver.solve()
                t1 = time.time()
                stats['elapsed_seconds'] = round(t1 - t0, 4)
                self.steps = steps
                self.stats = stats
                self.solution_board = solution
                self.root.after(0, self._on_solve_finished)
            except Exception as e:
                pass # Bị dừng hoặc lỗi

        self.solver_thread = threading.Thread(target=run_solver, daemon=True)
        self.solver_thread.start()

    def on_stop_click(self):
        if not self.is_solving: return
        self._log("Đang dừng thuật toán...", "error")
        if hasattr(self, 'solver_thread') and self.solver_thread.is_alive():
            import ctypes
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.solver_thread.ident), ctypes.py_object(SystemExit))
        
        self.is_solving = False
        self.btn_solve.config(state="normal", text="▶ Giải")
        self.btn_edit.config(state="normal")
        self.btn_new.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.info_label.config(text="Đã dừng thuật toán.")
        self._log("Thuật toán đã bị người dùng dừng lại.", "error")

    def _on_solve_finished(self):
        self.is_solving = False
        self.btn_solve.config(state="normal", text=f"▶ Giải")
        self.btn_edit.config(state="normal")
        self.btn_new.config(state="normal")
        self.btn_stop.config(state="disabled")

        total_steps = len(self.steps)
        if self.solution_board is None:
            self._log("Không tìm thấy lời giải. (Bị kẹt cục bộ / Không thể giải tiếp)", "error")
            self.info_label.config(text="Bị kẹt! Bạn có thể phát lại để xem quá trình chạy sai hướng.")
        else:
            nodes = self.stats.get('nodes_expanded', self.stats.get('nodes', 0))
            time_sec = self.stats.get('elapsed_seconds', 0)
            info_text = f"Đã giải xong! Nodes: {nodes:,} | Thời gian: {time_sec}s | Số bước ghi nhận: {total_steps:,}"
            self.info_label.config(text=info_text)
            self._log(f"Hoàn thành trong {time_sec}s với {nodes:,} nodes được mở rộng.", "success")
            self._log("Bạn có thể bấm 'Phát lại', kéo thanh tiến độ hoặc bấm < > để xem lại.", "info")

        if total_steps > 0:
            self.progress_scale.config(to=total_steps, state="normal")
            self.btn_play.config(state="normal")
            self.btn_skip.config(state="normal")
        else:
            self.progress_scale.config(to=100, state="disabled")
            if self.solution_board is None:
                messagebox.showwarning("Không tìm thấy lời giải", f"{self.algo_name} không tìm được lời giải hợp lệ và không có bước chạy nào.")
        self.progress_scale.set(0)

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    def _on_progress_drag(self, value):
        if self.is_playing or self.is_solving: return
        if not self.steps: return
        
        idx = int(float(value))
        if idx == 0:
            self._render_board(self.puzzle)
            self.info_label.config(text="Trạng thái ban đầu.")
        else:
            step = self.steps[idx - 1]
            self._render_board(step.board, highlight=(step.row, step.col, getattr(step, 'action_type', 'try')))
            self.info_label.config(text=f"Tiến độ: {idx}/{len(self.steps)}")

    def on_step_back_click(self):
        if not self.steps or self.is_playing or self.is_solving: return
        val = int(self.progress_scale.get())
        if val > 0:
            self.progress_scale.set(val - 1)
            self._on_progress_drag(val - 1)

    def on_step_forward_click(self):
        if not self.steps or self.is_playing or self.is_solving: return
        val = int(self.progress_scale.get())
        if val < len(self.steps):
            self.progress_scale.set(val + 1)
            self._on_progress_drag(val + 1)

    # ================= PLAYBACK LOGIC =================

    def on_play_click(self):
        if self.is_playing: return
        self.is_playing = True
        self.is_paused = False
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸ Tạm dừng")
        self.btn_solve.config(state="disabled")
        self.btn_new.config(state="disabled")
        self.btn_edit.config(state="disabled")
        
        if self.progress_scale.get() >= len(self.steps):
            self.progress_scale.set(0)
            
        self._play_next_step()

    def on_pause_click(self):
        if not self.is_playing: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶ Tiếp tục")
            self._log("Đã tạm dừng phát lại.", "info")
        else:
            self.btn_pause.config(text="⏸ Tạm dừng")
            self._play_next_step()

    def on_skip_click(self):
        self.is_playing = False
        self.is_paused = False
        self.progress_scale.set(len(self.steps))
        if self.solution_board:
            self._render_board(self.solution_board)
            self.info_label.config(text="Đã nhảy đến kết quả cuối cùng.")
            self._log("Đã hiển thị kết quả cuối.", "success")
        self._finish_playing()

    def _play_next_step(self):
        if self.is_paused or not self.is_playing: return
            
        current = int(self.progress_scale.get())
        if current >= len(self.steps):
            self._finish_playing()
            return

        step = self.steps[current]
        action_type = getattr(step, 'action_type', 'try')
        
        if action_type == 'new_iteration':
            self._render_board(step.board)
            self._log(f"--- Lặp mới: depth={getattr(step, 'depth_limit', '')} ---", "system")
        elif action_type == 'swap':
            self._render_board(step.board, highlight=(step.row, step.col, 'swap'))
            self._log(f"Hoán đổi tại ({step.row+1}, {step.col+1})", "try")
        elif action_type == 'info':
             self._render_board(step.board)
             self._log(f"Thông tin: {getattr(step, 'value', '')}", "info")
        elif action_type in ('accept_better', 'accept_worse', 'reject'):
            c1 = getattr(step, 'col1', step.col)
            c2 = getattr(step, 'col2', step.value)
            self._render_board(step.board, highlight=((step.row, c1), (step.row, c2), action_type))
            self._log(f"{action_type.upper()}: Hoán đổi ({step.row+1}, {c1+1}) và ({step.row+1}, {c2+1})", "try" if action_type != 'reject' else "error")
        elif action_type in ('restart', 'stuck', 'beam_update'):
            self._render_board(step.board, highlight=(step.row, step.col, action_type))
            self._log(f"{action_type.upper()}: {getattr(step, 'detail', '')}", "system")
        else:
            self._render_board(step.board, highlight=(step.row, step.col, action_type))
            if action_type in ('try', 'assign'):
                self._log(f"Thử điền {step.value} tại ({step.row+1}, {step.col+1})", "try")
            elif action_type == 'backtrack':
                self._log(f"Quay lui tại ({step.row+1}, {step.col+1})", "backtrack")
            elif action_type == 'forward_check_fail':
                self._log(f"Kiểm tra tiến thất bại tại ({step.row+1}, {step.col+1})", "backtrack")

        # Trace Log
        if hasattr(step, 'detail') and step.detail:
            tag = action_type if action_type in ('try', 'backtrack', 'success', 'info', 'system') else 'info'
            self._log_trace(f"[{current+1}/{len(self.steps)}] {step.detail}", tag)

        self.progress_scale.set(current + 1)
        self.root.after(self.play_speed_ms, self._play_next_step)

    def _finish_playing(self):
        self.is_playing = False
        self.btn_play.config(state="normal")
        self.btn_pause.config(state="disabled")
        self.btn_solve.config(state="normal")
        self.btn_new.config(state="normal")
        self.btn_edit.config(state="normal")
        
        if self.progress_scale.get() == len(self.steps):
            if self.solution_board:
                self._render_board(self.solution_board)
                self._log("Kết thúc phát lại.", "success")
            else:
                last_board = self.steps[-1].board if self.steps else self.puzzle
                self._render_board(last_board, highlight='failed')
                self._log("Phát lại hoàn tất. Thuật toán bị kẹt cục bộ/ngõ cụt tại đây.", "error")
                messagebox.showwarning("Kẹt cục bộ", "Thuật toán đã bị kẹt cục bộ / không thể giải được và đã dừng lại.")

    # ================= HELPERS =================
    
    def _log(self, message, tag="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.trace_text.config(state=tk.NORMAL)
        self.trace_text.delete(1.0, tk.END)
        self.trace_text.config(state=tk.DISABLED)

    def _log_trace(self, message, tag="info"):
        self.trace_text.config(state=tk.NORMAL)
        self.trace_text.insert(tk.END, message + "\n", tag)
        self.trace_text.see(tk.END)
        self.trace_text.config(state=tk.DISABLED)

    def _render_board(self, board, highlight=None):
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                label = self.cell_labels[r][c]
                
                # Check original clue safely (in case edit mode changed it)
                is_original_clue = False
                if not self.edit_mode and hasattr(self, 'puzzle'):
                    is_original_clue = self.puzzle[r][c] != 0

                text = str(val) if val != 0 else ""
                label.config(text=text)

                # Edit mode selection highlight
                if self.edit_mode and self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                    continue

                if highlight == 'failed':
                    if is_original_clue:
                        label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                    else:
                        label.config(bg="#FF325A", fg="#FFFFFF") # RED
                    continue

                # Playback highlights
                if highlight is not None and highlight != 'failed':
                    is_highlighted = False
                    action_t = None
                    if isinstance(highlight[0], tuple):
                        cells = highlight[:-1]
                        if (r, c) in cells:
                            is_highlighted = True
                            action_t = highlight[-1]
                    elif highlight[0] == r and highlight[1] == c:
                        is_highlighted = True
                        action_t = highlight[2]
                        
                    if is_highlighted:
                        if action_t in ('try', 'assign'):
                            label.config(bg=COLOR_TRY_BG, fg=COLOR_TRY_TEXT)
                        elif action_t == 'backtrack':
                            label.config(bg=COLOR_BACKTRACK_BG, fg=COLOR_BACKTRACK_TEXT)
                        elif action_t == 'forward_check_fail':
                            label.config(bg="#FF325A", fg="#FFFFFF", text="✕")
                        elif action_t == 'new_iteration':
                            label.config(bg=COLOR_NEW_ITER_FLASH, fg=COLOR_SOLVED_TEXT)
                        elif action_t in ('swap', 'accept_better', 'beam_update'):
                            label.config(bg="#00E473", fg="black")
                        elif action_t == 'accept_worse':
                            label.config(bg="#FFBE00", fg="black")
                        elif action_t == 'reject':
                            label.config(bg="#FF325A", fg="white")
                        elif action_t == 'restart':
                            label.config(bg="#00C6FF", fg="black")
                        elif action_t == 'stuck':
                            label.config(bg="#FF00FF", fg="white")
                        continue

                # Normal state
                if is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val != 0:
                    label.config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
                else:
                    label.config(bg=COLOR_EMPTY_BG, fg=TXT_B)

class SearchStep:
    def __init__(self, board, row, col, value, action_type, detail="", **kwargs):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type # 'try', 'backtrack', 'swap', 'new_iteration', 'info'
        self.detail = detail
        for k, v in kwargs.items():
            setattr(self, k, v)
