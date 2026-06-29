# -*- coding: utf-8 -*-
"""
12_LocalBeam_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: LOCAL SEARCH
Thuật toán trình bày: Local Beam Search
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom3_LocalSearch.local_beam_solver import LocalBeamSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="12 - Local Beam Search",
        subtitle="Nhóm 3: Local Search",
        algo_name="Local Beam",
        solver_class=LocalBeamSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
