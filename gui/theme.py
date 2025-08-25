# gui/theme.py - FINAL FIXED VERSION

# Light Mode Theme (Your Original Colors)
LIGHT_THEME = {
    "bg": "#f0f0f0",                 # Light background
    "fg": "#000000",                 # Black text
    "button_bg": "#4CAF50",          # Your original green buttons  
    "button_fg": "#ffffff",          # White button text
    "highlight": "#2196F3"           # Your original blue highlights
}

# Dark Mode Theme
DARK_THEME = {
    "bg": "#242424",                 # Dark background
    "fg": "#ffffff",                 # White text
    "button_bg": "#333333",          # Dark buttons
    "button_fg": "#ffffff",          # White text
    "highlight": "#00B8F4"           # Light blue highlight
}

# Global theme state
CURRENT_THEME = LIGHT_THEME
CURRENT_MODE = "light"

class ThemeManager:
    def __init__(self):
        self.registered_windows = []
        self.current_mode = "light"
    
    def register_window(self, window):
        if window not in self.registered_windows:
            self.registered_windows.append(window)
    
    def unregister_window(self, window):
        if window in self.registered_windows:
            self.registered_windows.remove(window)
    
    def switch_theme(self, mode):
        global CURRENT_THEME, CURRENT_MODE
        
        if mode == "dark":
            CURRENT_THEME = DARK_THEME
            CURRENT_MODE = "dark"
        else:
            CURRENT_THEME = LIGHT_THEME
            CURRENT_MODE = "light"
        
        self.current_mode = mode
        
        # Force update all windows
        for window in self.registered_windows[:]:
            try:
                if hasattr(window, 'winfo_exists') and window.winfo_exists():
                    self.apply_theme_to_window(window)
            except Exception:
                self.unregister_window(window)
    
    def apply_theme_to_window(self, window):
        """FIXED: Proper theme application with correct text colors"""
        def recursive_set(widget):
            try:
                widget_class = widget.winfo_class()
                
                # Always set background color
                widget.configure(bg=CURRENT_THEME["bg"])
                
                # Handle foreground colors based on widget type and theme mode
                if widget_class == 'Button':
                    # Buttons: Use theme button colors
                    widget.configure(bg=CURRENT_THEME["button_bg"], fg=CURRENT_THEME["button_fg"])
                
                elif widget_class == 'Label':
                    # Labels: Black text in light mode, white in dark mode
                    if CURRENT_MODE == 'light':
                        widget.configure(fg='#000000')  # Black text for light mode
                    else:
                        widget.configure(fg=CURRENT_THEME['fg'])  # White text for dark mode
                
                elif widget_class == 'Entry':
                    # Entry fields: Black text and cursor in light mode
                    if CURRENT_MODE == 'light':
                        widget.configure(fg='#000000', insertbackground='#000000')
                    else:
                        widget.configure(fg=CURRENT_THEME['fg'], insertbackground=CURRENT_THEME['fg'])
                
                elif widget_class in ['Text', 'Listbox']:
                    # Text widgets: Black text in light mode, white in dark mode
                    if CURRENT_MODE == 'light':
                        widget.configure(fg='#000000')
                    else:
                        widget.configure(fg=CURRENT_THEME['fg'])
                
                elif widget_class == 'Frame':
                    # Frames: Only background color (no text color)
                    pass
                
                else:
                    # Other widgets: Apply theme text color only in dark mode
                    if CURRENT_MODE == 'dark':
                        try:
                            widget.configure(fg=CURRENT_THEME['fg'])
                        except:
                            pass
                        
            except Exception:
                pass
            
            # Apply to all children recursively
            for child in widget.winfo_children():
                recursive_set(child)
        
        try:
            # Set window background
            window.configure(bg=CURRENT_THEME["bg"])
            # Apply theme to all widgets
            recursive_set(window)
        except Exception:
            pass

# Global theme manager instance
theme_manager = ThemeManager()

def set_theme(mode="light"):
    theme_manager.switch_theme(mode)

def get_current_theme():
    return CURRENT_THEME

def get_current_mode():
    return CURRENT_MODE
