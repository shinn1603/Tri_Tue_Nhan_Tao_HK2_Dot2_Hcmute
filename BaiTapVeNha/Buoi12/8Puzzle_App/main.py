import tkinter as tk
import sys
import os

# Đảm bảo có thể import các module bên trong 8Puzzle_App
sys.path.append(os.path.dirname(os.path.abspath(__line__ if '__line__' in locals() else __file__)))

from gui.app import PuzzleGUI

def main():
    root = tk.Tk()
    
    # Kích hoạt DPI awareness cho màn hình nét (Windows)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        root.tk.call('tk', 'scaling', 1.5)
    except Exception:
        pass
        
    app = PuzzleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
