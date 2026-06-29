# -*- coding: utf-8 -*-
"""
17_AlphaBeta_SudokuBattle.py
============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: ADVERSARIAL SEARCH (Tìm kiếm đối kháng)
Thuật toán trình bày: Alpha-Beta Pruning
Bài toán áp dụng: "SUDOKU BATTLE" (Luật Ép Ô)
"""

import sys
import os
import copy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle, _fill_full_board, is_valid
from ThuatToan.Nhom6_AdversarialSearch.alpha_beta_solver import AlphaBetaSudokuBattle

BG = "#080816"              
CARD = "#141630"            
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_CLUE_TEXT = "#A0A5D0"
COLOR_CLUE_BG = "#2A2D54"
COLOR_EMPTY_BG = "#1A1C38"
COLOR_P1_BG = "#00E473"     
COLOR_P1_TEXT = "#000000"
COLOR_P2_BG = "#FF325A"     
COLOR_P2_TEXT = "#FFFFFF"

COLOR_TARGET_BG = "#FFD700"  
COLOR_TARGET_TEXT = "#000000"

COLOR_SELECTED_BG = "#2c3e50"
COLOR_AGENT_CORRECT_BG = "#d1fae5"
COLOR_HUMAN_CORRECT_BG = "#d1fae5"
COLOR_HUMAN_CORRECT_TEXT = "#1d4ed8"
COLOR_AGENT_CORRECT_TEXT = "#1d4ed8"


FONT_CELL = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SCORE = ("Segoe UI", 14, "bold")


class AlphaBetaBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Battle - Alpha-Beta (Luật Ép Ô)")
        self.root.configure(bg=BG)
        self.root.minsize(1050, 750)

        self.edit_mode = False
        self.moves_history = []
        
        self._build_ui()
        self.on_new_game_click()
        
        self.root.bind("<Key>", self.on_key_press)

    def _build_ui(self):
        title = tk.Label(self.root, text="Sudoku Battle: You vs Alpha-Beta AI (Luật Ép Ô)",
                          font=FONT_TITLE, bg=BG, fg=ACCENT)
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm 6: Adversarial Search   |   Điền đúng & Chỉ định ô để ép đối thủ. Mắc 5 lỗi là Thua!",
            font=FONT_LABEL, bg=BG, fg=TXT_D
        )
        subtitle.pack(pady=(0, 10))

        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(padx=12, pady=4, fill="both", expand=True)

        left_frame = tk.Frame(main_frame, bg=BG)
        left_frame.grid(row=0, column=0, padx=(0, 16), sticky="n")

        score_frame = tk.Frame(left_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        score_frame.pack(pady=(0, 10), padx=20, fill="x")

        self.human_score_label = tk.Label(score_frame, text="👤 Lỗi Người: 0/5", font=FONT_TITLE, bg=CARD, fg=COLOR_P1_BG)
        self.human_score_label.pack(side="left", padx=20, pady=10)

        self.agent_score_label = tk.Label(score_frame, text="🤖 Lỗi Agent: 0/5", font=FONT_TITLE, bg=CARD, fg=COLOR_P2_BG)
        self.agent_score_label.pack(side="right", padx=20, pady=10)

        grid_frame = tk.Frame(left_frame, bg="#2A2D54", bd=2)
        grid_frame.pack(padx=12, pady=8)

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pad_top = 3 if r % BOX == 0 else 1
                pad_left = 3 if c % BOX == 0 else 1
                pad_bottom = 3 if r == SIZE - 1 else 1
                pad_right = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT,
                    relief="flat", borderwidth=0, cursor="hand2"
                )
                cell.grid(row=r, column=c, padx=(pad_left, pad_right), pady=(pad_top, pad_bottom), sticky="nsew")
                cell.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))
                self.cell_labels[r][c] = cell

        controls_frame = tk.Frame(left_frame, bg=BG)
        controls_frame.pack(pady=4)

        self.diff_var = tk.StringVar(value="Trung bình")
        combo_diff = ttk.Combobox(controls_frame, textvariable=self.diff_var, values=["Dễ", "Trung bình", "Khó"], state="readonly", width=10)
        combo_diff.pack(side="left", padx=4)
        combo_diff.bind("<<ComboboxSelected>>", lambda e: self.on_new_game_click())

        self.btn_new_game = tk.Button(controls_frame, text="↻ Trận mới", command=self.on_new_game_click,
                                       font=FONT_LABEL, bg="#FFBE00", fg="black", activebackground="#D9A200", relief="flat", padx=6, pady=2)
        self.btn_new_game.pack(side="left", padx=4)

        self.btn_edit = tk.Button(controls_frame, text="Tự nhập đề", command=self.toggle_edit_mode,
                                       font=FONT_LABEL, bg="#9D4EDD", fg=TXT_B, activebackground="#7B2CBF", relief="flat", padx=6, pady=2)
        self.btn_edit.pack(side="left", padx=4)

        self.btn_undo = tk.Button(controls_frame, text="↶ Lùi nước", state="disabled",
                                       font=FONT_LABEL, bg=TXT_D, fg=TXT_B, activebackground="#4B5563", relief="flat", padx=6, pady=2)
        self.btn_undo.pack(side="left", padx=4)

        self.btn_stop = tk.Button(controls_frame, text="⏹ Dừng", command=self.on_stop_click, state="disabled",
                                       font=FONT_LABEL, bg="#FF325A", fg=TXT_B, activebackground="#CC2848", relief="flat", padx=6, pady=2)
        self.btn_stop.pack(side="left", padx=4)

        self.info_label = tk.Label(left_frame, text="Trận mới! Bạn đi trước. Hãy click chọn 1 ô trống để ép AI giải.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B, justify="left", wraplength=480)
        self.info_label.pack(pady=(12, 4))

        right_frame = tk.Frame(main_frame, bg="#111827", bd=1, relief="solid")
        right_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#111827", borderwidth=0)
        style.configure("TNotebook.Tab", background="#2c3e50", foreground=TXT_B, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#00E473")], foreground=[("selected", "black")])

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(padx=10, pady=(10, 10), fill="both", expand=True)

        tab_log = tk.Frame(self.notebook, bg="#0b0f14")
        self.notebook.add(tab_log, text="📝 Log Lượt Chơi")
        
        self.log_text = tk.Text(tab_log, bg="#0b0f14", fg=ACCENT,
                                 font=("Consolas", 10), wrap="word", state="disabled")
        self.log_text.pack(fill="both", expand=True)

        tab_tree = tk.Frame(self.notebook, bg="#0b0f14")
        self.notebook.add(tab_tree, text="🌳 Cây Suy Luận AI")
        
        self.tree_log_text = tk.Text(tab_tree, bg="#0b0f14", fg="#00C6FF",
                                      font=("Consolas", 10), wrap="word", state="disabled")
        self.tree_log_text.pack(fill="both", expand=True)

    def _log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _log_tree(self, text):
        self.tree_log_text.config(state="normal")
        self.tree_log_text.insert("end", text + "\n")
        self.tree_log_text.see("end")
        self.tree_log_text.config(state="disabled")

    def _update_score_label(self):
        self.human_score_label.config(text=f"👤 Lỗi Người: {self.game.human_mistakes}/5")
        self.agent_score_label.config(text=f"🤖 Lỗi Agent: {self.game.agent_mistakes}/5")

    def on_new_game_click(self):
        if getattr(self, 'edit_mode', False): return
        diff_map = {"Dễ": 40, "Trung bình": 30, "Khó": 20}
        num = diff_map.get(self.diff_var.get(), 30)
        
        self.puzzle, self.real_solution = generate_puzzle(num_clues=num, seed=None)
        self._start_game_with_puzzle()
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.tree_log_text.config(state="normal")
        self.tree_log_text.delete("1.0", "end")
        self.tree_log_text.config(state="disabled")
        self._log(f"[HỆ THỐNG] Đã tạo trận mới (Độ khó: {self.diff_var.get()})")
        
    def _start_game_with_puzzle(self):
        self.game = AlphaBetaSudokuBattle(self.puzzle, self.real_solution, search_depth=3)
        self.moves_history = []
        self.selected_cell = None
        self.target_cell = None
        self.phase = "HUMAN_CHOOSE_TARGET" 
        self.is_agent_thinking = False
        self.game_over = False
        
        self._render_board()
        self._update_score_label()
        self.info_label.config(text="Trận mới! Bạn đi trước. Hãy click chọn 1 ô trống để ép AI giải.")

    def toggle_edit_mode(self):
        if getattr(self, 'is_agent_thinking', False): return
        
        if not self.edit_mode:
            self.edit_mode = True
            self.btn_edit.config(text="✓ Xác nhận đề", bg="#00E473", fg="black")
            self.btn_new_game.config(state="disabled")
            
            self.puzzle = [[0]*9 for _ in range(9)]
            self.moves_history = []
            self.selected_cell = None
            self.target_cell = None
            self.game_over = True 
            self._render_board()
            self.info_label.config(text="Chế độ nhập đề. Click vào ô và gõ phím số (1-9). Bấm Xác nhận khi xong.")
            self._log("\n[HỆ THỐNG] --- VÀO CHẾ ĐỘ NHẬP ĐỀ TAY ---")
        else:
            temp = copy.deepcopy(self.puzzle)
            if not _fill_full_board(temp):
                messagebox.showerror("Lỗi", "Đề bài bạn nhập KHÔNG HỢP LỆ (hoặc không có lời giải). Vui lòng sửa lại.")
                return
            
            self.real_solution = temp
            self.edit_mode = False
            self.btn_edit.config(text="Tự nhập đề", bg="#9D4EDD", fg=TXT_B)
            self.btn_new_game.config(state="normal")
            
            self._start_game_with_puzzle()
            self._log("\n[HỆ THỐNG] Đã xác nhận đề tự nhập. Trận đấu bắt đầu!")

    def _render_board(self):
        for r in range(SIZE):
            for c in range(SIZE):
                val = self.puzzle[r][c] if self.edit_mode else self.game.board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if self.edit_mode and self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                elif not self.edit_mode and self.target_cell == (r, c):
                    label.config(bg=COLOR_TARGET_BG, fg=COLOR_TARGET_TEXT)
                elif not self.edit_mode and self.selected_cell == (r, c) and self.phase == "HUMAN_CHOOSE_TARGET":
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                elif is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val == 0:
                    label.config(bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT)
                else:
                    if not self.edit_mode:
                        bg = COLOR_HUMAN_CORRECT_BG
                        fg = COLOR_HUMAN_CORRECT_TEXT
                        for m in self.moves_history:
                            if m['row'] == r and m['col'] == c:
                                if m['by_agent']:
                                    bg = COLOR_AGENT_CORRECT_BG
                                    fg = COLOR_AGENT_CORRECT_TEXT
                        label.config(bg=bg, fg=fg)

    def on_cell_click(self, row, col):
        if self.edit_mode:
            self.selected_cell = (row, col)
            self._render_board()
            return
            
        if self.game_over or self.is_agent_thinking:
            return
            
        if self.game.board[row][col] != 0:
            return  
            
        if self.phase == "HUMAN_CHOOSE_TARGET":
            self.selected_cell = (row, col)
            self._render_board()
            self.target_cell = (row, col)
            self.selected_cell = None
            self.phase = "AGENT_TURN"
            self.info_label.config(text=f"Bạn đã ép AI giải ô ({row+1}, {col+1}). Đang chờ AI...")
            self._render_board()
            self._log(f"👤 Bạn đã chọn ô ({row+1}, {col+1}) ép AI giải.")
            self.root.after(300, self._agent_turn)
            
        elif self.phase == "HUMAN_FILL":
            if (row, col) != self.target_cell:
                messagebox.showwarning("Nhắc nhở", "Bạn PHẢI giải ô đang bị tô vàng (ô bị AI ép)!")
                return
            self.selected_cell = (row, col)
            self._render_board()

    def on_key_press(self, event):
        if not self.selected_cell and not self.target_cell: return

        if self.edit_mode:
            r, c = self.selected_cell
            if event.char and event.char in "123456789":
                self.puzzle[r][c] = int(event.char)
                self._render_board()
            elif event.keysym in ("BackSpace", "Delete", "0"):
                self.puzzle[r][c] = 0
                self._render_board()
        else:
            if self.game_over or self.is_agent_thinking or self.phase != "HUMAN_FILL":
                return
                
            r, c = self.target_cell
            if event.char and event.char in "123456789":
                value = int(event.char)
                is_correct = self.game.human_move(r, c, value)
                
                if not is_correct:
                    self._log(f"👤 Người điền {value} tại ({r+1}, {c+1}) -> SAI ✗ (Lỗi: {self.game.human_mistakes}/5)")
                    self._update_score_label()
                    if self.game.is_game_over():
                        self._end_game()
                    else:
                        valid_cands = [str(v) for v in range(1, 10) if is_valid(self.game.board, r, c, v)]
                        hint = f"Các số hợp lệ theo luật ở ô này: {', '.join(valid_cands)}" if valid_cands else "Không có số hợp lệ"
                        self._log(f"   💡 GỢI Ý: {hint}")
                        messagebox.showerror("Sai rồi", f"Số {value} KHÔNG ĐÚNG! Bạn bị ghi nhận 1 lỗi.\n\n💡 Gợi ý: {hint}")
                    return
                else:
                    self.moves_history.append({'row': r, 'col': c, 'val': value, 'by_agent': False})
                    self._log(f"👤 Người điền {value} tại ({r+1}, {c+1}) -> ĐÚNG ✓")
                    self.target_cell = None
                    self.selected_cell = None
                    self._render_board()
                    self._update_score_label()

                    if self.game.is_game_over():
                        self._end_game()
                        return

                    self.phase = "HUMAN_CHOOSE_TARGET"
                    self.info_label.config(text="Tuyệt! Giờ hãy click chọn 1 ô trống bất kỳ để ép AI giải.")

    def on_stop_click(self):
        if not getattr(self, 'is_agent_thinking', False): return
        self._log("Đang dừng Agent...", "error")
        if hasattr(self, 'agent_thread') and self.agent_thread.is_alive():
            import ctypes
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.agent_thread.ident), ctypes.py_object(SystemExit))
        
        self.is_agent_thinking = False
        self.phase = "HUMAN_CHOOSE_TARGET"
        self.btn_stop.config(state="disabled")
        self.info_label.config(text="Đã dừng Agent. Hãy chọn ô ép AI.")
        self._log("Agent đã bị người dùng dừng lại.", "error")

    def _agent_turn(self):
        self.is_agent_thinking = True
        self.btn_stop.config(state="normal")

        def run_agent():
            t0 = time.time()
            
            r, c = self.target_cell
            val = self.game.real_solution[r][c]
            self.game.agent_move(r, c, val)
            
            if self.game.is_game_over():
                self.root.after(0, lambda: self._on_agent_move_done(r, c, val, None, None, [], 0, t1 - t0))
                return
                
            next_r, next_c, trace, nodes = self.game.agent_choose_target()
            t1 = time.time()
            
            self.root.after(0, lambda: self._on_agent_move_done(r, c, val, next_r, next_c, trace, nodes, t1 - t0))

        self.agent_thread = threading.Thread(target=run_agent, daemon=True)
        self.agent_thread.start()

    def _on_agent_move_done(self, solved_r, solved_c, solved_val, next_r, next_c, trace, nodes, elapsed):
        self.btn_stop.config(state="disabled")
        
        self.moves_history.append({'row': solved_r, 'col': solved_c, 'val': solved_val, 'by_agent': True})
        
        self._log(f"🤖 Agent (Alpha-Beta, depth={self.game.search_depth}) suy luận trong {elapsed:.3f}s:")
        self._log(f"   ➜ Agent ĐÃ GIẢI ĐÚNG ô ({solved_r+1}, {solved_c+1}) = {solved_val}")

        if next_r is not None:
            self._log_tree("==================================================")
            self._log_tree(f"🤖 ĐẾN LƯỢT AI CHỌN Ô CHO BẠN")
            self._log_tree(f"- Thuật toán: Alpha-Beta Pruning")
            self._log_tree(f"- Độ sâu tìm kiếm (Depth): {self.game.search_depth}")
            self._log_tree(f"- Số node đã duyệt: {nodes}")
            self._log_tree(f"- Thời gian chạy: {elapsed:.3f}s")
            self._log_tree(f"- Chi tiết đánh giá ứng viên:")
            for t in trace:
                self._log_tree(f"  + Ô ({t['row']+1}, {t['col']+1}): Độ khó = {t.get('hardness', 0)} | Điểm = {t['score']} | Alpha = {t.get('alpha', '')} | Beta = {t.get('beta', '')}")
            self._log_tree(f"=> QUYẾT ĐỊNH: Ép bạn giải ô ({next_r+1}, {next_c+1})")
            self._log_tree("==================================================\n")
        
        if self.game.is_game_over() or next_r is None:
            self.target_cell = None
            self._render_board()
            self._update_score_label()
            self._end_game()
            self.is_agent_thinking = False
            return
            
        self._log(f"   ➜ Agent CHỈ ĐỊNH ô ({next_r+1}, {next_c+1}) cho bạn!\n")
        
        self.target_cell = (next_r, next_c)
        self.phase = "HUMAN_FILL"
        self.is_agent_thinking = False
        
        self._render_board()
        self._update_score_label()
        
        self.info_label.config(text=f"AI ép bạn giải ô ({next_r+1}, {next_c+1}) đang tô Vàng. Gõ phím số (1-9) để điền.")

    def _end_game(self):
        self.game_over = True
        h, a = self.game.human_mistakes, self.game.agent_mistakes
        
        if h >= 5:
            result_text = "🤖 AGENT THẮNG! (Bạn đã mắc đủ 5 lỗi)"
        elif a >= 5:
            result_text = "🎉 NGƯỜI THẮNG! (AI đã mắc đủ 5 lỗi - điều này hiếm khi xảy ra!)"
        else:
            if h < a:
                result_text = f"🎉 NGƯỜI THẮNG! (Hết ô trống. Lỗi: {h} - {a})"
            elif a < h:
                result_text = f"🤖 AGENT THẮNG! (Hết ô trống. Lỗi: {a} - {h})"
            else:
                result_text = f"🤝 HÒA! (Hết ô. Lỗi: {h} - {a})"

        self.info_label.config(text=f"TRẬN ĐẤU KẾT THÚC — {result_text}")
        self._log(f"\n=== KẾT THÚC TRẬN ĐẤU: {result_text} ===")
        messagebox.showinfo("Kết thúc trận đấu", result_text)


def main():
    root = tk.Tk()
    app = AlphaBetaBattleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
