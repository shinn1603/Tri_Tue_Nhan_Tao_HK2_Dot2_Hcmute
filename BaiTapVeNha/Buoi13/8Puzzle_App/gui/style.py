import tkinter as tk
from tkinter import ttk

# Colors
BG_COLOR = "#F0F4F8"
PANEL_BG = "#FFFFFF"
PRIMARY_COLOR = "#0078D7"
PRIMARY_HOVER = "#005A9E"
SUCCESS_COLOR = "#107C10"
TEXT_MAIN = "#333333"
TEXT_MUTED = "#666666"

# Fonts
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 10)

def setup_styles(root):
    root.configure(bg=BG_COLOR)
    
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    
    style.configure("TFrame", background=BG_COLOR)
    style.configure("Panel.TFrame", background=PANEL_BG)
    
    style.configure("TLabelframe", background=PANEL_BG, font=FONT_BOLD, foreground=PRIMARY_COLOR)
    style.configure("TLabelframe.Label", background=PANEL_BG, font=FONT_BOLD, foreground=PRIMARY_COLOR)
    
    style.configure("TLabel", background=PANEL_BG, font=FONT_MAIN, foreground=TEXT_MAIN)
    style.configure("Title.TLabel", background=BG_COLOR, font=FONT_TITLE, foreground=PRIMARY_COLOR)
    
    style.configure("TButton", font=FONT_BOLD, padding=5)
    style.map("TButton",
              background=[('active', PRIMARY_HOVER), ('!disabled', PRIMARY_COLOR), ('disabled', '#CCCCCC')],
              foreground=[('!disabled', 'white'), ('disabled', '#888888')])
              
    style.configure("Success.TButton", font=FONT_BOLD, padding=5)
    style.map("Success.TButton",
              background=[('active', '#0B5A0B'), ('!disabled', SUCCESS_COLOR), ('disabled', '#CCCCCC')],
              foreground=[('!disabled', 'white'), ('disabled', '#888888')])

    style.configure('TNotebook', background=BG_COLOR)
    style.configure('TNotebook.Tab', font=FONT_BOLD, padding=[15, 6])
    style.map('TNotebook.Tab', 
              background=[('selected', PRIMARY_COLOR), ('!selected', '#E1E1E1')],
              foreground=[('selected', 'white'), ('!selected', TEXT_MAIN)])
