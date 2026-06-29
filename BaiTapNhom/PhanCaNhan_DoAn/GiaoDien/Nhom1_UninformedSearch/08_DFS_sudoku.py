# -*- coding: utf-8 -*-
"""
08_DFS_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: UNINFORMED SEARCH (Tìm kiếm mù / không thông tin)
Thuật toán trình bày: Depth-First Search (DFS)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom1_UninformedSearch.dfs_solver import DFSSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="08 - Depth-First Search (DFS)",
        subtitle="Nhóm 1: Uninformed Search",
        algo_name="DFS",
        solver_class=DFSSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
