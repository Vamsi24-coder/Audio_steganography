import tkinter as tk
from tkinter import messagebox
from gui.main_window import main_app
from gui.dialogs import login_dialog, signup_dialog
from gui.project_info import open_project_info
from database import DatabaseManager
import subprocess
import pkg_resources
import sys


# Simplified required packages for WAV and FLAC only
required_packages = ['cryptography', 'pillow', 'PyPDF2', 'bcrypt', 'soundfile', 'numpy']

# Simple theme variables with improved dark colors
DARK_MODE = False

def get_bg_color():
    return "#1e1e2f" if DARK_MODE else "#f0f0f0"  # Improved dark blueish background

def get_fg_color():
    return "#e0e0e0" if DARK_MODE else "#000000"  # Softer white text for better readability

def get_button_bg():
    return "#3a3a5a" if DARK_MODE else "#4CAF50"  # Improved dark button background

def get_button_fg():
    return "#ffffff"

def get_highlight_color():
    return "#4fc3f7" if DARK_MODE else "#2196F3"  # Better light blue highlight

def get_frame_bg():
    return "#2a2a3f" if DARK_MODE else "#f8f9fa"  # Improved frame background for dark mode

def switch_theme(mode, window):
    """Simple theme switching that only affects colors when needed"""
    global DARK_MODE
    DARK_MODE = (mode == "dark")
    apply_theme_to_window(window)

def apply_theme_to_window(window):
    """Apply theme to window - simple and reliable with improved dark colors"""
    bg = get_bg_color()
    fg = get_fg_color()
    button_bg = get_button_bg()
    button_fg = get_button_fg()
    highlight = get_highlight_color()
    frame_bg = get_frame_bg()
    
    def update_widget(widget):
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Tk':
                widget.configure(bg=bg)
            elif widget_class == 'Frame':
                # Handle special frames differently
                current_bg = str(widget.cget('bg'))
                if current_bg == '#f8f9fa' or current_bg == '#2a2a3f':
                    widget.configure(bg=frame_bg)
                else:
                    widget.configure(bg=bg)
            elif widget_class == 'Label':
                current_fg = str(widget.cget('fg'))
                current_bg = str(widget.cget('bg'))
                
                # Handle frame labels
                if current_bg == '#f8f9fa' or current_bg == '#2a2a3f':
                    widget.configure(bg=frame_bg)
                else:
                    widget.configure(bg=bg)
                
                # Only change text color for normal labels, keep special colors
                if current_fg in ['#000000', '#ffffff', 'black', 'white', 'SystemWindowText']:
                    widget.configure(fg=fg)
                elif current_fg in ['#666666', '#999999']:  # Gray text
                    if DARK_MODE:
                        widget.configure(fg="#b0b0c0")  # Lighter gray for dark mode
                # Keep other special colors (like #2E7D32, #1976D2, etc.)
                
            elif widget_class == 'Button':
                current_bg = str(widget.cget('bg'))
                # Update themed buttons, leave colored buttons alone
                if current_bg in ['#4CAF50', '#3a3a5a', get_bg_color()]:
                    widget.configure(bg=button_bg, fg=button_fg)
                # Leave other colored buttons (like #2196F3, #FFC107, etc.) unchanged
                
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


def install_package(package):
    """Install a single package"""
    try:
        if package == 'pillow':
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
        else:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True, f"Successfully installed {package}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to install {package}: {e}"


def check_and_install_dependencies():
    """Check and install required packages"""
    print("Checking dependencies for WAV and FLAC audio steganography...")
    
    failed_packages = []
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"✓ {package} is already installed")
        except pkg_resources.DistributionNotFound:
            print(f"Installing {package}...")
            success, message = install_package(package)
            if not success:
                print(f"✗ {message}")
                failed_packages.append(package)
            else:
                print(f"✓ {message}")
    
    if failed_packages:
        error_msg = (f"Failed to install: {', '.join(failed_packages)}\n\n"
                    "Please install manually:\n" +
                    '\n'.join([f"pip install {pkg}" for pkg in failed_packages]))
        messagebox.showerror("Installation Failed", error_msg)
        return False
    
    print("✓ All dependencies installed!")
    return True


def check_system_compatibility():
    """Check if system supports audio processing"""
    try:
        import numpy as np
        import soundfile as sf
        print("✓ Audio processing libraries loaded successfully")
        return True
    except ImportError as e:
        messagebox.showerror("System Error", 
                           f"Audio libraries failed to load: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        print("=== WAV & FLAC Audio Steganography Application ===")
        print("Starting dependency check...")
        
        if not check_and_install_dependencies():
            sys.exit(1)
        
        if not check_system_compatibility():
            sys.exit(1)
        
        print("Initializing database...")
        try:
            db = DatabaseManager()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"✗ Database failed: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to initialize: {str(e)}")
            sys.exit(1)
        
        print("Starting GUI...")
        root = tk.Tk()
        root.title("WAV & FLAC Audio Steganography")
        root.geometry("500x350")
        
        # Set initial theme colors
        root.configure(bg=get_bg_color())
        
        # Create simple theme menu
        menubar = tk.Menu(root)
        theme_menu = tk.Menu(menubar, tearoff=0)
        theme_menu.add_command(label="☀️ Light Mode", 
                              command=lambda: switch_theme("light", root))
        theme_menu.add_command(label="🌙 Dark Mode", 
                              command=lambda: switch_theme("dark", root))
        menubar.add_cascade(label="Theme", menu=theme_menu)
        root.config(menu=menubar)
        
        tk.Label(root, text="🎵 Audio Steganography 🎵", 
                font=("Arial", 18, "bold"), fg="#2E7D32", bg=get_bg_color()).pack(pady=20)
        
        tk.Label(root, text="Hide your secrets in WAV and FLAC audio files", 
                font=("Arial", 11), fg="#666666", bg=get_bg_color()).pack(pady=5)
        
        # Supported formats
        format_frame = tk.Frame(root, bg=get_frame_bg(), relief="ridge", bd=1)
        format_frame.pack(pady=15, padx=30, fill="x")
        
        tk.Label(format_frame, text="Supported Audio Formats:", 
                bg=get_frame_bg(), font=("Arial", 10, "bold")).pack(pady=5)
        tk.Label(format_frame, text="WAV (PCM) • FLAC (Lossless)", 
                bg=get_frame_bg(), font=("Arial", 9), fg="#1976D2").pack()
        tk.Label(format_frame, text="High-quality LSB steganography with perfect audio preservation", 
                bg=get_frame_bg(), font=("Arial", 8), fg="#666666").pack(pady=(0,5))
        
        # Login/Signup buttons
        button_frame = tk.Frame(root, bg=get_bg_color())
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="🔐 Login", command=login_dialog,
                 width=15, height=2, bg="#4CAF50", fg="white", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="👤 Sign Up", command=signup_dialog,
                 width=15, height=2, bg="#2196F3", fg="white", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Project Info", command=open_project_info,
                 width=15, height=2, bg="#FFC107", fg="black", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        tk.Label(root, text="Secure • Lossless • User-Friendly", 
                font=("Arial", 8), fg="#999999", bg=get_bg_color()).pack(side="bottom", pady=10)
        
        print("✓ Application ready!")
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        print(f"✗ {error_msg}")
        try:
            messagebox.showerror("Application Error", error_msg)
        except:
            pass
        sys.exit(1)
