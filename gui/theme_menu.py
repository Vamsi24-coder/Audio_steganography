# gui/theme_menu.py
import tkinter as tk
from gui.theme import theme_manager, get_current_mode, CURRENT_THEME as THEME

def add_theme_menu(window):
    """Add theme menu to any window"""
    # Create menu bar if it doesn't exist
    try:
        menubar = window.cget('menu')
        if not menubar:
            menubar = tk.Menu(window, bg=THEME["bg"], fg=THEME["fg"])
            window.config(menu=menubar)
    except:
        menubar = tk.Menu(window, bg=THEME["bg"], fg=THEME["fg"])
        window.config(menu=menubar)
    
    # Add theme menu
    theme_menu = tk.Menu(menubar, tearoff=0, bg=THEME["bg"], fg=THEME["fg"])
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: theme_manager.switch_theme("light"))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: theme_manager.switch_theme("dark"))
    
    menubar.add_cascade(label="Theme", menu=theme_menu)
    
    # Register window with theme manager
    theme_manager.register_window(window)
    
    # Apply current theme
    def apply_theme():
        theme_manager.apply_theme_to_window(window)
        # Update menu colors too
        try:
            menubar.configure(bg=THEME["bg"], fg=THEME["fg"])
            theme_menu.configure(bg=THEME["bg"], fg=THEME["fg"])
        except:
            pass
    
    window.apply_theme = apply_theme
    window.apply_theme()
    
    return window

def add_theme_buttons(parent_frame):
    """Add theme toggle buttons to any frame"""
    theme_frame = tk.Frame(parent_frame, bg=THEME["bg"])
    theme_frame.pack(pady=5)
    
    tk.Label(theme_frame, text="Theme:", font=("Arial", 10), 
             bg=THEME["bg"], fg=THEME["fg"]).pack(side=tk.LEFT, padx=5)
    
    tk.Button(theme_frame, text="☀️ Light", 
              command=lambda: theme_manager.switch_theme("light"),
              font=("Arial", 9), bg=THEME["button_bg"], fg=THEME["button_fg"]).pack(side=tk.LEFT, padx=2)
    
    tk.Button(theme_frame, text="🌙 Dark", 
              command=lambda: theme_manager.switch_theme("dark"),
              font=("Arial", 9), bg=THEME["button_bg"], fg=THEME["button_fg"]).pack(side=tk.LEFT, padx=2)
    
    return theme_frame
