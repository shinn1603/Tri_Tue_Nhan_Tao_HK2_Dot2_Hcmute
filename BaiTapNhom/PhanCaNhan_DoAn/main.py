# -*- coding: utf-8 -*-
"""
main.py
=======
Giao diện chính để quản lý và chọn chạy 1 trong 18 thuật toán Sudoku.
Giao diện được thiết kế lại hoàn toàn theo phong cách Cyberpunk (Dashboard).
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# ===================== CẤU HÌNH MÀU SẮC =====================
BG_MAIN = "#060814"
CARD_BG = "#0f1423"
CARD_HOVER = "#1a2238"
TXT_WHITE = "#FFFFFF"
TXT_LIGHT = "#D7DAE8"
TXT_DARK = "#646987"
ACCENT_BLUE = "#00B9FF"

# ===================== CẤU TRÚC DỮ LIỆU =====================
GROUPS_DATA = [
    {
        "title": "🔍 1. Uninformed Search — Tìm kiếm mù",
        "color": "#00C6FF", 
        "folder": "Nhom1_UninformedSearch",
        "algorithms": [
            ("DFS", "Depth-First Search", "Tìm kiếm theo chiều sâu", "08_DFS_sudoku.py")
        ]
    },
    {
        "title": "🎯 2. Informed Search — Tìm kiếm có thông tin",
        "color": "#00E473", 
        "folder": "Nhom2_InformedSearch",
        "algorithms": [
            ("A*", "A* Search", "Tìm kiếm A*", "10_AStar_sudoku.py")
        ]
    },
    {
        "title": "🏔️ 3. Local Search — Tìm kiếm cục bộ",
        "color": "#FFD166", 
        "folder": "Nhom3_LocalSearch",
        "algorithms": [
            ("Local Beam", "Local Beam Search", "Tìm kiếm chùm tia cục bộ", "12_LocalBeam_sudoku.py")
        ]
    },
    {
        "title": "🧩 4. Complex Environments — Môi trường phức tạp",
        "color": "#FF6B00", 
        "folder": "Nhom4_ComplexSearch",
        "algorithms": [
            ("Sensorless", "Sensorless Search", "Tìm kiếm không có quan sát", "14_Sensorless_sudoku.py")
        ]
    },
    {
        "title": "🔒 5. CSP — Bài toán thỏa mãn ràng buộc",
        "color": "#9D4EDD", 
        "folder": "Nhom5_CSP",
        "algorithms": [
            ("Min-Conflicts", "Min-Conflicts", "Thuật toán giảm xung đột", "16_MinConflicts_sudoku.py")
        ]
    },
    {
        "title": "⚔️ 6. Adversarial Search — Tìm kiếm đối kháng",
        "color": "#FF325A", 
        "folder": "Nhom6_AdversarialSearch",
        "algorithms": [
            ("Alpha-Beta", "Alpha-Beta Pruning", "Minimax + cắt tỉa α-β", "17_AlphaBeta_SudokuBattle.py")
        ]
    }
]

# ===================== THÀNH PHẦN UI CUSTOM =====================
class AlgoRow(tk.Frame):
    """Một hàng chứa 1 thuật toán, có thể click để chạy."""
    def __init__(self, parent, short_name, title, desc, command, hover_color=CARD_HOVER):
        super().__init__(parent, bg=CARD_BG, cursor="hand2")
        self.command = command
        self.hover_color = hover_color
        self.default_bg = CARD_BG
        
        self.columnconfigure(2, weight=1)

        # Icon mũi tên
        self.lbl_icon = tk.Label(self, text="▶", font=("Segoe UI", 10), bg=CARD_BG, fg=TXT_WHITE)
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=(15, 10), sticky="e")
        
        # Tên viết tắt
        self.lbl_short = tk.Label(self, text=short_name, font=("Segoe UI", 11, "bold"), bg=CARD_BG, fg=TXT_WHITE, width=13, anchor="w")
        self.lbl_short.grid(row=0, column=1, rowspan=2, sticky="w")
        
        # Tên tiếng Anh đầy đủ
        self.lbl_title = tk.Label(self, text=title, font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TXT_LIGHT, anchor="w")
        self.lbl_title.grid(row=0, column=2, sticky="w", pady=(6, 0))
        
        # Mô tả tiếng Việt
        self.lbl_desc = tk.Label(self, text=desc, font=("Segoe UI", 9), bg=CARD_BG, fg=TXT_DARK, anchor="w")
        self.lbl_desc.grid(row=1, column=2, sticky="w", pady=(0, 6))
        
        # Gắn event click & hover cho tất cả thành phần con
        for w in [self, self.lbl_icon, self.lbl_short, self.lbl_title, self.lbl_desc]:
            w.bind("<Enter>", self.on_enter)
            w.bind("<Leave>", self.on_leave)
            w.bind("<Button-1>", self.on_click)

    def on_enter(self, e):
        for w in [self, self.lbl_icon, self.lbl_short, self.lbl_title, self.lbl_desc]:
            w.config(bg=self.hover_color)
            
    def on_leave(self, e):
        for w in [self, self.lbl_icon, self.lbl_short, self.lbl_title, self.lbl_desc]:
            w.config(bg=self.default_bg)
            
    def on_click(self, e):
        self.command()


class MainDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Sudoku Solver — Đồ Án Cuối Kỳ Trí Tuệ Nhân Tạo")
        self.root.geometry("1250x750")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(1000, 600)
        
        self.root.eval('tk::PlaceWindow . center')
        self.build_ui()

    def build_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=BG_MAIN)
        header_frame.pack(fill=tk.X, pady=(25, 15))

        # Title
        title_lbl = tk.Label(header_frame, text="🧩 AI Sudoku Solver", font=("Segoe UI", 28, "bold"), bg=BG_MAIN, fg=ACCENT_BLUE)
        title_lbl.pack()
        
        # Subtitle
        sub_lbl = tk.Label(header_frame, text="Đồ Án Cuối Kỳ — Trí Tuệ Nhân Tạo • 18 Thuật Toán • 6 Nhóm", font=("Segoe UI", 12), bg=BG_MAIN, fg=TXT_DARK)
        sub_lbl.pack(pady=(5, 10))

        # Divider line
        line = tk.Frame(self.root, bg="#116b8c", height=1)
        line.pack(fill=tk.X, padx=40, pady=(0, 20))

        # Main Grid Frame
        grid_frame = tk.Frame(self.root, bg=BG_MAIN)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))

        # Cấu hình grid 3 cột đều nhau
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1, uniform="col")
        grid_frame.rowconfigure(0, weight=1, uniform="row")
        grid_frame.rowconfigure(1, weight=1, uniform="row")

        # Tạo các thẻ (cards)
        for idx, group in enumerate(GROUPS_DATA):
            row = idx // 3
            col = idx % 3
            self.create_group_card(grid_frame, group, row, col)

    def create_group_card(self, parent, group, row, col):
        card_outer = tk.Frame(parent, bg=group["color"], padx=1, pady=1) # Dùng 1 frame bọc ngoài để làm viền (border)
        card_outer.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        card_inner = tk.Frame(card_outer, bg=CARD_BG)
        card_inner.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề nhóm
        lbl_title = tk.Label(card_inner, text=group["title"], font=("Segoe UI", 13, "bold"), 
                             bg=CARD_BG, fg=group["color"], anchor="w", justify="left", wraplength=320)
        lbl_title.pack(fill=tk.X, padx=15, pady=(15, 15))

        # Danh sách thuật toán
        for short_name, title, desc, script_file in group["algorithms"]:
            # Capture variables for the lambda
            cmd = lambda f=group["folder"], s=script_file: self.launch_script(f, s)
            
            row_ui = AlgoRow(card_inner, short_name, title, desc, command=cmd)
            row_ui.pack(fill=tk.X, pady=2, padx=5)

    def launch_script(self, folder, script_file):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GiaoDien", folder, script_file)
        if not os.path.exists(script_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {script_path}")
            return
        
        try:
            subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            messagebox.showerror("Lỗi khởi chạy", f"Có lỗi xảy ra khi mở thuật toán:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainDashboard(root)
    root.mainloop()
