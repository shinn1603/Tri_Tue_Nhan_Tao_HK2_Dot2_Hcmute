# -*- coding: utf-8 -*-
"""
16_MinConflicts_sudoku.py
======================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: CONSTRAINT SATISFACTION PROBLEM (CSP)
Thuật toán trình bày: Min-Conflicts
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom5_CSP.min_conflicts_solver import MinConflictsSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="16 - Min-Conflicts (CSP)",
        subtitle="Nhóm 5: Constraint Satisfaction Problem",
        algo_name="Min-Conflicts",
        solver_class=MinConflictsSolver,
        num_clues=35
    )
    root.mainloop()

if __name__ == "__main__":
    main()
