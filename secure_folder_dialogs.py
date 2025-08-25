# secure_folder_dialogs.py
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from database import DatabaseManager


# Simple theme variables - sync with main app
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


def set_theme_mode(dark_mode):
    """Set theme mode from parent application"""
    global DARK_MODE
    DARK_MODE = dark_mode


def secure_folder_selection_dialog(user_id, data_type, parent=None):
    """Main dialog to select secure folder option for saving decoded files"""
    db = DatabaseManager()
    
    selection_window = tk.Toplevel(parent) if parent else tk.Toplevel()
    selection_window.title("🔒 Secure Folder Options")
    selection_window.geometry("580x480")  # Smaller, should fit on most screens
    selection_window.grab_set()
    selection_window.configure(bg=get_bg_color())
    
    # Center the window
    selection_window.transient(parent)
    selection_window.update_idletasks()
    width = selection_window.winfo_width()
    height = selection_window.winfo_height()
    x = (selection_window.winfo_screenwidth() // 2) - (width // 2)
    y = (selection_window.winfo_screenheight() // 2) - (height // 2)
    selection_window.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None, "use_security": False, "cancelled": True}
    
    # Header
    tk.Label(selection_window, text="🔒 Secure Folder Options", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    tk.Label(selection_window, text=f"Choose how to save your decoded {data_type}:", 
             font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(pady=10)
    
    # Check 7-Zip encryption support
    zip_available, zip_msg = db.check_7zip_available()
    if zip_available:
        encryption_info = "🛡️ 7-Zip AES-256 encryption available"
        encryption_color = "green"
    else:
        encryption_info = f"⚠️ 7-Zip encryption unavailable: {zip_msg}"
        encryption_color = "orange"
    
    tk.Label(selection_window, text=encryption_info, 
             font=("Arial", 10), fg=encryption_color, bg=get_bg_color()).pack(pady=5)
    
    # Options frame
    options_frame = tk.Frame(selection_window, bg=get_bg_color())
    options_frame.pack(pady=20, padx=20, fill="x")
    
    # Option 1: No security (standard folder)
    def choose_no_security():
        result["use_security"] = False
        result["cancelled"] = False
        selection_window.destroy()
    
    tk.Button(options_frame, text="📁 Save Without Security", 
              command=choose_no_security,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
              width=32, height=2).pack(pady=8)
    tk.Label(options_frame, text="Save to user-specific folder without password protection", 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Option 2: Use last used secure folder
    last_folder = db.get_last_used_folder(user_id)
    if last_folder:
        def use_last_folder():
            folder_password = ask_folder_password(selection_window, last_folder[1])
            if folder_password:
                success, message = db.verify_folder_password(last_folder[0], folder_password, user_id)
                if success:
                    result["folder_id"] = last_folder[0]
                    result["use_security"] = True
                    result["cancelled"] = False
                    selection_window.destroy()
                else:
                    messagebox.showerror("Access Denied", message, parent=selection_window)
        
        # Check encryption status - updated for 7-Zip
        is_encrypted = len(last_folder) > 4 and last_folder[4]  # is_encrypted field
        encryption_method = last_folder[5] if len(last_folder) > 5 else 'none'
        is_hidden = len(last_folder) > 7 and last_folder[7]  # is_hidden field
        
        # Determine encryption icon and status
        if is_encrypted and encryption_method == '7zip_aes256':
            encryption_icon = "🛡️"
            encryption_status = "7-Zip AES-256 Encrypted"
        elif is_hidden:
            encryption_icon = "🫥"
            encryption_status = "Hidden + App-level security"
        else:
            encryption_icon = "🔓"
            encryption_status = "App-level security only"
        
        last_used_date = last_folder[3][:16] if last_folder[3] else "Never used"
        button_text = f"{encryption_icon} Use Last: {last_folder[1][:16]}{'...' if len(last_folder[1]) > 16 else ''}"
        
        tk.Button(options_frame, text=button_text, 
                  command=use_last_folder,
                  bg="#FF9800", fg="white", font=("Arial", 12, "bold"),
                  width=32, height=2).pack(pady=8)
        
        tk.Label(options_frame, text=f"Last used: {last_used_date} • {encryption_status}", 
                 font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Option 3: Select existing secure folder
    folders = db.get_user_secure_folders(user_id)
    if folders:
        def select_existing_folder():
            folder_id = select_folder_dialog(selection_window, folders)
            if folder_id:
                folder_info = db.get_folder_info(folder_id, user_id)
                if folder_info:
                    folder_password = ask_folder_password(selection_window, folder_info[1])
                    if folder_password:
                        success, message = db.verify_folder_password(folder_id, folder_password, user_id)
                        if success:
                            result["folder_id"] = folder_id
                            result["use_security"] = True
                            result["cancelled"] = False
                            selection_window.destroy()
                        else:
                            messagebox.showerror("Access Denied", message, parent=selection_window)
        
        # Count encrypted folders - updated for 7-Zip
        encrypted_count = sum(1 for folder in folders if len(folder) > 5 and folder[5] and folder[6] == '7zip_aes256')
        hidden_count = sum(1 for folder in folders if len(folder) > 8 and folder[8])
        
        tk.Button(options_frame, text="📂 Select Existing Folder", 
                  command=select_existing_folder,
                  bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                  width=32, height=2).pack(pady=8)
        
        folder_stats = f"Choose from {len(folders)} folders ({encrypted_count} 7-Zip encrypted, {hidden_count} hidden)"
        tk.Label(options_frame, text=folder_stats, 
                 font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Option 4: Create new secure folder
    def create_new_folder():
        folder_data = create_folder_dialog(selection_window, user_id)
        if folder_data:
            result["folder_id"] = folder_data
            result["use_security"] = True
            result["cancelled"] = False
            selection_window.destroy()
    
    tk.Button(options_frame, text="➕ Create New Secure Folder", 
              command=create_new_folder,
              bg="#9C27B0", fg="white", font=("Arial", 12, "bold"),
              width=32, height=2).pack(pady=8)
    
    # Enhanced creation info based on available encryption
    if zip_available:
        create_info = "Password protection + 7-Zip AES-256 encryption + folder hiding"
    else:
        create_info = "Password protection + folder hiding (7-Zip encryption unavailable)"
    
    tk.Label(options_frame, text=create_info, 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(pady=(0,15))
    
    # Cancel button
    tk.Button(selection_window, text="❌ Cancel", 
              command=selection_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(pady=15)
    
    selection_window.wait_window()
    return result


def ask_folder_password(parent, folder_name):
    """Dialog to ask for folder password with enhanced security info - FIXED VERSION"""
    password_window = tk.Toplevel(parent)
    password_window.title("🔐 Folder Password")
    password_window.geometry("500x280")  # Slightly larger for security info
    password_window.grab_set()
    password_window.configure(bg=get_bg_color())
    
    # Center the window
    password_window.transient(parent)
    password_window.update_idletasks()
    width = password_window.winfo_width()
    height = password_window.winfo_height()
    x = (password_window.winfo_screenwidth() // 2) - (width // 2)
    y = (password_window.winfo_screenheight() // 2) - (height // 2)
    password_window.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"password": None}
    
    tk.Label(password_window, text=f"🔐 Enter Password for Secure Folder", 
             font=("Arial", 14, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    tk.Label(password_window, text=f"'{folder_name}'", 
             font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(pady=5)
    
    # Security notice
    tk.Label(password_window, text="This password will decrypt your secure files", 
             font=("Arial", 9), fg="orange", bg=get_bg_color()).pack(pady=5)
    
    # Password entry with show/hide
    pw_frame = tk.Frame(password_window, bg=get_bg_color())
    pw_frame.pack(pady=20)
    
    password_var = tk.StringVar()
    password_entry = tk.Entry(pw_frame, width=30, show="*", textvariable=password_var,
                             bg="white" if not DARK_MODE else get_bg_color(),
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color(),
                             font=("Arial", 11))
    password_entry.pack(side=tk.LEFT, padx=5)
    
    password_shown = [False]
    def toggle_password():
        if password_shown[0]:
            password_entry.config(show="*")
            toggle_btn.config(text="👁️")
            password_shown[0] = False
        else:
            password_entry.config(show="")
            toggle_btn.config(text="🙈")
            password_shown[0] = True
    
    toggle_btn = tk.Button(pw_frame, text="👁️", width=3, command=toggle_password,
                          bg=get_bg_color(), fg=get_fg_color(), font=("Arial", 10))
    toggle_btn.pack(side=tk.LEFT, padx=5)
    
    def submit_password():
        if password_var.get().strip():
            result["password"] = password_var.get()
            password_window.destroy()
        else:
            messagebox.showwarning("Empty Password", "Please enter a password.", parent=password_window)
    
    def on_enter(event):
        submit_password()
    
    password_entry.bind('<Return>', on_enter)
    password_entry.focus_set()
    
    # Forgot password option - FIXED: No more "transparent" error
    def forgot_password():
        if messagebox.askyesno("Forgot Password", 
                             "Do you want to reset the password for this folder?\n"
                             "This will require verification and create a new password.",
                             parent=password_window):
            password_window.destroy()
            show_forgot_password_dialog(parent, folder_name)
    
    # ✅ FIXED: Using proper background color instead of "transparent"
    tk.Button(password_window, text="❓ Forgot Password?", command=forgot_password,
              bg=get_bg_color(), fg=get_highlight_color(), font=("Arial", 9, "underline"),
              bd=0, relief="flat", cursor="hand2").pack(pady=5)
    
    # Buttons
    button_frame = tk.Frame(password_window, bg=get_bg_color())
    button_frame.pack(pady=15)
    
    tk.Button(button_frame, text="🔓 Unlock", command=submit_password,
              bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=password_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    
    password_window.wait_window()
    return result["password"]


def select_folder_dialog(parent, folders):
    """Dialog to select from existing folders with 7-Zip encryption status"""
    select_window = tk.Toplevel(parent)
    select_window.title("📂 Select Secure Folder")
    select_window.geometry("650x520")  # Larger for enhanced encryption info
    select_window.grab_set()
    select_window.configure(bg=get_bg_color())
    
    # Center the window
    select_window.transient(parent)
    select_window.update_idletasks()
    width = select_window.winfo_width()
    height = select_window.winfo_height()
    x = (select_window.winfo_screenwidth() // 2) - (width // 2)
    y = (select_window.winfo_screenheight() // 2) - (height // 2)
    select_window.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None}
    
    tk.Label(select_window, text="📂 Select Secure Folder", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    # Folders listbox with scrollbar
    folders_frame = tk.Frame(select_window, bg=get_bg_color())
    folders_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    tk.Label(folders_frame, text="Your Secure Folders:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(0,10))
    
    # Listbox with scrollbar
    list_frame = tk.Frame(folders_frame, bg=get_bg_color())
    list_frame.pack(fill="both", expand=True)
    
    listbox = tk.Listbox(list_frame, height=12, font=("Arial", 10),
                        bg="white" if not DARK_MODE else get_bg_color(),
                        fg="black" if not DARK_MODE else get_fg_color(),
                        selectbackground=get_highlight_color())
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    listbox.configure(yscrollcommand=scrollbar.set)
    
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Populate listbox with enhanced encryption status
    for i, folder in enumerate(folders):
        folder_name = folder[1]
        folder_path = folder[2]
        created_date = folder[3][:10] if folder[3] else "Unknown"
        is_encrypted = len(folder) > 5 and folder[5]  # is_encrypted field
        encryption_method = folder[6] if len(folder) > 6 else 'none'
        is_hidden = len(folder) > 8 and folder[8] if len(folder) > 8 else False
        
        # Enhanced encryption indicators for 7-Zip
        if is_encrypted and encryption_method == '7zip_aes256':
            encryption_icon = "🛡️"
            encryption_text = "7ZIP"
        elif is_hidden:
            encryption_icon = "🫥"
            encryption_text = "HIDE"
        else:
            encryption_icon = "🔓"
            encryption_text = "APP"
        
        display_text = f"{encryption_icon} {folder_name} | {folder_path[:25]}{'...' if len(folder_path) > 25 else ''} | {encryption_text} | {created_date}"
        listbox.insert(tk.END, display_text)
    
    # Selection info
    info_label = tk.Label(folders_frame, text="Select a folder and click 'Choose Folder'", 
                         font=("Arial", 9), fg="gray", bg=get_bg_color())
    info_label.pack(pady=10)
    
    def on_select(event):
        selection = listbox.curselection()
        if selection:
            folder_info = folders[selection[0]]
            is_encrypted = len(folder_info) > 5 and folder_info[5]
            encryption_method = folder_info[6] if len(folder_info) > 6 else 'none'
            is_hidden = len(folder_info) > 8 and folder_info[8] if len(folder_info) > 8 else False
            
            # Enhanced encryption status display
            if is_encrypted and encryption_method == '7zip_aes256':
                encryption_status = "7-Zip AES-256 Encrypted + Password Protected"
            elif is_hidden:
                encryption_status = "Hidden from File Explorer + App Password"
            else:
                encryption_status = "App-level password protection only"
                
            info_text = f"Selected: {folder_info[1]}\nPath: {folder_info[2]}\nSecurity: {encryption_status}"
            info_label.config(text=info_text, fg=get_fg_color())
    
    listbox.bind('<<ListboxSelect>>', on_select)
    
    def select_folder():
        selection = listbox.curselection()
        if selection:
            result["folder_id"] = folders[selection[0]][0]
            select_window.destroy()
        else:
            messagebox.showwarning("No Selection", "Please select a folder.", parent=select_window)
    
    def on_double_click(event):
        select_folder()
    
    listbox.bind('<Double-1>', on_double_click)
    
    # Enhanced Legend
    legend_frame = tk.Frame(folders_frame, bg=get_bg_color(), relief="ridge", bd=1)
    legend_frame.pack(fill="x", pady=5)
    
    tk.Label(legend_frame, text="Legend: 🛡️ 7-Zip AES-256 • 🫥 Hidden Folder • 🔓 App Password Only", 
             font=("Arial", 8), bg=get_bg_color(), fg="gray").pack(pady=3)
    
    # Buttons
    button_frame = tk.Frame(select_window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    tk.Button(button_frame, text="✅ Choose Folder", command=select_folder,
              bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=select_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
    
    select_window.wait_window()
    return result["folder_id"]


def create_folder_dialog(parent, user_id):
    """Dialog to create new secure folder with 7-Zip encryption support and scrollable content"""
    db = DatabaseManager()
    
    create_window = tk.Toplevel(parent)
    create_window.title("🔒 Create New Secure Folder")
    create_window.geometry("700x500")  # Fixed smaller size
    create_window.grab_set()
    create_window.configure(bg=get_bg_color())
    
    # Center the window
    create_window.transient(parent)
    create_window.update_idletasks()
    width = create_window.winfo_width()
    height = create_window.winfo_height()
    x = (create_window.winfo_screenwidth() // 2) - (width // 2)
    y = (create_window.winfo_screenheight() // 2) - (height // 2)
    create_window.geometry(f"{width}x{height}+{x}+{y}")
    
    result = {"folder_id": None}
    
    # Header (fixed at top)
    tk.Label(create_window, text="🔒 Create New Secure Folder", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=10)
    
    # Check 7-Zip encryption support and show status
    zip_available, zip_msg = db.check_7zip_available()
    
    # ✅ FIXED: Handle the 3-value return from get_user_security_preferences
    try:
        preferences = db.get_user_security_preferences(user_id)
        if len(preferences) >= 2:
            use_7zip, use_hiding = preferences[0], preferences[1]
            # If there's a third value (compression_level), we can access it as preferences[2] if needed
        else:
            use_7zip, use_hiding = False, False
    except (ValueError, TypeError):
        # Fallback values if unpacking fails
        use_7zip, use_hiding = False, False
    
    if zip_available and use_7zip:
        encryption_status = "🛡️ 7-Zip AES-256 encryption will be automatically applied"
        status_color = "green"
    elif zip_available and not use_7zip:
        encryption_status = "🔓 7-Zip encryption available but disabled in preferences"
        status_color = "orange"
    else:
        encryption_status = f"⚠️ 7-Zip encryption unavailable: {zip_msg}"
        status_color = "red"
    
    tk.Label(create_window, text=encryption_status, 
             font=("Arial", 9), fg=status_color, bg=get_bg_color()).pack(pady=2)
    
    # ===== SCROLLABLE CONTENT AREA =====
    # Create canvas and scrollbar for scrollable content
    canvas_frame = tk.Frame(create_window, bg=get_bg_color())
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas = tk.Canvas(canvas_frame, bg=get_bg_color(), highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=get_bg_color())
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Enable mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _bind_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _unbind_from_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', _bind_to_mousewheel)
    canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    # ===== ALL FORM CONTENT GOES IN scrollable_frame =====
    form_frame = scrollable_frame  # Use scrollable_frame instead of create_window
    
    # Folder name
    tk.Label(form_frame, text="Folder Name:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(15,5), padx=20)
    name_entry = tk.Entry(form_frame, width=50, font=("Arial", 11),
                         bg="white" if not DARK_MODE else get_bg_color(),
                         fg="black" if not DARK_MODE else get_fg_color(),
                         insertbackground="black" if not DARK_MODE else get_fg_color())
    name_entry.pack(anchor="w", pady=5, padx=20)
    tk.Label(form_frame, text="Choose a unique name for your secure folder", 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(anchor="w", padx=20)
    
    # Folder path
    tk.Label(form_frame, text="Folder Location:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(20,5), padx=20)
    
    path_frame = tk.Frame(form_frame, bg=get_bg_color())
    path_frame.pack(anchor="w", pady=5, fill="x", padx=20)
    
    path_var = tk.StringVar()
    path_entry = tk.Entry(path_frame, textvariable=path_var, width=35, font=("Arial", 11),
                         bg="white" if not DARK_MODE else get_bg_color(),
                         fg="black" if not DARK_MODE else get_fg_color(),
                         insertbackground="black" if not DARK_MODE else get_fg_color())
    path_entry.pack(side=tk.LEFT, padx=(0,10))
    
    def browse_path():
        path = filedialog.askdirectory(title="Select Folder Location", parent=create_window)
        if path:
            path_var.set(path)
    
    tk.Button(path_frame, text="📁 Browse", command=browse_path,
              bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    tk.Label(form_frame, text="Choose where to create your secure folder", 
             font=("Arial", 9), fg="gray", bg=get_bg_color()).pack(anchor="w", padx=20)
    
    # Password fields
    tk.Label(form_frame, text="Folder Password:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(20,5), padx=20)
    
    # Password entry with show/hide
    pw_frame = tk.Frame(form_frame, bg=get_bg_color())
    pw_frame.pack(anchor="w", pady=5, padx=20)
    
    password_var = tk.StringVar()
    password_entry = tk.Entry(pw_frame, width=30, show="*", textvariable=password_var, font=("Arial", 11),
                             bg="white" if not DARK_MODE else get_bg_color(),
                             fg="black" if not DARK_MODE else get_fg_color(),
                             insertbackground="black" if not DARK_MODE else get_fg_color())
    password_entry.pack(side=tk.LEFT, padx=(0,10))
    
    password_shown = [False]
    def toggle_password():
        if password_shown[0]:
            password_entry.config(show="*")
            toggle_btn.config(text="👁️")
            password_shown[0] = False
        else:
            password_entry.config(show="")
            toggle_btn.config(text="🙈")
            password_shown[0] = True
    
    toggle_btn = tk.Button(pw_frame, text="👁️", width=3, command=toggle_password,
                          bg=get_bg_color(), fg=get_fg_color(), font=("Arial", 10))
    toggle_btn.pack(side=tk.LEFT)
    
    # Confirm password
    tk.Label(form_frame, text="Confirm Password:", 
             font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(15,5), padx=20)
    
    cpw_frame = tk.Frame(form_frame, bg=get_bg_color())
    cpw_frame.pack(anchor="w", pady=5, padx=20)
    
    confirm_var = tk.StringVar()
    confirm_entry = tk.Entry(cpw_frame, width=30, show="*", textvariable=confirm_var, font=("Arial", 11),
                            bg="white" if not DARK_MODE else get_bg_color(),
                            fg="black" if not DARK_MODE else get_fg_color(),
                            insertbackground="black" if not DARK_MODE else get_fg_color())
    confirm_entry.pack(side=tk.LEFT, padx=(0,10))
    
    confirm_shown = [False]
    def toggle_confirm():
        if confirm_shown[0]:
            confirm_entry.config(show="*")
            toggle_confirm_btn.config(text="👁️")
            confirm_shown[0] = False
        else:
            confirm_entry.config(show="")
            toggle_confirm_btn.config(text="🙈")
            confirm_shown[0] = True
    
    toggle_confirm_btn = tk.Button(cpw_frame, text="👁️", width=3, command=toggle_confirm,
                                  bg=get_bg_color(), fg=get_fg_color(), font=("Arial", 10))
    toggle_confirm_btn.pack(side=tk.LEFT)
    
    # Password requirements (compact version)
    req_frame = tk.Frame(form_frame, bg=get_bg_color(), relief="ridge", bd=1)
    req_frame.pack(fill="x", pady=10, padx=20)
    
    tk.Label(req_frame, text="🔐 Password Requirements:", 
             font=("Arial", 9, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", padx=8, pady=3)
    req_text = "• 8+ chars • Uppercase • Lowercase • Number • Special char (!@#$%^&*)"
    tk.Label(req_frame, text=req_text, 
             font=("Arial", 8), bg=get_bg_color(), fg=get_fg_color(), wraplength=600).pack(anchor="w", padx=15, pady=(0,3))
    
    # Security info (compact version)
    security_frame = tk.Frame(form_frame, bg=get_bg_color(), relief="ridge", bd=1)
    security_frame.pack(fill="x", pady=8, padx=20)
    
    tk.Label(security_frame, text="🛡️ Multi-Layer Security Features:", 
             font=("Arial", 9, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", padx=8, pady=3)
    
    security_features = ["• App-level password protection"]
    
    if zip_available and use_7zip:
        security_features.append("• 7-Zip AES-256 encryption (military-grade)")
        security_features.append("• Encrypted file names")
    else:
        security_features.append("• 7-Zip AES-256 encryption not available")
    
    if use_hiding:
        security_features.append("• Windows folder hiding")
    
    security_features.append("• Automatic compression")
    
    security_text = " ".join(security_features)
    tk.Label(security_frame, text=security_text, 
             font=("Arial", 8), bg=get_bg_color(), fg="green", wraplength=600).pack(anchor="w", padx=15, pady=(0,3))
    
    # Status label
    status_label = tk.Label(form_frame, text="", font=("Arial", 10), bg=get_bg_color())
    status_label.pack(pady=10)
    
    # Add some bottom padding
    tk.Label(form_frame, text="", bg=get_bg_color()).pack(pady=20)
    
    # ===== BUTTONS (FIXED AT BOTTOM) =====
    def create_folder():
        folder_name = name_entry.get().strip()
        folder_path = path_var.get().strip()
        password = password_var.get()
        confirm_password = confirm_var.get()
        
        # Validation
        if not folder_name:
            status_label.config(text="❌ Please enter a folder name", fg="red")
            name_entry.focus_set()
            return
        if not folder_path:
            status_label.config(text="❌ Please select a folder path", fg="red")
            return
        if not password:
            status_label.config(text="❌ Please enter a password", fg="red")
            password_entry.focus_set()
            return
        if password != confirm_password:
            status_label.config(text="❌ Passwords do not match", fg="red")
            confirm_entry.focus_set()
            return
        
        # Create full folder path
        full_path = os.path.join(folder_path, folder_name)
        
        # Check if folder already exists
        if os.path.exists(full_path):
            if not messagebox.askyesno("Folder Exists", 
                                     f"Folder '{full_path}' already exists.\n"
                                     "Do you want to use it as your secure folder?",
                                     parent=create_window):
                return
        
        status_label.config(text="Creating secure folder with multi-layer encryption...", fg="blue")
        create_window.update()
        
        success, message, folder_id = db.create_secure_folder(user_id, folder_name, full_path, password)
        
        if success:
            status_label.config(text="✅ Folder created successfully!", fg="green")
            result["folder_id"] = folder_id
            
            # Enhanced success message with detailed security info
            success_msg = f"Secure folder '{folder_name}' created successfully!\n\n"
            success_msg += f"📍 Location: {full_path}\n"
            success_msg += f"📁 Subdirectories: Images/ and PDFs/ created\n\n"
            success_msg += f"🔒 Security Applied:\n{message}"
            
            messagebox.showinfo("🛡️ Secure Folder Created", success_msg, parent=create_window)
            create_window.destroy()
        else:
            status_label.config(text=f"❌ {message}", fg="red")
    
    # Fixed buttons at bottom
    button_frame = tk.Frame(create_window, bg=get_bg_color())
    button_frame.pack(side="bottom", pady=10)
    
    tk.Button(button_frame, text="🛡️ Create Secure Folder", command=create_folder,
              bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Cancel", command=create_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
    
    # Focus on name entry
    create_window.after(100, lambda: name_entry.focus_set())
    
    create_window.wait_window()
    return result["folder_id"]


def secure_folder_now_dialog(user_id, parent=None):
    """Dialog to select and secure existing folders with 7-Zip encryption (placeholder)"""
    # This function will be properly implemented once we get your database functions
    messagebox.showinfo("Secure Folder Now", 
                       "This feature will be implemented once your database functions are ready.\n\n"
                       "It will allow direct creation of .7z encrypted archives.",
                       parent=parent)


def show_forgot_password_dialog(parent, folder_name):
    """Dialog for forgot password functionality"""
    messagebox.showinfo("Forgot Password", 
                       f"Forgot Password feature for folder '{folder_name}' is not yet implemented.\n\n"
                       "Please contact your system administrator or use a different folder.",
                       parent=parent)


def manage_folders_dialog(user_id, parent=None):
    """Dialog to manage existing secure folders with enhanced 7-Zip encryption status"""
    db = DatabaseManager()
    
    manage_window = tk.Toplevel(parent) if parent else tk.Toplevel()
    manage_window.title("🗂️ Manage Secure Folders")
    manage_window.geometry("750x550")  # Larger for enhanced encryption info
    manage_window.grab_set()
    manage_window.configure(bg=get_bg_color())
    
    # Center the window
    if parent:
        manage_window.transient(parent)
    manage_window.update_idletasks()
    width = manage_window.winfo_width()
    height = manage_window.winfo_height()
    x = (manage_window.winfo_screenwidth() // 2) - (width // 2)
    y = (manage_window.winfo_screenheight() // 2) - (height // 2)
    manage_window.geometry(f"{width}x{height}+{x}+{y}")
    
    tk.Label(manage_window, text="🗂️ Manage Secure Folders", 
             font=("Arial", 16, "bold"), bg=get_bg_color(), fg=get_highlight_color()).pack(pady=20)
    
    # Folders list
    folders_frame = tk.Frame(manage_window, bg=get_bg_color())
    folders_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    folders = db.get_user_secure_folders(user_id)
    
    if not folders:
        tk.Label(folders_frame, text="No secure folders found.\nClick 'Create New Folder' to get started.", 
                font=("Arial", 12), bg=get_bg_color(), fg=get_fg_color()).pack(expand=True)
    else:
        # Enhanced statistics for 7-Zip encryption
        encrypted_count = sum(1 for folder in folders if len(folder) > 5 and folder[5] and folder[6] == '7zip_aes256')
        hidden_count = sum(1 for folder in folders if len(folder) > 8 and folder[8])
        app_only_count = len(folders) - encrypted_count
        
        stats_text = f"You have {len(folders)} secure folders:"
        stats_detail = f"• {encrypted_count} with 7-Zip AES-256 encryption"
        stats_detail2 = f"• {hidden_count} hidden from File Explorer"
        stats_detail3 = f"• {app_only_count} with app-level security only"
        
        tk.Label(folders_frame, text=stats_text, 
                font=("Arial", 12, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(anchor="w", pady=(0,5))
        tk.Label(folders_frame, text=stats_detail, 
                font=("Arial", 10), bg=get_bg_color(), fg="green").pack(anchor="w", padx=20)
        tk.Label(folders_frame, text=stats_detail2, 
                font=("Arial", 10), bg=get_bg_color(), fg="blue").pack(anchor="w", padx=20)
        tk.Label(folders_frame, text=stats_detail3, 
                font=("Arial", 10), bg=get_bg_color(), fg="orange").pack(anchor="w", padx=20, pady=(0,10))
        
        # Create scrollable frame for folders
        canvas = tk.Canvas(folders_frame, bg=get_bg_color())
        scrollbar = tk.Scrollbar(folders_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=get_bg_color())
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for folder in folders:
            folder_frame = tk.Frame(scrollable_frame, bg=get_bg_color(), relief="ridge", bd=1)
            folder_frame.pack(fill="x", pady=5)
            
            # Enhanced folder header with 7-Zip encryption status
            header_frame = tk.Frame(folder_frame, bg=get_bg_color())
            header_frame.pack(fill="x", padx=10, pady=5)
            
            is_encrypted = len(folder) > 5 and folder[5]
            encryption_method = folder[6] if len(folder) > 6 else 'none'
            is_hidden = len(folder) > 8 and folder[8] if len(folder) > 8 else False
            
            # Enhanced encryption status display
            if is_encrypted and encryption_method == '7zip_aes256':
                encryption_icon = "🛡️"
                encryption_text = "7-Zip AES-256 Encrypted"
                encryption_color = "green"
            elif is_hidden:
                encryption_icon = "🫥"
                encryption_text = "Hidden + App Security"
                encryption_color = "blue"
            else:
                encryption_icon = "🔓"
                encryption_text = "App-level Security Only"
                encryption_color = "orange"
            
            tk.Label(header_frame, text=f"{encryption_icon} {folder[1]}", 
                    font=("Arial", 11, "bold"), bg=get_bg_color(), fg=get_fg_color()).pack(side="left")
            
            tk.Label(header_frame, text=encryption_text, 
                    font=("Arial", 9), bg=get_bg_color(), fg=encryption_color).pack(side="right")
            
            # Enhanced folder details
            tk.Label(folder_frame, text=f"📍 Location: {folder[2]}", 
                    font=("Arial", 9), bg=get_bg_color(), fg="gray").pack(anchor="w", padx=20)
            tk.Label(folder_frame, text=f"📅 Created: {folder[3][:16] if folder[3] else 'Unknown'}", 
                    font=("Arial", 9), bg=get_bg_color(), fg="gray").pack(anchor="w", padx=20)
            tk.Label(folder_frame, text=f"🕒 Last used: {folder[4][:16] if folder[4] else 'Never'}", 
                    font=("Arial", 9), bg=get_bg_color(), fg="gray").pack(anchor="w", padx=20)
            
            # Security details
            security_details = []
            if is_encrypted and encryption_method == '7zip_aes256':
                security_details.append("AES-256 encrypted")
            if is_hidden:
                security_details.append("Hidden folder")
            security_details.append("Password protected")
            
            tk.Label(folder_frame, text=f"🔒 Security: {', '.join(security_details)}", 
                    font=("Arial", 8), bg=get_bg_color(), fg="gray").pack(anchor="w", padx=20, pady=(0,5))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    # Buttons
    button_frame = tk.Frame(manage_window, bg=get_bg_color())
    button_frame.pack(pady=20)
    
    def create_new():
        folder_id = create_folder_dialog(manage_window, user_id)
        if folder_id:
            manage_window.destroy()
            manage_folders_dialog(user_id, parent)  # Refresh the dialog
    
    tk.Button(button_frame, text="➕ Create New Folder", command=create_new,
              bg="#4CAF50", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="❌ Close", command=manage_window.destroy,
              bg="#f44336", fg="white", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)


# Example usage and testing function
if __name__ == "__main__":
    # Test the dialogs (for development purposes)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Test with a dummy user_id
    test_user_id = 1
    
    # Test the main selection dialog
    result = secure_folder_selection_dialog(test_user_id, "image")
    print(f"Selection result: {result}")
    
    root.destroy()
