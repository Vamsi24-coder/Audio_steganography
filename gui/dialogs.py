import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re
import time
import datetime
from database import DatabaseManager
from steganography_utils import (
    encode_data, decode_data, validate_image_file, validate_pdf_file,
    get_file_size_mb, estimate_audio_duration_needed
)

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
    global DARK_MODE
    DARK_MODE = (mode == "dark")
    apply_theme_to_window(window)

def apply_theme_to_window(window):
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
                if current_fg in ['#000000', '#ffffff', 'black', 'white', 'SystemWindowText']:
                    widget.configure(bg=bg, fg=fg)
                elif current_fg == 'gray':
                    widget.configure(bg=bg)
                else:
                    widget.configure(bg=bg)
            elif widget_class == 'Button':
                current_bg = str(widget.cget('bg'))
                if current_bg in ['#4CAF50', '#333333', get_bg_color()]:
                    widget.configure(bg=button_bg, fg=button_fg)
            elif widget_class == 'Entry':
                if DARK_MODE:
                    widget.configure(bg=bg, fg=fg, insertbackground=fg)
                else:
                    widget.configure(bg="white", fg="black", insertbackground="black")
            for child in widget.winfo_children():
                update_widget(child)
        except Exception:
            pass
    update_widget(window)

def login_dialog():
    db = DatabaseManager()
    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("400x340")
    login_window.grab_set()
    login_window.configure(bg=get_bg_color())

    menubar = tk.Menu(login_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode",
                          command=lambda: switch_theme("light", login_window))
    theme_menu.add_command(label="🌙 Dark Mode",
                          command=lambda: switch_theme("dark", login_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    login_window.config(menu=menubar)

    tk.Label(login_window, text="🎵 Audio Steganography Login",
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)

    tk.Label(login_window, text="Username or Email:",
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    username_entry = tk.Entry(login_window, width=40, bg="white" if not DARK_MODE else get_bg_color(),
                                fg="black" if not DARK_MODE else get_fg_color(),
                                insertbackground="black" if not DARK_MODE else get_fg_color())
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:",
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)

    pw_frame = tk.Frame(login_window, bg=get_bg_color())
    pw_frame.pack(pady=5)
    password_var = tk.StringVar()
    password_entry = tk.Entry(pw_frame, width=32, show="*", textvariable=password_var,
                             bg="white" if not DARK_MODE else get_bg_color(),
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color())
    password_entry.pack(side=tk.LEFT)

    password_shown = [False]
    def toggle_password():
        if password_shown[0]:
            password_entry.config(show="*")
            toggle_btn.config(text="Show")
            password_shown[0] = False
        else:
            password_entry.config(show="")
            toggle_btn.config(text="Hide")
            password_shown[0] = True

    toggle_btn = tk.Button(pw_frame, text="Show",
                           width=5, command=toggle_password,
                           bg=get_bg_color(), fg=get_fg_color())
    toggle_btn.pack(side=tk.LEFT, padx=(6,5))

    forgot_btn = tk.Button(
        login_window,
        text="Forgot Password?",
        command=lambda: [login_window.destroy(), forgot_password_dialog()],
        bg=get_bg_color(),
        fg=get_highlight_color(),
        activebackground=get_highlight_color(),
        activeforeground=get_bg_color(),
        font=("Arial", 10, "italic"),
        relief="flat",
        borderwidth=0,
        cursor="hand2"
    )
    forgot_btn.pack(pady=(0, 10))

    def perform_login():
        username = username_entry.get().strip()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        try:
            success, result = db.login(username, password)
            if success:
                root_window = login_window.master
                login_window.destroy()
                if root_window:
                    root_window.destroy()
                new_root = tk.Tk()
                new_root.withdraw()
                from gui.main_window import main_app
                main_app_window = main_app(result, master_root=new_root)
                def on_main_app_close():
                    new_root.quit()
                    new_root.destroy()
                if main_app_window:
                    main_app_window.protocol("WM_DELETE_WINDOW", on_main_app_close)
                new_root.mainloop()
            else:
                messagebox.showerror("Error", result)
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")

    def on_enter(event):
        perform_login()
    password_entry.bind('<Return>', on_enter)
    username_entry.bind('<Return>', on_enter)

    tk.Button(login_window, text="Login", command=perform_login,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12)).pack(pady=10)

    tk.Button(login_window, text="Sign Up",
              command=lambda: [login_window.destroy(), signup_dialog()],
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(pady=5)
    username_entry.focus_set()


def signup_dialog():
    db = DatabaseManager()
    signup_window = tk.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("500x600")
    signup_window.grab_set()
    signup_window.configure(bg=get_bg_color())

    menubar = tk.Menu(signup_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode",
                          command=lambda: switch_theme("light", signup_window))
    theme_menu.add_command(label="🌙 Dark Mode",
                          command=lambda: switch_theme("dark", signup_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    signup_window.config(menu=menubar)

    tk.Label(signup_window, text="Create New Account",
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)

    fields = [
        ("First Name:", "first_name"),
        ("Last Name:", "last_name"),
        ("Username:", "username"),
        ("Email:", "email"),
    ]

    entries = {}
    for label, field in fields:
        tk.Label(signup_window, text=label, bg=get_bg_color(), fg=get_fg_color()).pack(pady=3)
        entry = tk.Entry(signup_window, width=40,
                    bg="white" if not DARK_MODE else get_bg_color(),
                    fg="black" if not DARK_MODE else get_fg_color(),
                    insertbackground="black" if not DARK_MODE else get_fg_color())
        entry.pack(pady=3)
        entries[field] = entry

    # Password field with show/hide
    tk.Label(signup_window, text="Password:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=3)
    pw_frame = tk.Frame(signup_window, bg=get_bg_color())
    pw_frame.pack(pady=3)
    password_var = tk.StringVar()
    password_entry = tk.Entry(pw_frame, width=32, show='*', textvariable=password_var,
                bg="white" if not DARK_MODE else get_bg_color(),
                fg="black" if not DARK_MODE else get_fg_color(),
                insertbackground="black" if not DARK_MODE else get_fg_color())
    password_entry.pack(side=tk.LEFT)
    password_shown = [False]
    def toggle_password():
        if password_shown[0]:
            password_entry.config(show='*')
            toggle_password_btn.config(text="Show")
            password_shown[0] = False
        else:
            password_entry.config(show='')
            toggle_password_btn.config(text="Hide")
            password_shown[0] = True
    toggle_password_btn = tk.Button(pw_frame, text="Show", width=5, command=toggle_password,
                                   bg=get_bg_color(), fg=get_fg_color())
    toggle_password_btn.pack(side=tk.LEFT, padx=(6,5))

    # Confirm password field with show/hide
    tk.Label(signup_window, text="Confirm Password:", bg=get_bg_color(), fg=get_fg_color()).pack(pady=3)
    cpw_frame = tk.Frame(signup_window, bg=get_bg_color())
    cpw_frame.pack(pady=3)
    confirm_var = tk.StringVar()
    confirm_entry = tk.Entry(cpw_frame, width=32, show='*', textvariable=confirm_var,
                bg="white" if not DARK_MODE else get_bg_color(),
                fg="black" if not DARK_MODE else get_fg_color(),
                insertbackground="black" if not DARK_MODE else get_fg_color())
    confirm_entry.pack(side=tk.LEFT)
    confirm_shown = [False]
    def toggle_confirm():
        if confirm_shown[0]:
            confirm_entry.config(show='*')
            toggle_confirm_btn.config(text="Show")
            confirm_shown[0] = False
        else:
            confirm_entry.config(show='')
            toggle_confirm_btn.config(text="Hide")
            confirm_shown[0] = True
    toggle_confirm_btn = tk.Button(cpw_frame, text="Show", width=5, command=toggle_confirm,
                                   bg=get_bg_color(), fg=get_fg_color())
    toggle_confirm_btn.pack(side=tk.LEFT, padx=(6,5))

    tk.Label(signup_window, text="Password: min 10 chars, letters, numbers, special",
             font=("Arial", 8), fg="gray", bg=get_bg_color()).pack()

    status_lbl = tk.Label(signup_window, text="", fg="red", bg=get_bg_color())
    status_lbl.pack()

    def perform_signup():
        values = {k: v.get().strip() for k, v in entries.items()}
        pwd = password_var.get()
        cpwd = confirm_var.get()
        if not all(values.values()) or not pwd or not cpwd:
            status_lbl.config(text="All fields are required", fg="red")
            return
        if pwd != cpwd:
            status_lbl.config(text="Passwords do not match", fg="red")
            return
        try:
            success, message = db.signup(
                values['first_name'], values['last_name'],
                values['username'], values['email'], pwd
            )
            if success:
                messagebox.showinfo("Success", message)
                signup_window.destroy()
                login_dialog()
            else:
                status_lbl.config(text=message, fg="red")
        except Exception as e:
            status_lbl.config(text=f"Signup failed: {str(e)}", fg="red")

    tk.Button(signup_window, text="Create Account", command=perform_signup,
              bg=get_button_bg(), fg=get_button_fg(), font=("Arial", 12)).pack(pady=20)

    tk.Button(signup_window, text="Back to Login",
              command=lambda: [signup_window.destroy(), login_dialog()],
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(pady=5)

def forgot_password_dialog():
    db = DatabaseManager()
    forgot_window = tk.Toplevel()
    forgot_window.title("Reset Password")
    forgot_window.geometry("450x450")  # Adjusted height
    forgot_window.grab_set()
    forgot_window.configure(bg=get_bg_color())

    menubar = tk.Menu(forgot_window)
    theme_menu = tk.Menu(menubar, tearoff=0)
    theme_menu.add_command(label="☀️ Light Mode",
                          command=lambda: switch_theme("light", forgot_window))
    theme_menu.add_command(label="🌙 Dark Mode",
                          command=lambda: switch_theme("dark", forgot_window))
    menubar.add_cascade(label="Theme", menu=theme_menu)
    forgot_window.config(menu=menubar)

    tk.Label(forgot_window, text="Reset Password",
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)

    # Single field for username OR email
    tk.Label(forgot_window, text="Username or Email:",
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    identifier_entry = tk.Entry(forgot_window, width=40,
                               bg="white" if not DARK_MODE else get_bg_color(),
                               fg="black" if not DARK_MODE else get_fg_color(),
                               insertbackground="black" if not DARK_MODE else get_fg_color())
    identifier_entry.pack(pady=5)

    # Info label
    tk.Label(forgot_window, text="Enter your username or email address",
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=2)

    # New Password field with show/hide
    tk.Label(forgot_window, text="New Password:",
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=(15,5))

    pw_frame = tk.Frame(forgot_window, bg=get_bg_color())
    pw_frame.pack(pady=5)
    password_var = tk.StringVar()
    password_entry = tk.Entry(pw_frame, width=32, show="*", textvariable=password_var,
                             bg="white" if not DARK_MODE else get_bg_color(),
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color())
    password_entry.pack(side=tk.LEFT)

    password_shown = [False]
    def toggle_password():
        if password_shown[0]:
            password_entry.config(show="*")
            toggle_password_btn.config(text="Show")
            password_shown[0] = False
        else:
            password_entry.config(show="")
            toggle_password_btn.config(text="Hide")
            password_shown[0] = True

    toggle_password_btn = tk.Button(pw_frame, text="Show",
                                   width=5, command=toggle_password,
                                   bg=get_bg_color(), fg=get_fg_color())
    toggle_password_btn.pack(side=tk.LEFT, padx=(6,5))

    # Confirm Password field with show/hide
    tk.Label(forgot_window, text="Confirm New Password:",
             bg=get_bg_color(), fg=get_fg_color()).pack(pady=(10,5))

    cpw_frame = tk.Frame(forgot_window, bg=get_bg_color())
    cpw_frame.pack(pady=5)
    confirm_var = tk.StringVar()
    confirm_entry = tk.Entry(cpw_frame, width=32, show="*", textvariable=confirm_var,
                            bg="white" if not DARK_MODE else get_bg_color(),
                            fg="black" if not DARK_MODE else get_fg_color(),
                            insertbackground="black" if not DARK_MODE else get_fg_color())
    confirm_entry.pack(side=tk.LEFT)

    confirm_shown = [False]
    def toggle_confirm():
        if confirm_shown[0]:
            confirm_entry.config(show="*")
            toggle_confirm_btn.config(text="Show")
            confirm_shown[0] = False
        else:
            confirm_entry.config(show="")
            toggle_confirm_btn.config(text="Hide")
            confirm_shown[0] = True

    toggle_confirm_btn = tk.Button(cpw_frame, text="Show",
                                  width=5, command=toggle_confirm,
                                  bg=get_bg_color(), fg=get_fg_color())
    toggle_confirm_btn.pack(side=tk.LEFT, padx=(6,5))

    # Password requirements
    tk.Label(forgot_window, text="Password: min 10 chars, letters, numbers, special",
             font=("Arial", 8), fg="gray", bg=get_bg_color()).pack(pady=5)

    # Status label for validation messages
    status_label = tk.Label(forgot_window, text="", font=("Arial", 9), bg=get_bg_color())
    status_label.pack(pady=5)

    def perform_reset():
        identifier = identifier_entry.get().strip()
        new_password = password_var.get()
        confirm_password = confirm_var.get()

        # Validation
        if not identifier:
            status_label.config(text="❌ Please enter your username or email", fg="red")
            return

        if not new_password:
            status_label.config(text="❌ Please enter a new password", fg="red")
            return

        if not confirm_password:
            status_label.config(text="❌ Please confirm your password", fg="red")
            return

        if new_password != confirm_password:
            status_label.config(text="❌ Passwords do not match", fg="red")
            return

        # Clear status
        status_label.config(text="", fg=get_fg_color())

        try:
            success, message = db.reset_password(identifier, new_password)
            
            if success:
                messagebox.showinfo("Success", message)
                forgot_window.destroy()
                login_dialog()
            else:
                status_label.config(text=f"❌ {message}", fg="red")
        except Exception as e:
            status_label.config(text=f"❌ Password reset failed: {str(e)}", fg="red")

    tk.Button(forgot_window, text="Reset Password", command=perform_reset,
              bg="#FF9800", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

    tk.Button(forgot_window, text="Back to Login",
              command=lambda: [forgot_window.destroy(), login_dialog()],
              bg=get_highlight_color(), fg="white", font=("Arial", 10)).pack(pady=5)

    # Focus on identifier field when dialog opens
    identifier_entry.focus_set()
