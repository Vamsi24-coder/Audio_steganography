import tkinter as tk
from gui.encode_gui import encode_smtp_dialog
from gui.decode_gui import decode_dialog
from gui.history_gui import history_dialog

# Simple theme variables
DARK_MODE = False

def get_bg_color():
    return "#242424" if DARK_MODE else "#f0f0f0"

def get_fg_color():
    return "#ffffff" if DARK_MODE else "#000000"

def get_button_bg():
    return "#333333" if DARK_MODE else "#4CAF50"

def get_button_fg():
    return "#ffffff"

def get_highlight_color():
    return "#00B8F4" if DARK_MODE else "#2196F3"

def switch_theme(mode, window):
    """Simple theme switching that only affects colors when needed"""
    global DARK_MODE
    DARK_MODE = (mode == "dark")
    apply_theme_to_window(window)

def apply_theme_to_window(window):
    """Apply theme to window - simple and reliable"""
    bg = get_bg_color()
    fg = get_fg_color()
    button_bg = get_button_bg()
    button_fg = get_button_fg()
    highlight = get_highlight_color()
    
    def update_widget(widget):
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Toplevel':
                widget.configure(bg=bg)
            elif widget_class == 'Frame':
                widget.configure(bg=bg)
            elif widget_class == 'Label':
                current_fg = str(widget.cget('fg'))
                # Only change text color for normal labels, keep special colors
                if current_fg in ['#000000', '#ffffff', 'black', 'white', 'SystemWindowText']:
                    widget.configure(bg=bg, fg=fg)
                else:
                    widget.configure(bg=bg)  # Keep special text colors
            elif widget_class == 'Button':
                current_bg = str(widget.cget('bg'))
                # Update themed buttons, leave colored buttons alone
                if current_bg in ['#4CAF50', '#333333', get_bg_color()]:
                    widget.configure(bg=button_bg, fg=button_fg)
                # Leave other colored buttons (like #FF9800, etc.) unchanged
            elif widget_class == 'Entry':
                if DARK_MODE:
                    widget.configure(bg=bg, fg=fg, insertbackground=fg)
                else:
                    widget.configure(bg="white", fg="black", insertbackground="black")
            
            # Recursively apply to children
            for child in widget.winfo_children():
                update_widget(child)
                
        except Exception:
            pass
    
    update_widget(window)

def main_app(user_id, master_root=None):
    """Main application window with simple, reliable theme management"""
    if master_root:
        app_window = tk.Toplevel(master_root)
    else:
        app_window = tk.Toplevel()
    
    app_window.title("Audio Steganography (WAV & FLAC)")
    app_window.geometry("800x600")
    app_window.grab_set()
    
    # Set initial colors (light mode)
    app_window.configure(bg=get_bg_color())
    
    # Make this window visible and bring to front
    app_window.deiconify()
    app_window.lift()
    app_window.focus_force()
    
    # Create simple theme menu
    menubar = tk.Menu(app_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode", 
                          command=lambda: switch_theme("light", app_window))
    theme_menu.add_command(label="🌙 Dark Mode", 
                          command=lambda: switch_theme("dark", app_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    app_window.config(menu=menubar)
    
    # Header
    tk.Label(app_window, text="🎵 Audio Steganography", 
             font=("Arial", 18, "bold"), fg=get_highlight_color(), bg=get_bg_color()).pack(pady=20)
    
    tk.Label(app_window, text="Hide messages, images, or PDF documents in audio files", 
             font=("Arial", 11), fg=get_fg_color(), bg=get_bg_color()).pack(pady=5)
    
    # Supported formats info
    format_frame = tk.Frame(app_window, bg=get_bg_color(), relief="ridge", bd=2)
    format_frame.pack(pady=15, padx=30, fill="x")
    
    tk.Label(format_frame, text="📊 SUPPORTED FORMATS & FEATURES", 
             bg=get_bg_color(), font=("Arial", 11, "bold"), fg=get_fg_color()).pack(pady=5)
    tk.Label(format_frame, text="🎵 Audio: WAV (16-bit PCM) • FLAC (Lossless)", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack()
    tk.Label(format_frame, text="📄 Data: Text Messages • JPG Images • PDF Documents", 
             bg=get_bg_color(), font=("Arial", 9), fg=get_fg_color()).pack()
    tk.Label(format_frame, text="🔒 Method: LSB Steganography (Perfect Quality)", 
             bg=get_bg_color(), font=("Arial", 9), fg="#2E7D32").pack(pady=(0,5))
    
    tk.Label(app_window, text="Choose an Action:", font=("Arial", 12, "bold"), 
             fg=get_fg_color(), bg=get_bg_color()).pack(pady=(20,10))
    
    # Action buttons with themed colors
    tk.Button(app_window, text="🎤 Encode Data in Audio", 
              command=lambda: encode_smtp_dialog(user_id),
              width=25, height=2, bg=get_button_bg(), fg=get_button_fg(), 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(app_window, text="🔍 Decode Audio File", 
              command=lambda: decode_dialog(user_id),
              width=25, height=2, bg="#FF9800", fg="white", 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(app_window, text="📚 View History", 
              command=lambda: history_dialog(user_id),
              width=25, height=2, bg=get_highlight_color(), fg="white", 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    # Status info
    status_frame = tk.Frame(app_window, bg=get_bg_color(), relief="groove", bd=1)
    status_frame.pack(pady=20, padx=30, fill="x")
    
    tk.Label(status_frame, text="ℹ️ QUALITY & COMPATIBILITY", 
             bg=get_bg_color(), font=("Arial", 10, "bold"), fg=get_fg_color()).pack(pady=5)
    tk.Label(status_frame, text="✅ Perfect audio quality preservation with LSB method", 
             bg=get_bg_color(), font=("Arial", 8), fg=get_fg_color()).pack()
    tk.Label(status_frame, text="🔄 Supports both encoding and decoding operations", 
             bg=get_bg_color(), font=("Arial", 8), fg=get_fg_color()).pack()
    tk.Label(status_frame, text="🔐 AES-256 encryption for maximum security", 
             bg=get_bg_color(), font=("Arial", 8), fg=get_fg_color()).pack(pady=(0,5))
    
    return app_window  # Return the window reference
