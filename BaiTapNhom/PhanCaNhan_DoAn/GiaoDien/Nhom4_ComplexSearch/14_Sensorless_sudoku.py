# -*- coding: utf-8 -*-
"""
14_Sensorless_sudoku.py
======================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: COMPLEX SEARCH
Thuật toán trình bày: Sensorless Search (Conformant)
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom4_ComplexSearch.sensorless_solver import SensorlessSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="14 - Sensorless Search",
        subtitle="Nhóm 4: Complex Search",
        algo_name="Sensorless",
        solver_class=SensorlessSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
